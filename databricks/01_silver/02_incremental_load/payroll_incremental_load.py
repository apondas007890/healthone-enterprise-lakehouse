"""
===============================================================================
                Silver Layer - Payroll Incremental Processing
===============================================================================

Script Purpose:
    Reads newly arrived payroll data from the Bronze CSV/Parquet files,
    cleans and standardizes the records, validates the incoming data, and
    loads the changes into the Silver Delta table using SCD Type 2 logic.

Processing Steps:
    1. Read the last successful watermark for the payroll table.
    2. Read newly arrived Bronze payroll records.
    3. Filter records using the Bronze file modification timestamp.
    4. Clean and standardize payroll columns.
    5. Calculate net_pay from gross_pay minus deductions.
    6. Validate duplicate payroll records.
    7. Prepare SCD Type 2 metadata.
    8. Close existing current records when a new version arrives.
    9. Append the new payroll history records to Silver.
    10. Update the watermark after successful processing.
    11. Record failures in the watermark metadata table.

Important Notes:
    - Bronze data remains unchanged.
    - This script assumes Bronze data is stored in Parquet format.
    - The Bronze files must contain Spark file metadata.
    - payroll_id is treated as the business key.
    - updated_at is used to identify record versions.
    - The script uses SCD Type 2 history tracking.
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
source_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/payroll/"


# Silver Delta target location.
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/payroll/"


# Metadata table used to store watermark and pipeline status.
watermark_table = "healthone_lakehouse.metadata.watermark_bronze_silver"

# Logical table name used in the watermark table.
table_name = "payroll"

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

    # Read Bronze Parquet files.
    #
    # _metadata.file_modification_time identifies when each source file
    # was modified in the storage layer.
    df_bronze = spark.read.parquet(source_path)

    # Select only files that arrived after the previous watermark and
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

        print("No new payroll records found.")

        # Advance the watermark even when no new data is available.
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

        # Select payroll columns and apply explicit data-type conversions.
        #
        # - ID columns are converted to BIGINT.
        # - Monetary values are converted to DECIMAL.
        # - net_pay is calculated from gross_pay minus deductions.
        # - paid_date is converted to DATE.
        # - created_at and updated_at are converted to TIMESTAMP.
        df_payroll_incremental = (
            df_incremental
            .select(
                col("payroll_id")
                    .cast("long")
                    .alias("payroll_id"),

                col("employee_id")
                    .cast("long")
                    .alias("employee_id"),

                trim(col("pay_period"))
                    .cast("string")
                    .alias("pay_period"),

                col("gross_pay")
                    .cast("decimal(10,2)")
                    .alias("gross_pay"),

                col("deductions")
                    .cast("decimal(10,2)")
                    .alias("deductions"),

                (
                    col("gross_pay").cast("decimal(10,2)")
                    - col("deductions").cast("decimal(10,2)")
                )
                .cast("decimal(10,2)")
                .alias("net_pay"),

                to_date(
                    col("paid_date"),
                    "yyyy-MM-dd"
                ).alias("paid_date"),

                to_timestamp(
                    col("created_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("created_at"),

                to_timestamp(
                    col("updated_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("updated_at")
            )

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

            # Initially, each incoming record is considered current.
            .withColumn(
                "valid_to",
                lit(None).cast("timestamp")
            )

            .withColumn(
                "is_current",
                lit(1).cast("int")
            )

            # Record when the record was loaded into Silver.
            .withColumn(
                "insertion_time",
                current_timestamp()
            )
        )


        # =====================================================================
        #                         Validate Incoming Data
        # =====================================================================

        # Check whether the same payroll_id has multiple records with the
        # same updated_at value in the incoming batch.
        #
        # Multiple records with the same business key and timestamp create
        # ambiguity in SCD Type 2 processing.
        duplicate_df = (
            df_payroll_incremental
            .groupBy("payroll_id", "updated_at")
            .count()
            .filter(col("count") > 1)
        )

        duplicate_count = duplicate_df.count()

        if duplicate_count > 0:
            raise ValueError(
                "Duplicate payroll records detected for the same "
                "payroll_id and updated_at."
            )


        # =====================================================================
        #                         Prepare SCD Type 2 Records
        # =====================================================================

        # Order each payroll record by updated_at within its business key.
        scd_window = (
            Window
            .partitionBy("payroll_id")
            .orderBy(col("updated_at"))
        )

        # The next version's timestamp becomes the current version's
        # valid_to value.
        df_payroll_scd = (
            df_payroll_incremental
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
                .otherwise(lit(0))
                .cast("int")
            )
        )


        # =====================================================================
        #                         Define Final Column Order
        # =====================================================================

        df_payroll_scd = df_payroll_scd.select(
            "payroll_id",
            "employee_id",
            "pay_period",
            "gross_pay",
            "deductions",
            "net_pay",
            "paid_date",
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

        # For each payroll_id, find the earliest incoming version.
        #
        # This timestamp is used to close the existing current Silver record.
        first_version_df = (
            df_payroll_scd
            .groupBy("payroll_id")
            .agg(
                min("valid_from").alias("first_file_valid_from")
            )
        )


        # =====================================================================
        #                         Load Existing Silver Delta Table
        # =====================================================================

        delta_table = DeltaTable.forPath(
            spark,
            target_path
        )


        # =====================================================================
        #                         Close Existing Current Records
        # =====================================================================

        # Close the currently active version of each payroll record when
        # a newer version arrives.
        #
        # Existing current record:
        #     is_current = 1
        #     valid_to = NULL
        #
        # After a new version arrives:
        #     is_current = 0
        #     valid_to = first incoming valid_from timestamp
        (
            delta_table.alias("target")
            .merge(
                first_version_df.alias("source"),
                """
                target.payroll_id = source.payroll_id
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
        # =====================================================================

        # Append the incoming records to the Silver Delta table.
        #
        # Existing history is preserved, while the new versions are added.
        (
            df_payroll_scd
            .write
            .format("delta")
            .mode("append")
            .save(target_path)
        )


        # =====================================================================
        #                         Update Watermark
        # =====================================================================

        # Update the watermark only after the Silver load succeeds.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                last_watermark = TIMESTAMP('{current_run_timestamp}'),
                status = 'SUCCESS',
                updated_at = current_timestamp()
            WHERE table_name = '{table_name}'
        """)

        print("Payroll incremental load completed successfully.")


# =============================================================================
#                         Error Handling
# =============================================================================

except Exception as error:

    error_message = str(error).replace("'", "''")

    print("Payroll incremental load failed.")
    print(error_message)

    # Record the failure in the metadata table.
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

    # Re-raise the original exception so the orchestration tool can detect
    # the pipeline failure.
    raise