"""
===============================================================================
                    Silver Layer - Hospitals File Processing
===============================================================================

Script Purpose:
    This script reads hospital data from a JSON file stored in the Bronze Layer,
    transforms and standardizes the data, and writes the result to a Silver
    Delta table.

    The script performs the following operations:
        1. Reads the hospitals JSON file from ADLS Gen2.
        2. Explodes the hospitals array into individual hospital records.
        3. Cleans and standardizes string, date, and numeric columns.
        4. Adds metadata columns required for SCD Type 2 processing.
        5. Writes the transformed data to the Silver Delta location.
        6. Registers the Delta location as a Unity Catalog table.
        7. Optimizes the table using Z-Ordering on hospital_id.

Design Principles:
    - Bronze data is treated as the raw source.
    - Silver data is cleaned and standardized.
    - String values are trimmed and converted to lowercase.
    - Numeric and date columns are explicitly cast to the correct data types.
    - Metadata columns support source tracking and historical processing.
    - Delta Lake is used for reliable storage and table management.

Usage Notes:
    - This script performs a full overwrite of the target Silver data.
    - It should be used for initial loading or controlled full-refresh processing.
    - For production incremental processing, use MERGE instead of overwrite.
    - The target directory and Unity Catalog table must be accessible.
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
    to_date,
    to_timestamp,
    current_timestamp
)


# =============================================================================
#                         Read Bronze JSON File
# =============================================================================

# Path of the hospital JSON file stored in the Bronze Layer
file_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/onedrive_landing/hospitals_departments.json"

# Read the JSON file.
# multiline=True is required because the file contains a JSON document
# with the hospitals array stored across multiple lines.
df_raw_file = (
    spark.read
    .option("multiline", "true")
    .json(file_path)
)


# =============================================================================
#                         Extract Hospital Records
# =============================================================================

# Explode the hospitals array so that each hospital becomes a separate row.
# The hospital struct is then expanded into individual columns.
df_hospitals_file = (
    df_raw_file
    .select(explode(col("hospitals")).alias("hospital"))
    .select("hospital.*")
)


# =============================================================================
#                         Clean and Standardize Data
# =============================================================================

# Select the required hospital columns and apply data-quality transformations.
# - Numeric fields are converted to appropriate numeric data types.
# - String fields are trimmed and converted to lowercase.
# - Date and timestamp fields are converted to proper Spark data types.
df_hospitals_file = (
    df_hospitals_file
    .select(
        col("hospital_id").cast("long"),
        lower(trim(col("name"))).alias("name"),
        lower(trim(col("address"))).alias("address"),
        lower(trim(col("city"))).alias("city"),
        lower(trim(col("region"))).alias("region"),
        col("capacity").cast("int"),to_date(col("opened_date"),"yyyy-MM-dd").alias("opened_date"),
        to_timestamp(col("created_at"),"yyyy-MM-dd HH:mm:ss").alias("created_at"),
        to_timestamp(col("updated_at"),"yyyy-MM-dd HH:mm:ss").alias("updated_at"))
        .withColumn("source", lit("file")) # Identify the original source of the record
        .withColumn("valid_from", col("updated_at")) # Set the beginning of the record's validity period
        .withColumn("valid_to", lit(None).cast("timestamp"))  # A null valid_to value indicates that the record is currently active
        .withColumn("is_current", lit(1).cast("int")) # Mark the record as the current version
        .withColumn("insertion_time", current_timestamp()) # Store the time when the record is inserted into the Silver Layer
)


# =============================================================================
#                         Define Silver Target
# =============================================================================

# ADLS Gen2 path where the Silver Delta data will be stored
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/hospitals/"

# Unity Catalog table name used to query the Silver data with SQL
table_name = "healthone_lakehouse.silver.hospitals"


# =============================================================================
#                         Write Data to Silver Delta
# =============================================================================

# Write the transformed hospital data in Delta format.
# overwrite replaces the existing data at the target location.
# overwriteSchema allows the target schema to be updated when required.
(
    df_hospitals_file
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(target_path)
)


# =============================================================================
#                         Register Unity Catalog Table
# =============================================================================

# Register the existing Delta files as a Unity Catalog table.
# IF NOT EXISTS prevents an error if the table has already been registered.
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {table_name}
    USING DELTA
    LOCATION '{target_path}'
""")


# =============================================================================
#                         Optimize Silver Table
# =============================================================================

# Optimize the Delta table to compact small files and improve query performance.
# ZORDER organizes data based on hospital_id so queries filtering by this column
# can skip irrelevant data files more efficiently.
spark.sql(f"""
    OPTIMIZE {table_name}
    ZORDER BY (hospital_id)
""")