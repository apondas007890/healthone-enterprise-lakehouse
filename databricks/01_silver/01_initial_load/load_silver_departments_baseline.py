"""
===============================================================================
                    Silver Layer - Departments File Processing
===============================================================================

Script Purpose:
    This script reads department data from a JSON file stored in the Bronze
    Layer, transforms and standardizes the data, and writes the result to a
    Silver Delta table.

    The script performs the following operations:
        1. Reads the departments JSON file from ADLS Gen2.
        2. Explodes the departments array into individual department records.
        3. Cleans and standardizes string, numeric, and timestamp columns.
        4. Adds metadata columns required for SCD Type 2 processing.
        5. Writes the transformed data to the Silver Delta location.
        6. Registers the Delta location as a Unity Catalog table.
        7. Optimizes the table using Z-Ordering on department_id.

Design Principles:
    - Bronze data is treated as the raw source.
    - Silver data is cleaned and standardized.
    - String values are trimmed and converted to lowercase.
    - Numeric and timestamp columns are explicitly cast.
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
    to_timestamp,
    current_timestamp
)


# =============================================================================
#                         Read Bronze JSON File
# =============================================================================

# Path of the department JSON file stored in the Bronze Layer
file_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/onedrive_landing/hospitals_departments.json"

# Read the JSON file.
# multiline=True is required because the file contains a JSON document
# with the departments array stored across multiple lines.
df_raw_file = (
    spark.read
    .option("multiline", "true")
    .json(file_path)
)


# =============================================================================
#                         Extract Department Records
# =============================================================================

# Explode the departments array so that each department becomes a separate row.
# The department struct is then expanded into individual columns.
df_departments_file = (
    df_raw_file
    .select(explode(col("departments")).alias("department"))
    .select("department.*")
)


# =============================================================================
#                         Clean and Standardize Data
# =============================================================================

# Select the required department columns and apply data-quality transformations.
#
# - department_id and hospital_id are converted to long.
# - name is trimmed and converted to lowercase.
# - created_at and updated_at are converted to timestamps.
df_departments_file = (
    df_departments_file
    .select(
        col("department_id").cast("long"),
        lower(trim(col("name"))).alias("name"),
        col("hospital_id").cast("long"),
        to_timestamp(col("created_at"), "yyyy-MM-dd HH:mm:ss").alias("created_at"),
        to_timestamp(col("updated_at"), "yyyy-MM-dd HH:mm:ss").alias("updated_at"))
        .withColumn("source", lit("file")) # Identify the original source of the record
        .withColumn("valid_from", col("updated_at")) # Set the beginning of the record's validity period
        .withColumn("valid_to", lit(None).cast("timestamp")) # NULL valid_to means the record is currently active
        .withColumn("is_current", lit(1).cast("int")) # Mark the record as the current version
        .withColumn("insertion_time", current_timestamp()) # Store the time when the record is inserted into Silver
)


# =============================================================================
#                         Define Silver Target
# =============================================================================

# ADLS Gen2 path where the Silver Delta data will be stored
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/departments/"


# Unity Catalog table name used to query the Silver data with SQL
table_name = "healthone_lakehouse.silver.departments"


# =============================================================================
#                         Write Data to Silver Delta
# =============================================================================

# Write the transformed department data in Delta format.
#
# overwrite replaces the existing data at the target location.
# overwriteSchema allows the target schema to be updated when required.
(
    df_departments_file
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
#
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
#
# ZORDER organizes data based on department_id so queries filtering by this
# column can skip irrelevant data files more efficiently.
spark.sql(f"""
    OPTIMIZE {table_name}
    ZORDER BY (department_id)
""")