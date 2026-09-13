"""
===============================================================================
                    Silver Layer - Doctors File Processing
===============================================================================

Script Purpose:
    Reads doctor data from the Bronze file, cleans and standardizes the data,
    adds Silver-layer metadata, and writes the result as a Delta table.

Processing Steps:
    1. Read the Bronze doctors file.
    2. Cast ID columns to the required numeric data types.
    3. Standardize specialization values.
    4. Convert date and timestamp columns to the required data types.
    5. Add source and SCD Type 2 metadata columns.
    6. Write the transformed data to the Silver Delta location.
    7. Register the Delta location as a Unity Catalog table.
    8. Optimize the table using Z-Ordering on employee_id.

Notes:
    - Bronze data remains unchanged.
    - Silver data contains cleaned and standardized doctor records.
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
    to_timestamp,
    current_timestamp
)


# =============================================================================
#                         Read Bronze File
# =============================================================================

# df_raw_file should contain the doctor records read from the Bronze layer.
# The file-reading logic can be defined in the Bronze ingestion notebook
# or earlier in this notebook.

# Path to the Bronze CSV file containing employee data.
file_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/onedrive_landing/doctors.csv"

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

# Select the required doctor columns and apply data-quality transformations.
#
# - ID columns are converted to BIGINT.
# - specialization is trimmed and converted to lowercase.
# - created_at and updated_at are converted to TIMESTAMP.
df_doctors_file = (
    df_raw_file
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
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/doctors/"

# Unity Catalog table used to query the Silver data with SQL.
table_name = "healthone_lakehouse.silver.doctors"


# =============================================================================
#                         Write Data to Silver Delta
# =============================================================================

# Write the transformed doctor data in Delta format.
#
# overwrite:
#     Replaces the existing Silver data.
#
# overwriteSchema:
#     Allows the target Delta schema to be updated when required.
(
    df_doctors_file
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
# that filter or match doctor records using employee_id.
spark.sql(f"""
    OPTIMIZE {table_name}
    ZORDER BY (employee_id)
""")