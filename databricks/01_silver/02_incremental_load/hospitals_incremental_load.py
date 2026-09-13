"""
===============================================================================
                    Silver Layer - Hospitals Incremental Load
===============================================================================

Script Purpose:
    This script incrementally loads hospital data from the Bronze Layer into
    the Silver Delta table using a high-watermark approach.

    The script performs the following operations:
        1. Reads the last successful watermark from the metadata table.
        2. Reads only Bronze files modified after that watermark.
        3. Cleans and standardizes the hospital data.
        4. Validates duplicate hospital_id + updated_at records.
        5. Builds SCD Type 2 validity periods for incoming records.
        6. Closes the existing current version for affected hospitals.
        7. Appends the new hospital history to the Silver Delta table.
        8. Updates the watermark after a successful load.
        9. Records NO_DATA or FAILED status in the metadata table.

Design Principles:
    - Bronze files are processed incrementally using file modification time.
    - The watermark is advanced only after a successful Silver load.
    - Failed loads do not advance the watermark so the data can be retried.
    - Hospital history is maintained using SCD Type 2.
    - Existing current records are closed before new versions are inserted.
    - Duplicate hospital_id + updated_at records are rejected.
    - Execution status and errors are recorded in the metadata table.

Usage Notes:
    - This script is designed for scheduled Databricks pipeline execution.
    - The target Delta table must already exist.
    - The watermark table must contain a record for the hospitals table.
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
    col,
    lit,
    trim,
    lower,
    to_date,
    to_timestamp,
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

# Bronze source location
source_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/hospitals/"

# Silver target location
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/hospitals/"

# Metadata table used to control incremental processing
watermark_table = "healthone_lakehouse.metadata.watermark_bronze_silver"

# Metadata record for the table being processed
table_name = "hospitals"


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

    # Read only Bronze records whose source files arrived after the
    # previously successful watermark and before this pipeline run started.
    df_hr_hospitals_db = (
        spark.read
        .parquet(source_path)
        .filter(
            (col("_metadata.file_modification_time") > lit(last_watermark)) &
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
    source_file_count = df_hr_hospitals_db.count()


    if source_file_count == 0:

        # Record that the pipeline completed without new source data.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                last_watermark = CAST('{current_run_timestamp}' AS TIMESTAMP),
                rows_loaded = 0,
                status = 'NO_DATA',
                started_at = CAST('{current_run_timestamp}' AS TIMESTAMP),
                completed_at = current_timestamp(),
                error_message = NULL
            WHERE table_name = '{table_name}'
        """)

    else:

        # =====================================================================
        #                         Clean Source Data
        # =====================================================================

        # Standardize columns and convert them to the required Silver types.
        df_hr_hospitals_db = (
            df_hr_hospitals_db
            .select(
                col("hospital_id")
                    .cast("long")
                    .alias("hospital_id"),

                lower(trim(col("name")))
                    .alias("name"),

                lower(trim(col("address")))
                    .alias("address"),

                lower(trim(col("city")))
                    .alias("city"),

                lower(trim(col("region")))
                    .alias("region"),

                col("capacity")
                    .cast("int")
                    .alias("capacity"),

                to_date(
                    col("opened_date"),
                    "yyyy-MM-dd"
                ).alias("opened_date"),

                to_timestamp(
                    col("created_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("created_at"),

                to_timestamp(
                    col("updated_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("updated_at")
            )

            # Identify the source system
            .withColumn("source", lit("db"))

            # Set the beginning of the SCD Type 2 validity period
            .withColumn("valid_from", col("updated_at"))

            # valid_to will be populated after the next version is created
            .withColumn(
                "valid_to",
                lit(None).cast("timestamp")
            )
            .withColumn("insertion_time", current_timestamp()) # Store the time when the record is inserted into the Silver Layer
        )


        # =====================================================================
        #                         Validate Duplicate Events
        # =====================================================================

        # Check whether the same hospital has multiple records with the
        # same updated_at timestamp.
        df_duplicate_timestamp = (
            df_hr_hospitals_db
            .groupBy("hospital_id", "updated_at")
            .count()
            .filter(col("count") > 1)
        )

        duplicate_count = df_duplicate_timestamp.count()

        # Stop processing because the correct record cannot be determined.
        if duplicate_count > 0:

            raise Exception(
                f"Duplicate hospital_id + updated_at records found "
                f"for '{table_name}'. "
                f"Review the source data before continuing."
            )


        # =====================================================================
        #                         Build SCD Type 2 History
        # =====================================================================

        # Order each hospital's versions chronologically.
        window_spec = (
            Window
            .partitionBy("hospital_id")
            .orderBy("updated_at")
        )

        # Use the next update timestamp as the current version's valid_to.
        df_hr_hospitals_scd = (
            df_hr_hospitals_db
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
        df_hr_hospitals_scd = (
            df_hr_hospitals_scd
            .select(
                "hospital_id",
                "name",
                "address",
                "city",
                "region",
                "capacity",
                "opened_date",
                "created_at",
                "updated_at",
                "source",
                "valid_from",
                "valid_to",
                "is_current"
            )
        )


        # =====================================================================
        #                         Find First DB Version
        # =====================================================================

        # Find the first incoming version for each hospital.
        # This timestamp is used to close the existing file/current version.
        df_hr_hospitals_scd_first_version = (
            df_hr_hospitals_scd
            .groupBy("hospital_id")
            .agg(
                min("valid_from").alias("first_db_valid_from")
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

        # Close the existing current version when a newer DB version arrives.
        (
            delta_target.alias("tgt")
            .merge(
                df_hr_hospitals_scd_first_version.alias("src"),
                """
                tgt.hospital_id = src.hospital_id
                AND tgt.is_current = 1
                """
            )
            .whenMatchedUpdate(
                set={
                    "valid_to": "src.first_db_valid_from",
                    "is_current": "0"
                }
            )
            .execute()
        )


        # =====================================================================
        #                         Append New History
        # =====================================================================

        # Append all incoming DB versions to the Silver Delta table.
        (
            df_hr_hospitals_scd
            .write
            .format("delta")
            .mode("append")
            .save(target_path)
        )


        # =====================================================================
        #                         Record Load Result
        # =====================================================================

        # Count the number of SCD Type 2 records successfully written.
        row_count = df_hr_hospitals_scd.count()


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