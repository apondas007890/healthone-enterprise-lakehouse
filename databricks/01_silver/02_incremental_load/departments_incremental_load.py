"""
===============================================================================
                    Silver Layer - Departments Incremental Load
===============================================================================

Script Purpose:
    This script incrementally loads department data from the Bronze Layer into
    the Silver Delta table using a high-watermark approach.

    The script reads department records from Bronze JSON files, cleans and
    standardizes the data, maintains historical department versions using
    SCD Type 2, and records pipeline execution details in the metadata table.

Processing Steps:
    1. Read the last successful watermark from the metadata table.
    2. Read only Bronze files modified after the previous watermark.
    3. Explode the departments array into individual department records.
    4. Clean and standardize department columns.
    5. Validate duplicate department_id + updated_at records.
    6. Build SCD Type 2 validity periods for incoming records.
    7. Close existing current department versions.
    8. Append new department history to the Silver Delta table.
    9. Update the watermark after a successful load.
   10. Record NO_DATA or FAILED status in the metadata table.

Design Principles:
    - Bronze files are processed incrementally using file modification time.
    - The watermark advances only after a successful Silver load.
    - Failed loads do not advance the watermark and can be retried.
    - Department history is maintained using SCD Type 2.
    - Existing current records are closed before new versions are inserted.
    - Duplicate department_id + updated_at records are rejected.
    - Execution status and errors are recorded in the metadata table.

Usage Notes:
    - This script is designed for scheduled Databricks pipeline execution.
    - The target Silver Delta table must already exist.
    - The watermark table must contain a record for the departments table.
    - Bronze data must be available in Parquet format at the configured source
      location.
    - A failure after the Delta append but before the watermark update can
      cause the same Bronze data to be processed again. Production pipelines
      should therefore use an idempotent MERGE or batch/run identifier when
      exactly-once processing is required.
===============================================================================
"""


# =============================================================================
#                         Import Required Functions
# =============================================================================

from pyspark.sql.functions import (
    explode,
    col,
    lit,
    trim,
    lower,
    to_timestamp,
    current_timestamp,
    lead,
    when,
    min
)

from pyspark.sql.window import Window

from delta.tables import DeltaTable

from datetime import datetime

import traceback


# =============================================================================
#                         Configuration
# =============================================================================

# Bronze source location.
# This location is assumed to contain department data in Parquet format.
source_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/departments/"

# Silver target location.
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/departments/"

# Metadata table used to control incremental processing.
watermark_table = "healthone_lakehouse.metadata.watermark_bronze_silver"

# Metadata record for the table being processed.
table_name = "departments"


# =============================================================================
#                         Start Pipeline Run
# =============================================================================

# Capture the pipeline start time for this execution.
current_run_timestamp = datetime.now()


