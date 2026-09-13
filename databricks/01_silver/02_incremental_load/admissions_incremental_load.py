"""
===============================================================================
                    Silver Layer - Admissions Incremental Load
===============================================================================

Script Purpose:
    This script incrementally loads admission data from the Bronze Layer into
    the Silver Delta table using a high-watermark approach.

    The script performs the following operations:
        1. Reads the last successful watermark for the admissions table.
        2. Reads only newly arrived Bronze database records.
        3. Cleans and standardizes admission attributes.
        4. Validates duplicate admission_id + updated_at records.
        5. Builds SCD Type 2 validity periods for incoming admission records.
        6. Closes existing current admission records when new versions arrive.
        7. Appends the incoming admission history to the Silver Delta table.
        8. Updates the watermark after a successful load.
        9. Records NO_DATA or FAILED status in the metadata table.

Design Principles:
    - Admission data is sourced only from the database.
    - Incremental processing is controlled by file modification time.
    - Admission history is maintained using SCD Type 2.
    - Each admission lifecycle update becomes a separate historical version.
    - The watermark is updated only after a successful Silver load.
    - Failed loads do not advance the watermark.
    - Execution status and errors are stored in the metadata table.

Usage Notes:
    - The Bronze database landing path must already contain Parquet files.
    - The Silver admissions Delta table must already exist.
    - The watermark table must contain an admissions record.
    - This script uses append plus MERGE to maintain admission history.

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

# Bronze source containing incremental admission records.
source_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/admissions/"

# Silver target containing SCD Type 2 admission history.
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/admissions/"

# Metadata table used to control incremental processing.
watermark_table = "healthone_lakehouse.metadata.watermark_bronze_silver"

# Logical table name used in the watermark table.
table_name = "admissions"


# =============================================================================
#                         Start Pipeline Run
# =============================================================================

# Capture the pipeline start time for this execution
current_run_timestamp = datetime.now()


try:

    # =========================================================================
    #                         Read Last Watermark
    # =========================================================================

    # Read the last successfully processed watermark for admissions
    watermark_result = spark.sql(f"""
        SELECT last_watermark
        FROM {watermark_table}
        WHERE table_name = '{table_name}'
    """).first()

    # Stop the pipeline if the metadata record does not exist
    if watermark_result is None:
        raise Exception(
            f"No watermark record found for table '{table_name}'. "
            f"Check the metadata table."
        )

    last_watermark = watermark_result["last_watermark"]


    # =========================================================================
    #                         Read Incremental Bronze Data
    # =========================================================================

    # Read only Bronze records whose files were modified after the last
    # successful watermark and before the current pipeline run started
    df_admissions_db = (
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

    # Count the records available in the current incremental batch
    source_record_count = df_admissions_db.count()


    if source_record_count == 0:

        # Record that no new admission data was available
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                status = 'NO_DATA',
                started_at =
                    CAST('{current_run_timestamp}' AS TIMESTAMP),
                completed_at = current_timestamp(),
                error_message = NULL
            WHERE table_name = '{table_name}'
        """)

    else:

        # =====================================================================
        #                         Clean Source Data
        # =====================================================================

        # Standardize admission fields and convert them to Silver data types
        df_admissions_db = (
            df_admissions_db
            .select(
                col("admission_id")
                    .cast("long")
                    .alias("admission_id"),

                col("patient_id")
                    .cast("long")
                    .alias("patient_id"),

                col("hospital_id")
                    .cast("long")
                    .alias("hospital_id"),

                to_timestamp(
                    col("admit_datetime"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("admit_datetime"),

                to_timestamp(
                    col("discharge_datetime"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("discharge_datetime"),

                lower(trim(col("ward")))
                    .alias("ward"),

                trim(col("bed_no"))
                    .alias("bed_no"),

                lower(trim(col("status")))
                    .alias("status"),

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

            # valid_to will be populated using the next version timestamp
            .withColumn(
                "valid_to",
                lit(None).cast("timestamp")
            )
        )


        # =====================================================================
        #                         Validate Duplicate Events
        # =====================================================================

        # Check whether one admission has multiple records with the same
        # updated_at timestamp
        df_duplicate_timestamp = (
            df_admissions_db
            .groupBy("admission_id", "updated_at")
            .count()
            .filter(col("count") > 1)
        )

        duplicate_count = df_duplicate_timestamp.count()

        # Stop processing when the correct record cannot be determined
        if duplicate_count > 0:
            raise Exception(
                f"Duplicate admission_id + updated_at records found "
                f"for '{table_name}'. "
                f"Review the source data before continuing."
            )


        # =====================================================================
        #                         Build SCD Type 2 History
        # =====================================================================

        # Order each admission's versions chronologically
        window_spec = (
            Window
            .partitionBy("admission_id")
            .orderBy("updated_at")
        )

        # Use the next update timestamp as the current version's valid_to
        df_admissions_scd = (
            df_admissions_db
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

        # Keep the Silver admission columns in a consistent order
        df_admissions_scd = (
            df_admissions_scd
            .select(
                "admission_id",
                "patient_id",
                "hospital_id",
                "admit_datetime",
                "discharge_datetime",
                "ward",
                "bed_no",
                "status",
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

        # Find the first incoming version for each admission.
        # This timestamp is used to close the existing current version.
        df_admissions_scd_first_version = (
            df_admissions_scd
            .groupBy("admission_id")
            .agg(
                min("valid_from").alias("first_db_valid_from")
            )
        )


        # =====================================================================
        #                         Get Delta Target
        # =====================================================================

        # Create a DeltaTable object for the Silver admissions table
        delta_target = DeltaTable.forPath(
            spark,
            target_path
        )


        # =====================================================================
        #                         Close Existing Versions
        # =====================================================================

        # Close the existing current version for affected admissions
        (
            delta_target.alias("tgt")
            .merge(
                df_admissions_scd_first_version.alias("src"),
                """
                tgt.admission_id = src.admission_id
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
        #                         Append New Admission History
        # =====================================================================

        # Append all incoming admission versions to the Silver Delta table
        (
            df_admissions_scd
            .write
            .format("delta")
            .mode("append")
            .save(target_path)
        )


        # =====================================================================
        #                         Record Load Result
        # =====================================================================

        # Count the number of admission records written to Silver
        row_count = df_admissions_scd.count()


        # =====================================================================
        #                         Update Watermark
        # =====================================================================

        # Advance the watermark only after the Silver load succeeds
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

    # Capture the error message for metadata logging
    error_message = str(e)

    try:

        # Record the failure details in the metadata table
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

    except Exception:

        # Preserve the original pipeline error if metadata logging fails
        traceback.print_exc()


    # Re-raise the original exception so the Databricks job is marked FAILED
    raise