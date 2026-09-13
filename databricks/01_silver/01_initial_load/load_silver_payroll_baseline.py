"""
===============================================================================
                    Silver Layer - Payroll File Processing
===============================================================================

Script Purpose:
    Reads payroll data from the Bronze CSV file, cleans and standardizes
    the data, adds Silver-layer metadata, and writes the result as a Delta
    table.

Processing Steps:
    1. Read the Bronze payroll CSV file.
    2. Cast payroll columns to the required data types.
    3. Calculate net_pay from gross_pay and deductions.
    4. Add source and SCD Type 2 metadata columns.
    5. Write the transformed data to the Silver Delta location.
    6. Register the Delta location as a Unity Catalog table.
    7. Optimize the table using Z-Ordering on employee_id.

Notes:
    - Bronze data remains unchanged.
    - Silver data contains cleaned and standardized records.
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
    to_date,
    to_timestamp,
    current_timestamp
)


# =============================================================================
#                         Read Bronze CSV File
# =============================================================================

# Path to the Bronze CSV file containing payroll data.
file_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/onedrive_landing/payroll.csv"

# Read the CSV file.
# inferSchema=False keeps all source fields as strings so that each column
# can be explicitly converted to the required Silver data type.
df_raw_file = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")
    .csv(file_path)
)


# =============================================================================
#                         Clean and Standardize Data
# =============================================================================

# Select the required payroll columns and apply data-type transformations.
#
# - ID columns are converted to BIGINT.
# - pay_period remains STRING because it represents the payroll period.
# - Monetary values are converted to DECIMAL for financial accuracy.
# - net_pay is calculated as gross_pay minus deductions.
# - paid_date is converted to DATE.
# - created_at and updated_at are converted to TIMESTAMP.
df_payroll_file = (
    df_raw_file
    .select(
        col("payroll_id")
            .cast("long")
            .alias("payroll_id"),

        col("employee_id")
            .cast("long")
            .alias("employee_id"),

        col("pay_period")
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
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/payroll/"

# Unity Catalog table used to query the Silver data with SQL.
table_name = "healthone_lakehouse.silver.payroll"


# =============================================================================
#                         Write Data to Silver Delta
# =============================================================================

# Write the transformed payroll data in Delta format.
#
# overwrite:
#     Replaces the existing Silver data.
#
# overwriteSchema:
#     Allows the target Delta schema to be updated when required.
(
    df_payroll_file
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
# that filter or match payroll records using employee_id.
spark.sql(f"""
    OPTIMIZE {table_name}
    ZORDER BY (employee_id)
""")