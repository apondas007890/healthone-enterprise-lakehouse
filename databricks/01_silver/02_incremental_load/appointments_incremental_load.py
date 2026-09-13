"""
===============================================================================
                    Silver Layer - Appointments Processing
===============================================================================

Script Purpose:
    Reads incremental appointment data from the Bronze Layer, cleans and
    standardizes the data, applies SCD Type 2 logic, and writes the results
    to the Silver Delta table.

Processing Steps:
    1. Read incremental appointment data from the Bronze Layer.
    2. Apply the Bronze watermark to process only new/changed files.
    3. Clean and standardize appointment columns.
    4. Validate duplicate appointment versions.
    5. Create SCD Type 2 records using updated_at.
    6. Close the existing current Silver record when a new version arrives.
    7. Append the new appointment versions to Silver.
    8. Update the Bronze-to-Silver watermark after successful processing.
    9. Record execution status and errors in the metadata table.

SCD Type 2 Design:
    - appointment_id is the business key.
    - updated_at represents the effective time of a change.
    - valid_from = updated_at.
    - valid_to = next version's updated_at.
    - is_current = 1 for the latest version.
    - is_current = 0 for historical versions.

Important:
    The Bronze Layer must preserve multiple versions of the same appointment.
    A normal source-table UPDATE overwrites the previous value. Therefore,
    CDC, Change Tracking, temporal tables, or another history-preserving
    ingestion mechanism is required to capture every appointment version.

Target:
    Silver Delta table for appointments.

===============================================================================
"""

from pyspark.sql.functions import (
    col,
    lit,
    trim,
    lower,
    to_timestamp,
    row_number,
    lead,
    when,
    max
)

from pyspark.sql.window import Window
from delta.tables import DeltaTable
from datetime import datetime
import traceback


# =============================================================================
#                         Configuration
# =============================================================================

# Bronze source containing incremental appointment records.
source_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/appointments/"

# Silver target containing SCD Type 2 appointment history.
target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/appointments/"

# Metadata table used to control incremental processing.
watermark_table = "healthone_lakehouse.metadata.watermark_bronze_silver"

# Logical table name used in the watermark table.
table_name = "appointments"


# =============================================================================
#                         Execution Metadata
# =============================================================================

# Capture the execution start time for the current pipeline run.
current_run_timestamp = datetime.now()

# Read the last successfully processed Bronze file timestamp.
last_watermark = (
    spark.table(watermark_table)
    .filter(col("table_name") == table_name)
    .select("last_watermark")
    .first()["last_watermark"]
)


# =============================================================================
#                         Read Bronze Increment
# =============================================================================

# Read only Bronze records whose file modification time is newer than
# the previously processed watermark.
df_bronze = (
    spark.read
    .parquet(source_path)
    .filter(
        (col("_metadata.file_modification_time") > lit(last_watermark)) &
        (col("_metadata.file_modification_time") <= lit(current_run_timestamp))
    )
)


# Stop the pipeline when no new Bronze data is available.
if df_bronze.limit(1).count() == 0:

    spark.sql(f"""
        UPDATE {watermark_table}
        SET
            status = 'NO_DATA',
            started_at = TIMESTAMP('{current_run_timestamp}'),
            completed_at = current_timestamp(),
            error_message = NULL
        WHERE table_name = '{table_name}'
    """)

