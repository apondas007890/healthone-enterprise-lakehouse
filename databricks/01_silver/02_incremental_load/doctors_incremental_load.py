"""
===============================================================================
                    Silver Layer - Doctors Incremental Processing
===============================================================================

Script Purpose:
    Reads newly arrived doctor records from the Bronze Layer, cleans and
    standardizes the data, validates incoming records, and loads the data into
    the Silver Delta table using SCD Type 2 logic.

Processing Steps:
    1. Read the last successful watermark for the doctors table.
    2. Read newly arrived Bronze doctor records.
    3. Filter records using the Bronze file modification timestamp.
    4. Clean and standardize doctor attributes.
    5. Cast ID and timestamp columns to the required data types.
    6. Validate duplicate doctor records.
    7. Prepare SCD Type 2 metadata.
    8. Close existing current doctor records.
    9. Append new doctor versions to Silver.
    10. Update the watermark after successful processing.
    11. Record failures in the metadata table.

Important Notes:
    - Bronze data remains unchanged.
    - This script assumes Bronze doctor data is stored as Parquet.
    - doctor_id is treated as the business key.
    - updated_at identifies a new version of a doctor record.
    - Silver history is maintained using SCD Type 2 logic.
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
    current_timestamp,
    lead,
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
source_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/doctors/"


# Silver Delta target location.
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/doctors/"


# Metadata table containing watermark and pipeline execution information.
watermark_table = "healthone_lakehouse.metadata.watermark_bronze_silver"

# Logical table name used in the watermark metadata table.
table_name = "doctors"

# Timestamp for the current pipeline execution.
current_run_timestamp = datetime.now()


# =============================================================================
#                         Incremental Processing
# =============================================================================

try:

    # =========================================================================
    #                         Read Last Watermark
    # =========================================================================

    # Read the last successfully processed Bronze file modification timestamp.
    watermark_df = (
        spark.table(watermark_table)
        .filter(col("table_name") == table_name)
        .select("last_watermark")
    )

    watermark_row = watermark_df.first()

    if watermark_row is None or watermark_row["last_watermark"] is None:
        raise ValueError(
            f"No valid watermark found for table: {table_name}"
        )

    last_watermark = watermark_row["last_watermark"]

    print(f"Last watermark: {last_watermark}")
    print(f"Current run timestamp: {current_run_timestamp}")


    # =========================================================================
    #                         Read Incremental Bronze Data
    # =========================================================================

    # Read Bronze Parquet data.
    df_bronze = spark.read.parquet(source_path)

    # Select records from files modified after the previous watermark and
    # before or at the current pipeline execution timestamp.
    df_incremental = (
        df_bronze
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

    incremental_count = df_incremental.count()

    if incremental_count == 0:

        print("No new doctor records found.")

        # Advance the watermark when no new records are available.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                last_watermark = TIMESTAMP('{current_run_timestamp}'),
                status = 'NO_DATA',
                updated_at = current_timestamp()
            WHERE table_name = '{table_name}'
        """)

    else:

        print(f"Incremental Bronze records found: {incremental_count}")


        # =====================================================================
        #                         Clean and Standardize Data
        # =====================================================================

        # Select the required doctor columns and apply data-type conversions.
        #
        # - ID columns are converted to BIGINT.
        # - specialization is trimmed and converted to lowercase.
        # - created_at and updated_at are converted to TIMESTAMP.
        df_doctors_incremental = (
            df_incremental
            .select(
                col("doctor_id")
                    .cast("long")
                    .alias("doctor_id"),

                # Standardize specialization values.
                # Example: " Orthopedics " -> "orthopedics"
                lower(
                    trim(col("specialization"))
                ).alias("specialization"),

                col("employee_id")
                    .cast("long")
                    .alias("employee_id"),

                col("hospital_id")
                    .cast("long")
                    .alias("hospital_id"),

                # Convert source timestamps to Spark TIMESTAMP.
                to_timestamp(
                    col("created_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("created_at"),

                to_timestamp(
                    col("updated_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("updated_at")
            )

            # -----------------------------------------------------------------
            # SCD Type 2 Metadata
            # -----------------------------------------------------------------

            # Identify the original source of the record.
            .withColumn(
                "source",
                lit("file")
            )

            # Set the beginning of the record's validity period.
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
        #                         Validate Incoming Data
        # =====================================================================

        # Check for duplicate doctor versions within the incoming batch.
        #
        # The same doctor_id and updated_at combination must not appear
        # more than once.
        duplicate_df = (
            df_doctors_incremental
            .groupBy("doctor_id", "updated_at")
            .count()
            .filter(col("count") > 1)
        )

        duplicate_count = duplicate_df.count()

        if duplicate_count > 0:
            raise ValueError(
                "Duplicate doctor records detected for the same "
                "doctor_id and updated_at."
            )


        # =====================================================================
        #                         Prepare SCD Type 2 Records
        # =====================================================================

        # Order doctor versions by updated_at for each doctor.
        scd_window = (
            Window
            .partitionBy("doctor_id")
            .orderBy(col("updated_at"))
        )

        # The next version's updated_at becomes the current version's
        # valid_to value.
        df_doctors_scd = (
            df_doctors_incremental
            .withColumn(
                "valid_to",
                lead("updated_at").over(scd_window)
            )
            .withColumn(
                "is_current",
                when(
                    col("valid_to").isNull(),
                    lit(1)
                )
                .otherwise(
                    lit(0)
                )
                .cast("int")
            )
        )


        # =====================================================================
        #                         Define Final Column Order
        # =====================================================================

        df_doctors_scd = df_doctors_scd.select(
            "doctor_id",
            "specialization",
            "employee_id",
            "hospital_id",
            "created_at",
            "updated_at",
            "source",
            "valid_from",
            "valid_to",
            "is_current",
            "insertion_time"
        )


        # =====================================================================
        #                         Find First Incoming Version
        # =====================================================================

        # Find the earliest incoming version for each doctor.
        #
        # This timestamp is used to close the existing current Silver record.
        first_version_df = (
            df_doctors_scd
            .groupBy("doctor_id")
            .agg(
                min("valid_from").alias("first_file_valid_from")
            )
        )


        # =====================================================================
        #                         Load Existing Silver Delta Table
        # =========================================================================

        delta_table = DeltaTable.forPath(
            spark,
            target_path
        )


        # =====================================================================
        #                         Close Existing Current Records
        # =====================================================================

        # Close the currently active doctor record when a newer version
        # arrives for the same doctor_id.
        (
            delta_table.alias("target")
            .merge(
                first_version_df.alias("source"),
                """
                target.doctor_id = source.doctor_id
                AND target.is_current = 1
                """
            )
            .whenMatchedUpdate(
                set={
                    "valid_to": "source.first_file_valid_from",
                    "is_current": "0"
                }
            )
            .execute()
        )


        # =====================================================================
        #                         Append New SCD Type 2 Records
        # =========================================================================

        # Append new doctor versions while preserving existing history.
        (
            df_doctors_scd
            .write
            .format("delta")
            .mode("append")
            .save(target_path)
        )


        # =====================================================================
        #                         Update Watermark
        # =========================================================================

        # Update the watermark only after the Silver load succeeds.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                last_watermark = TIMESTAMP('{current_run_timestamp}'),
                status = 'SUCCESS',
                updated_at = current_timestamp()
            WHERE table_name = '{table_name}'
        """)

        print("Doctors incremental load completed successfully.")


# =============================================================================
#                         Error Handling
# =============================================================================

except Exception as error:

    error_message = str(error).replace("'", "''")

    print("Doctors incremental load failed.")
    print(error_message)

    # Record the failure in the watermark metadata table.
    try:

        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                status = 'FAILED',
                error_message = '{error_message}',
                updated_at = current_timestamp()
            WHERE table_name = '{table_name}'
        """)

    except Exception as metadata_error:

        print(
            "Failed to update the watermark metadata table: "
            f"{metadata_error}"
        )

    traceback.print_exc()

    # Re-raise the exception so ADF or Databricks Workflows can detect failure.
    raise