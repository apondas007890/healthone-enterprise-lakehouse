/*
===============================================================================
              Metadata Layer - Bronze to Silver Watermark Control
===============================================================================

Purpose:
    Creates and initializes the control table used to track Bronze-to-Silver
    incremental load executions.

The control table stores:
    - table_name       : Table being processed.
    - last_watermark   : Last successfully processed data watermark.
    - rows_loaded      : Number of rows loaded in the last execution.
    - status            : Current execution status.
    - started_at        : Load execution start time.
    - completed_at      : Load execution completion time.
    - error_message     : Error details when a load fails.

Design:
    - One control record is maintained for each source/target table.
    - The watermark is advanced only after a successful load.
    - Execution details support monitoring and troubleshooting.
    - Delta Lake provides reliable metadata storage.

Initialization:
    - Existing control table is dropped and recreated.
    - Each table starts with a default watermark of 2000-01-01.
    - Initial status is set to PENDING.
    - The ingestion pipeline is responsible for updating the control records.

===============================================================================
*/


-- ============================================================
-- Patients
-- ============================================================

DROP TABLE IF EXISTS healthone_lakehouse.silver.patients;

CREATE TABLE IF NOT EXISTS healthone_lakehouse.silver.patients (

    -- Patient
    patient_id BIGINT,
    first_name STRING,
    last_name STRING,

    -- Demographics & Contact
    dob DATE,
    gender STRING,
    phone STRING,
    address STRING,
    email STRING,
    blood_group STRING,

    -- Hospital
    hospital_id BIGINT,

    -- Source Audit
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    -- SCD Type 2
    source STRING,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current INT

)
USING DELTA
LOCATION 'abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/patients/';


-- ============================================================
-- Billing
-- ============================================================

DROP TABLE IF EXISTS healthone_lakehouse.silver.billing;

CREATE TABLE IF NOT EXISTS healthone_lakehouse.silver.billing (

    -- Identifiers
    bill_id BIGINT,
    admission_id BIGINT,
    patient_id BIGINT,

    -- Financial
    amount DECIMAL(18, 2),
    insurance_covered DECIMAL(18, 2),
    payment_status STRING,

    -- Dates & Audit
    bill_datetime TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    -- SCD Type 2
    source STRING,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current INT

)
USING DELTA
LOCATION 'abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/billing/';


-- ============================================================
-- Appointments
-- ============================================================

DROP TABLE IF EXISTS healthone_lakehouse.silver.appointments;

CREATE TABLE IF NOT EXISTS healthone_lakehouse.silver.appointments (

    -- Appointment
    appointment_id BIGINT,

    -- Related Entities
    patient_id BIGINT,
    doctor_id BIGINT,
    hospital_id BIGINT,

    -- Appointment Details
    appointment_datetime TIMESTAMP,
    status STRING,
    reason STRING,

    -- Source Audit
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    -- SCD Type 2
    source STRING,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current INT

)
USING DELTA
LOCATION 'abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/appointments/';