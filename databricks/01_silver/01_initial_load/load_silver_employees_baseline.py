"""
===============================================================================
                    Silver Layer - Employees File Processing
===============================================================================

Script Purpose:
    Reads employee data from the Bronze CSV file, cleans and standardizes
    employee attributes, applies basic data-quality rules, adds Silver-layer
    metadata, and prepares the data for Delta storage.

Processing Steps:
    1. Read the Bronze employees CSV file.
    2. Clean and standardize employee attributes.
    3. Standardize gender values.
    4. Clean and validate phone numbers.
    5. Clean and validate email addresses.
    6. Cast IDs, dates, salary, and timestamp columns to required data types.
    7. Add source and SCD Type 2 metadata columns.
    8. Write the transformed data to the Silver Delta location.
    9. Register the Delta location as a Unity Catalog table.
   10. Optimize the table using Z-Ordering on employee_id.

Notes:
    - Bronze data remains unchanged.
    - Silver data contains cleaned and standardized employee records.
    - Invalid phone numbers and email addresses are stored as "n/a".
    - This script uses full overwrite and is intended for initial or
      controlled full-refresh processing.
    - Production incremental processing should use Delta MERGE.
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
    concat_ws
)


# =============================================================================
#                         Read Bronze CSV File
# =============================================================================

# Path to the Bronze CSV file containing employee data.
file_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/onedrive_landing/employees.csv"

# Read the CSV file.
# inferSchema=False keeps source fields as strings so that each column
# can be explicitly converted to the required Silver data type.
#
# quote and escape ensure quoted CSV values are read correctly.
df_raw_file = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")
    .option("quote", '"')
    .option("escape", '"')
    .csv(file_path)
)


# =============================================================================
#                         Clean and Standardize Data
# =============================================================================

# Select the required employee columns and apply data-quality transformations.
#
# - IDs are converted to numeric data types.
# - Names, addresses, roles, and statuses are trimmed and lowercased.
# - Dates and timestamps are converted to proper Spark data types.
# - Salary is converted to DECIMAL for accurate financial values.
# - Gender is standardized to m, f, or n/a.
df_employees_file = (
    df_raw_file
    .select(
        col("employee_id")
            .cast("long")
            .alias("employee_id"),

        # Combine first and last name into one standardized name column.
        concat_ws(
            " ",
            lower(trim(col("first_name"))),
            lower(trim(col("last_name")))
        ).alias("name"),

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

        lower(trim(col("address"))).alias("address"),

        lower(trim(col("role"))).alias("role"),

        col("department_id")
            .cast("int")
            .alias("department_id"),

        to_date(
            col("hire_date"),
            "yyyy-MM-dd"
        ).alias("hire_date"),

        col("salary")
            .cast("decimal(10,2)")
            .alias("salary"),

        lower(trim(col("status"))).alias("status"),

        col("hospital_id")
            .cast("int")
            .alias("hospital_id"),

        to_timestamp(
            col("created_at"),
            "yyyy-MM-dd HH:mm:ss"
        ).alias("created_at"),

        to_timestamp(
            col("updated_at"),
            "yyyy-MM-dd HH:mm:ss"
        ).alias("updated_at"),

        # ---------------------------------------------------------------------
        # Phone Cleanup
        # ---------------------------------------------------------------------
        # Add a leading 0 when the source contains a 10-digit phone number.
        # The temporary column is validated below.
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

        # ---------------------------------------------------------------------
        # Email Cleanup
        # ---------------------------------------------------------------------
        # If the email ends with '@' but has no domain, append gmail.com.
        # The temporary column is validated below.
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

    # -------------------------------------------------------------------------
    # Phone Validation
    # -------------------------------------------------------------------------

    # Keep only valid Bangladesh-style mobile numbers matching 01XXXXXXXXX.
    # Invalid or malformed phone numbers are replaced with "n/a".
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

    # -------------------------------------------------------------------------
    # Email Validation
    # -------------------------------------------------------------------------

    # Keep only values matching a basic email format.
    # Invalid or malformed email addresses are replaced with "n/a".
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

    # Temporary columns are no longer required after validation.
    .drop(
        "phone_temp",
        "email_temp"
    )

    # -------------------------------------------------------------------------
    # SCD Type 2 Metadata
    # -------------------------------------------------------------------------

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


# =============================================================================
#                         Define Silver Target
# =============================================================================

# ADLS Gen2 location where the Silver Delta data will be stored.
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/employees/"

# Unity Catalog table used to query the Silver data with SQL.
table_name = "healthone_lakehouse.silver.employees"


# =============================================================================
#                         Write Data to Silver Delta
# =============================================================================

# Write the transformed employee data in Delta format.
#
# overwrite:
#     Replaces the existing Silver data.
#
# overwriteSchema:
#     Allows the target Delta schema to be updated when required.
(
    df_employees_file
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(target_path)
)


# =============================================================================
#                         Register Unity Catalog Table
# =============================================================================

# Register the existing Delta location as a Unity Catalog table.
# IF NOT EXISTS prevents an error if the table is already registered.
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {table_name}
    USING DELTA
    LOCATION '{target_path}'
""")


# =============================================================================
#                         Optimize Silver Table
# =============================================================================

# Compact small Delta files and organize data using employee_id.
# Z-Ordering improves data skipping for queries and MERGE operations
# that filter or match employee records using employee_id.
spark.sql(f"""
    OPTIMIZE {table_name}
    ZORDER BY (employee_id)
""")