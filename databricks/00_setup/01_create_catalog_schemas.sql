/*
===============================================================================
                 HealthOne Lakehouse - Catalog & Schema Setup
===============================================================================

Purpose:
    Creates the Unity Catalog structure and Bronze external tables for the
    HealthOne lakehouse.

Structure:
    Catalog:
        - healthone_lakehouse

    Schemas:
        - bronze
        - silver
        - gold
        - test
        - metadata

    Bronze Sources:
        - Corporate HR
            - hospitals
            - departments
            - employees
            - payroll

        - Hospital Operations
            - patients
            - doctors
            - appointments
            - admissions
            - billing

Design:
    - The catalog provides the top-level namespace for the HealthOne lakehouse.
    - Bronze uses external Parquet tables over ADLS Gen2 landing data.
    - Silver stores cleansed, validated, and SCD Type 2 data.
    - Gold stores business-ready analytical data.
    - Test is used for development and validation.
    - Metadata stores control tables and configuration data.
    - Schema-level permissions are granted to account users.

Storage:
    Catalog:
        abfss://catalog@sthealthonelakehouseci.dfs.core.windows.net/

    Bronze:
        abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/

    Silver:
        abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/

    Gold:
        abfss://gold@sthealthonelakehouseci.dfs.core.windows.net/

    Test:
        abfss://test@sthealthonelakehouseci.dfs.core.windows.net/

===============================================================================
*/


-- =============================================================================
-- Catalog: HealthOne Lakehouse
-- =============================================================================
-- Creates the main Unity Catalog catalog for the HealthOne lakehouse.

CREATE CATALOG IF NOT EXISTS healthone_lakehouse
MANAGED LOCATION 'abfss://catalog@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'HealthOne Enterprise Lakehouse - All data layers';

USE CATALOG healthone_lakehouse;


-- =============================================================================
-- Schema: Bronze
-- =============================================================================
-- Stores raw source data used for ingestion into the lakehouse.

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.bronze
COMMENT 'Raw landing ingestion layer (Parquet, CSV, and multi-format files)';


-- =============================================================================
-- Schema: Silver
-- =============================================================================
-- Stores cleansed, validated, and historized SCD Type 2 Delta tables.

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.silver
MANAGED LOCATION 'abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'Cleansed, validated, SCD2 data (Delta tables)';


-- =============================================================================
-- Schema: Gold
-- =============================================================================
-- Stores business-ready analytical tables and views.

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.gold
MANAGED LOCATION 'abfss://gold@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'Aggregated business-ready data (Delta tables)';


-- =============================================================================
-- Schema: Test
-- =============================================================================
-- Provides an isolated area for development, testing, and validation.

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.test
MANAGED LOCATION 'abfss://test@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'Test and validation data (Delta tables)';


-- =============================================================================
-- Schema: Metadata
-- =============================================================================
-- Stores control tables, configuration, and pipeline metadata.

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.metadata
COMMENT 'Control tables, configs, reference data';


-- =============================================================================
-- Bronze Tables: Corporate HR
-- =============================================================================
-- External Parquet tables for data sourced from the Corporate HR database.


-- -----------------------------------------------------------------------------
-- Table: Hospitals
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.hospitals
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/hospitals/';


-- -----------------------------------------------------------------------------
-- Table: Departments
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.departments
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/departments/';


-- -----------------------------------------------------------------------------
-- Table: Employees
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.employees
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/employees/';


-- -----------------------------------------------------------------------------
-- Table: Payroll
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.payroll
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/payroll/';


-- =============================================================================
-- Bronze Tables: Hospital Operations
-- =============================================================================
-- External Parquet tables for data sourced from the Hospital Operations database.


-- -----------------------------------------------------------------------------
-- Table: Patients
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.patients
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/patients/';


-- -----------------------------------------------------------------------------
-- Table: Doctors
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.doctors
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/doctors/';


-- -----------------------------------------------------------------------------
-- Table: Appointments
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.appointments
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/appointments/';


-- -----------------------------------------------------------------------------
-- Table: Admissions
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.admissions
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/admissions/';


-- -----------------------------------------------------------------------------
-- Table: Billing
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.billing
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/billing/';


-- =============================================================================
-- Permissions
-- =============================================================================
-- Grants users access according to the role of each lakehouse layer.

GRANT USE SCHEMA, SELECT
ON SCHEMA healthone_lakehouse.bronze
TO `account users`;

GRANT USE SCHEMA, SELECT, MODIFY
ON SCHEMA healthone_lakehouse.silver
TO `account users`;

GRANT USE SCHEMA, SELECT, MODIFY
ON SCHEMA healthone_lakehouse.gold
TO `account users`;

GRANT USE SCHEMA, SELECT, MODIFY
ON SCHEMA healthone_lakehouse.test
TO `account users`;

GRANT USE SCHEMA
ON SCHEMA healthone_lakehouse.metadata
TO `account users`;


/*
===============================================================================
                         Validation - Optional
===============================================================================

Use the following commands to verify that the catalog, schemas, and Bronze
tables were created successfully.

===============================================================================

USE CATALOG healthone_lakehouse;

SHOW SCHEMAS;

SHOW TABLES IN bronze;

-- Or from a Python notebook cell:

print("Catalog and schemas created successfully!")

display(
    spark.sql("SHOW SCHEMAS IN healthone_lakehouse")
)

display(
    spark.sql("SHOW TABLES IN healthone_lakehouse.bronze")
)

===============================================================================
*/
