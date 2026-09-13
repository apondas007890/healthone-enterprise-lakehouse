/*
===============================================================================
                    Metadata Layer - Bronze to Silver Watermark
===============================================================================

Script Purpose:
    This script creates and initializes the watermark control table used to
    track Bronze-to-Silver incremental data loads.

    The table stores:
        1. The name of the source or target table being processed.
        2. The last successfully processed watermark timestamp.
        3. The number of rows loaded during the execution.
        4. The execution status of the load.
        5. The start and completion timestamps.
        6. Any error message generated during processing.

Design Principles:
    - Each source table has its own watermark record.
    - The watermark identifies the latest successfully processed data.
    - The table supports incremental loading from Bronze to Silver.
    - Execution details are recorded for monitoring and troubleshooting.
    - Delta Lake is used for reliable metadata storage.

Usage Notes:
    - The existing watermark table is dropped and recreated.
    - All tables start with a default watermark of 2000-01-01.
    - The initial status of every table is set to PENDING.
    - The watermark should be updated only after a successful load.
    - In production, this table should be updated by the ingestion pipeline.

===============================================================================
*/


-- =============================================================================
--                         Recreate Watermark Table
-- =============================================================================

-- Remove the existing watermark table if it already exists.
-- This is useful when initializing or resetting the metadata environment.
DROP TABLE IF EXISTS workspace.metadata.watermark_bronze_silver;


-- =============================================================================
--                         Create Watermark Table
-- =============================================================================

-- Create the Delta table that stores incremental-load metadata.
CREATE TABLE workspace.metadata.watermark_bronze_silver (
    table_name STRING, -- Name of the table being processed
    last_watermark TIMESTAMP, -- Latest successfully processed source timestamp
    rows_loaded BIGINT, -- Number of records loaded during the latest execution
    status STRING, -- Current execution status, such as PENDING, RUNNING, SUCCESS, or FAILED
    started_at TIMESTAMP, -- Timestamp when the load process started
    completed_at TIMESTAMP, -- Timestamp when the load process completed
    error_message STRING -- Error details when the load fails

)

USING DELTA

-- Describe the purpose of this metadata table
COMMENT 'Tracks high-watermarks and execution status for incremental loads';


-- =============================================================================
--                         Initialize Watermark Records
-- =============================================================================

-- Insert one initial control record for each table participating in the
-- Bronze-to-Silver ingestion process.
INSERT INTO workspace.metadata.watermark_bronze_silver (

    table_name,
    last_watermark,
    rows_loaded,
    status,
    started_at,
    completed_at,
    error_message

)

VALUES

    -- Hospital master data
    (
        'hospitals',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Department master data
    (
        'departments',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Doctor master data
    (
        'doctors',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Employee master data
    (
        'employees',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Payroll transaction data
    (
        'payroll',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Patient master data
    (
        'patients',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Appointment transaction data
    (
        'appointments',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Admission transaction data
    (
        'admissions',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    ),

    -- Billing transaction data
    (
        'billing',
        '2000-01-01 00:00:00',
        0,
        'PENDING',
        '2000-01-01 00:00:00',
        '2000-01-01 00:00:00',
        NULL
    );