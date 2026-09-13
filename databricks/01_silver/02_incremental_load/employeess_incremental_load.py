"""
===============================================================================
              Silver Layer - Employees Incremental Processing
===============================================================================

Script Purpose:
    Reads newly arrived employee records from the Bronze Layer, cleans and
    standardizes the data, applies data-quality validations, and loads the
    records into the Silver Delta table using SCD Type 2 logic.

Processing Steps:
    1. Read the last successful watermark for the employees table.
    2. Read newly arrived Bronze employee data.
    3. Filter records using the Bronze file modification timestamp.
    4. Clean and standardize employee attributes.
    5. Standardize gender values.
    6. Clean and validate phone numbers.
    7. Clean and validate email addresses.
    8. Cast IDs, dates, salary, and timestamp columns.
    9. Validate duplicate employee records.
    10. Prepare SCD Type 2 history columns.
    11. Close existing current employee records.
    12. Append new employee versions to Silver.
    13. Update the watermark after successful processing.
    14. Record failures in the metadata table.

Important Notes:
    - Bronze data remains unchanged.
    - This script assumes Bronze employee data is stored as Parquet.
    - employee_id is treated as the business key.
    - updated_at identifies a new employee version.
    - Invalid phone numbers and email addresses are stored as "n/a".
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
    when,
    length,
    to_date,
    to_timestamp,
    current_timestamp,
    concat,
    substring,
    concat_ws,
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
source_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/employees/"

# Silver Delta target location.
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/employees/"

# Metadata table containing watermark and pipeline execution information.
watermark_table = "healthone_lakehouse.metadata.watermark_bronze_silver"

# Logical table name used in the watermark metadata table.
table_name = "employees"

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

        print("No new employee records found.")

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

        # Convert source columns to their required Silver data types and
        # apply the same cleaning rules used in the full-refresh process.
        df_employees_incremental = (
            df_incremental
            .select(
                col("employee_id")
                    .cast("long")
                    .alias("employee_id"),

                # Combine first_name and last_name into one standardized name.
                concat_ws(
                    " ",
                    lower(trim(col("first_name"))),
                    lower(trim(col("last_name")))
                ).alias("name"),

                # Convert date of birth into DATE.
                to_date(
                    col("dob"),
                    "yyyy-MM-dd"
                ).alias("dob"),

                # Standardize gender values to m, f, or n/a.
                when(
                    lower(substring(trim(col("gender")), 1, 1)) == "m",
                    lit("m")
                )
                .when(
                    lower(substring(trim(col("gender")), 1, 1)) == "f",
                    lit("f")
                )
                .otherwise(
                    lit("n/a")
                )
                .alias("gender"),

                # Standardize text attributes.
                lower(trim(col("address"))).alias("address"),
                lower(trim(col("role"))).alias("role"),

                # Convert foreign keys to INTEGER.
                col("department_id")
                    .cast("int")
                    .alias("department_id"),

                # Convert hire date into DATE.
                to_date(
                    col("hire_date"),
                    "yyyy-MM-dd"
                ).alias("hire_date"),

                # Convert salary into DECIMAL.
                col("salary")
                    .cast("decimal(10,2)")
                    .alias("salary"),

                # Standardize employee status.
                lower(trim(col("status"))).alias("status"),

                # Convert hospital ID to INTEGER.
                col("hospital_id")
                    .cast("int")
                    .alias("hospital_id"),

                # Convert audit timestamps.
                to_timestamp(
                    col("created_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("created_at"),

                to_timestamp(
                    col("updated_at"),
                    "yyyy-MM-dd HH:mm:ss"
                ).alias("updated_at"),

                # -----------------------------------------------------------------
                # Phone Cleanup
                # -----------------------------------------------------------------
                # Add a leading zero to 10-digit phone numbers.
                when(
                    length(trim(col("phone"))) == 10,
                    concat(
                        lit("0"),
                        trim(col("phone"))
                    )
                )
                .otherwise(
                    trim(col("phone"))
                )
                .alias("phone_temp"),

                # -----------------------------------------------------------------
                # Email Cleanup
                # -----------------------------------------------------------------
                # Append gmail.com when the source contains only a username
                # followed by the @ symbol.
                when(
                    lower(trim(col("email"))).rlike("^[^@\\s]+@$"),
                    concat(
                        lower(trim(col("email"))),
                        lit("gmail.com")
                    )
                )
                .otherwise(
                    lower(trim(col("email")))
                )
                .alias("email_temp")
            )

            # -----------------------------------------------------------------
            # Phone Validation
            # -----------------------------------------------------------------
            # Keep only Bangladesh-style mobile numbers:
            # 01XXXXXXXXX
            .withColumn(
                "phone",
                when(
                    col("phone_temp").rlike("^01[0-9]{9}$"),
                    col("phone_temp")
                )
                .otherwise(
                    lit("n/a")
                )
            )

            # -----------------------------------------------------------------
            # Email Validation
            # -----------------------------------------------------------------
            # Keep only values matching a basic email pattern.
            .withColumn(
                "email",
                when(
                    col("email_temp").rlike(
                        "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"
                    ),
                    col("email_temp")
                )
                .otherwise(
                    lit("n/a")
                )
            )

            # Remove temporary validation columns.
            .drop(
                "phone_temp",
                "email_temp"
            )

            # -----------------------------------------------------------------
            # SCD Type 2 Metadata
            # -----------------------------------------------------------------
            .withColumn(
                "source",
                lit("file")
            )
            .withColumn(
                "valid_from",
                col("updated_at")
            )
            .withColumn(
                "valid_to",
                lit(None).cast("timestamp")
            )
            .withColumn(
                "is_current",
                lit(1).cast("int")
            )
            .withColumn(
                "insertion_time",
                current_timestamp()
            )
        )


        # =====================================================================
        #                         Validate Incoming Data
        # =====================================================================

        # Check for duplicate employee versions within the incoming batch.
        #
        # The same employee_id and updated_at combination must not appear
        # more than once.
        duplicate_df = (
            df_employees_incremental
            .groupBy("employee_id", "updated_at")
            .count()
            .filter(col("count") > 1)
        )

        duplicate_count = duplicate_df.count()

        if duplicate_count > 0:
            raise ValueError(
                "Duplicate employee records detected for the same "
                "employee_id and updated_at."
            )


        # =====================================================================
        #                         Prepare SCD Type 2 Records
        # =====================================================================

        # Order employee versions by updated_at for each employee.
        scd_window = (
            Window
            .partitionBy("employee_id")
            .orderBy(col("updated_at"))
        )

        # The next version's updated_at becomes the current version's
        # valid_to value.
        df_employees_scd = (
            df_employees_incremental
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

        df_employees_scd = df_employees_scd.select(
            "employee_id",
            "name",
            "dob",
            "gender",
            "address",
            "role",
            "department_id",
            "hire_date",
            "salary",
            "status",
            "hospital_id",
            "created_at",
            "updated_at",
            "phone",
            "email",
            "source",
            "valid_from",
            "valid_to",
            "is_current",
            "insertion_time"
        )


        # =====================================================================
        #                         Find First Incoming Version
        # =========================================================================

        # Find the earliest incoming version for each employee.
        #
        # This timestamp is used to close the existing current Silver record.
        first_version_df = (
            df_employees_scd
            .groupBy("employee_id")
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
        # =========================================================================

        # Close the currently active employee record when a newer version
        # arrives for the same employee_id.
        (
            delta_table.alias("target")
            .merge(
                first_version_df.alias("source"),
                """
                target.employee_id = source.employee_id
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

        # Append new employee versions while preserving existing history.
        (
            df_employees_scd
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

        print("Employees incremental load completed successfully.")


# =============================================================================
#                         Error Handling
# =============================================================================

except Exception as error:

    error_message = str(error).replace("'", "''")

    print("Employees incremental load failed.")
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