else:

    try:

        # =============================================================================
        #                         Clean and Standardize Data
        # =============================================================================

        # Standardize appointment columns and convert them to the Silver data types.
        df_appointments = (
            df_bronze
            .select(
                col("appointment_id").cast("long").alias("appointment_id"),

                col("patient_id").cast("long").alias("patient_id"),

                col("doctor_id").cast("long").alias("doctor_id"),

                col("hospital_id").cast("long").alias("hospital_id"),

                to_timestamp(
                    trim(col("appointment_datetime"))
                ).alias("appointment_datetime"),

                lower(
                    trim(col("status"))
                ).alias("status"),

                lower(
                    trim(col("reason"))
                ).alias("reason"),

                to_timestamp(
                    trim(col("created_at"))
                ).alias("created_at"),

                to_timestamp(
                    trim(col("updated_at"))
                ).alias("updated_at"),

                lit("sql-hospital-ops").alias("source"),

                to_timestamp(
                    trim(col("updated_at"))
                ).alias("valid_from"),

                lit(None).cast("timestamp").alias("valid_to"),

                lit(1).cast("int").alias("is_current"),

                col("_metadata.file_modification_time").alias(
                    "bronze_file_modification_time"
                )
            )
        )


        # =============================================================================
        #                         Duplicate Validation
        # =============================================================================

        # Identify duplicate versions of the same appointment.
        duplicate_window = (
            Window
            .partitionBy("appointment_id", "updated_at")
            .orderBy(col("bronze_file_modification_time").desc())
        )

        # Keep only the latest Bronze copy of an identical appointment version.
        df_appointments = (
            df_appointments
            .withColumn(
                "_row_number",
                row_number().over(duplicate_window)
            )
            .filter(col("_row_number") == 1)
            .drop("_row_number")
        )


        # =============================================================================
        #                         Create SCD Type 2 Versions
        # =============================================================================

        # Order appointment versions chronologically for each appointment.
        scd_window = (
            Window
            .partitionBy("appointment_id")
            .orderBy("updated_at")
        )

        # The next update becomes the valid_to timestamp of the current version.
        df_appointments_scd = (
            df_appointments
            .withColumn(
                "valid_to",
                lead("updated_at").over(scd_window)
            )
            .withColumn(
                "is_current",
                when(
                    col("valid_to").isNull(),
                    1
                ).otherwise(0).cast("int")
            )
        )


        # =============================================================================
        #                  Identify First Version of Each Appointment
        # =============================================================================

        # Find the earliest incoming version for each appointment.
        df_first_version = (
            df_appointments_scd
            .groupBy("appointment_id")
            .agg(
                min("valid_from").alias("first_db_valid_from")
            )
        )

        # Add the first incoming version timestamp to the SCD dataset.
        df_appointments_scd_first_version = (
            df_appointments_scd
            .join(
                df_first_version,
                on="appointment_id",
                how="left"
            )
        )


        # =============================================================================
        #                         Close Current Records
        # =============================================================================

        # Close the existing Silver current version when a newer appointment
        # version arrives.
        delta_target = DeltaTable.forPath(spark, target_path)

        (
            delta_target.alias("tgt")
            .merge(
                df_appointments_scd_first_version.alias("src"),
                """
                tgt.appointment_id = src.appointment_id
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


        # =============================================================================
        #                         Write Silver Data
        # =============================================================================

        # Append the new SCD Type 2 versions to the Silver Delta table.
        (
            df_appointments_scd_first_version
            .drop("first_db_valid_from")
            .drop("bronze_file_modification_time")
            .write
            .format("delta")
            .mode("append")
            .save(target_path)
        )


        # =============================================================================
        #                         Update Watermark
        # =============================================================================

        # Advance the watermark only to the latest Bronze file actually processed.
        batch_max_file_time = (
            df_bronze
            .agg(
                max("_metadata.file_modification_time").alias("max_file_time")
            )
            .first()["max_file_time"]
        )

        # Record the successful execution in the metadata table.
        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                last_watermark = TIMESTAMP('{batch_max_file_time}'),
                rows_loaded = {df_appointments_scd_first_version.count()},
                status = 'SUCCESS',
                started_at = TIMESTAMP('{current_run_timestamp}'),
                completed_at = current_timestamp(),
                error_message = NULL
            WHERE table_name = '{table_name}'
        """)


    except Exception as e:

        # Record the failure so the next pipeline run can be investigated
        # without advancing the watermark.
        error_message = str(e).replace("'", "''")

        spark.sql(f"""
            UPDATE {watermark_table}
            SET
                status = 'FAILED',
                started_at = TIMESTAMP('{current_run_timestamp}'),
                completed_at = current_timestamp(),
                error_message = '{error_message}'
            WHERE table_name = '{table_name}'
        """)

        raise