try:

    # =========================================================================
    #                         Read Last Watermark
    # =========================================================================

    # Read the last successfully processed watermark for this table.
    watermark_result = spark.sql(f"""
        SELECT last_watermark
        FROM {watermark_table}
        WHERE table_name = '{table_name}'
    """).first()

    # Stop the pipeline if the required metadata record does not exist.
    if watermark_result is None:
        raise Exception(
            f"No watermark record found for table '{table_name}'. "
            f"Check the metadata table."
        )

    last_watermark = watermark_result["last_watermark"]


    # =========================================================================
    #                         Read Incremental Bronze Data
    # =========================================================================

    # Read only Bronze files that arrived after the previous successful
    # watermark and before this pipeline run started.
    df_bronze_departments = (
        spark.read
        .parquet(source_path)
        .filter(
            (col("_metadata.file_modification_time") > lit(last_watermark))
            &
            (
                col("_metadata.file_modification_time")
                <= lit(current_run_timestamp)
            )
        )
    )


    # =========================================================================
    #                         Check for New Data
    # =========================================================================

    # Count the records available in the current incremental batch.
    source_file_count = df_bronze_departments.count()


    if source_file_count == 0:

        # ---------------------------------------------------------------------
        # No New Data
        # ---------------------------------------------------------------------

        # Record that the pipeline completed without new source data.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                last_watermark =
                    CAST('{current_run_timestamp}' AS TIMESTAMP),
                rows_loaded = 0,
                status = 'NO_DATA',
                started_at =
                    CAST('{current_run_timestamp}' AS TIMESTAMP),
                completed_at = current_timestamp(),
                error_message = NULL
            WHERE table_name = '{table_name}'
        """)

    else:

        # =====================================================================
        #                         Extract Department Records
        # =====================================================================

        # Explode the departments array so each department becomes one row.
        # The nested department object is then expanded into individual
        # department columns.
        df_departments_file = (
            df_bronze_departments
            .select(
                explode(col("departments")).alias("department")
            )
            .select("department.*")
        )


        # =====================================================================
        #                         Clean and Standardize Data
        # =====================================================================

        # Select the required department columns and apply data-quality
        # transformations.
        #
        # - department_id and hospital_id are converted to BIGINT.
        # - name is trimmed and converted to lowercase.
        # - created_at and updated_at are converted to TIMESTAMP.
        df_departments_file = (
            df_departments_file
            .select(
                col("department_id")
                    .cast("long")
                    .alias("department_id"),

                lower(trim(col("name")))
                    .alias("name"),

                col("hospital_id")
                    .cast("long")
                    .alias("hospital_id"),

                to_timestamp(
                    col("created_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("created_at"),

                to_timestamp(
                    col("updated_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("updated_at")
            )

            # Identify the original source system.
            .withColumn(
                "source",
                lit("file")
            )

            # Set the beginning of the SCD Type 2 validity period.
            .withColumn(
                "valid_from",
                col("updated_at")
            )

            # NULL indicates that the record is currently active.
            .withColumn(
                "valid_to",
                lit(None).cast("timestamp")
            )

            # Mark the record as the current version.
            .withColumn(
                "is_current",
                lit(1).cast("int")
            )

            # Record when the data was loaded into the Silver layer.
            .withColumn(
                "insertion_time",
                current_timestamp()
            )
        )


        # =====================================================================
        #                         Validate Duplicate Events
        # =====================================================================

        # Check whether the same department has multiple records with the
        # same updated_at timestamp in the current incremental batch.
        df_duplicate_timestamp = (
            df_departments_file
            .groupBy(
                "department_id",
                "updated_at"
            )
            .count()
            .filter(col("count") > 1)
        )

        duplicate_count = df_duplicate_timestamp.count()


        # Stop processing because the correct version cannot be determined.
        if duplicate_count > 0:
            raise Exception(
                f"Duplicate department_id + updated_at records found "
                f"for '{table_name}'. "
                f"Review the source data before continuing."
            )


        # =====================================================================
        #                         Build SCD Type 2 History
        # =====================================================================

        # Order each department's incoming versions chronologically.
        window_spec = (
            Window
            .partitionBy("department_id")
            .orderBy("updated_at")
        )


        # Use the next update timestamp as the current version's valid_to.
        #
        # The last incoming version for each department remains active
        # because its next update timestamp is NULL.
        df_departments_scd = (
            df_departments_file
            .withColumn(
                "valid_to",
                lead("updated_at").over(window_spec)
            )
            .withColumn(
                "is_current",
                when(col("valid_to").isNull(), 1)
                .otherwise(0)
                .cast("int")
            )
        )


        # =====================================================================
        #                         Select Target Columns
        # =====================================================================

        # Keep the Silver table columns in a consistent order.
        df_departments_scd = (
            df_departments_scd
            .select(
                "department_id",
                "name",
                "hospital_id",
                "created_at",
                "updated_at",
                "source",
                "valid_from",
                "valid_to",
                "is_current",
                "insertion_time"
            )
        )


        # =====================================================================
        #                         Find First Incoming Version
        # =====================================================================

        # Find the earliest incoming version for each department.
        # This timestamp is used to close the existing current version.
        df_departments_first_version = (
            df_departments_scd
            .groupBy("department_id")
            .agg(
                min("valid_from").alias("first_file_valid_from")
            )
        )


        # =====================================================================
        #                         Get Delta Target
        # =====================================================================

        # Create a DeltaTable object for the Silver target.
        delta_target = DeltaTable.forPath(
            spark,
            target_path
        )


        # =====================================================================
        #                         Close Existing Versions
        # =====================================================================

        # Close the existing current version when a newer department version
        # arrives from the Bronze file.
        (
            delta_target.alias("tgt")
            .merge(
                df_departments_first_version.alias("src"),
                """
                tgt.department_id = src.department_id
                AND tgt.is_current = 1
                """
            )
            .whenMatchedUpdate(
                set={
                    "valid_to": "src.first_file_valid_from",
                    "is_current": "0"
                }
            )
            .execute()
        )


        # =====================================================================
        #                         Append New History
        # =====================================================================

        # Append all incoming department versions to the Silver Delta table.
        (
            df_departments_scd
            .write
            .format("delta")
            .mode("append")
            .save(target_path)
        )


        # =====================================================================
        #                         Record Load Result
        # =====================================================================

        # Count the number of SCD Type 2 records written in this batch.
        row_count = df_departments_scd.count()


        # =====================================================================
        #                         Update Watermark
        # =====================================================================

        # Advance the watermark only after the Silver load succeeds.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                last_watermark =
                    CAST('{current_run_timestamp}' AS TIMESTAMP),
                rows_loaded = {row_count},
                status = 'SUCCESS',
                started_at =
                    CAST('{current_run_timestamp}' AS TIMESTAMP),
                completed_at = current_timestamp(),
                error_message = NULL
            WHERE table_name = '{table_name}'
        """)


except Exception as e:

    # =========================================================================
    #                         Handle Pipeline Failure
    # =========================================================================

    # Capture the error so it can be stored in the metadata table.
    error_message = str(e)


    # Do not advance the watermark when processing fails.
    # The same Bronze data can therefore be retried on the next run.
    try:

        # Record the failure details in the metadata table.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                status = 'FAILED',
                started_at =
                    CAST('{current_run_timestamp}' AS TIMESTAMP),
                completed_at = current_timestamp(),
                error_message =
                    '{error_message.replace("'", "''")}'
            WHERE table_name = '{table_name}'
        """)

    except Exception as metadata_error:

        # Preserve the metadata error for the Databricks execution log.
        traceback.print_exc()


    # Re-raise the original exception so the Databricks job is marked FAILED.
    raise