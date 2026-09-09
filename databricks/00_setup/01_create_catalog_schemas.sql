%sql
-- 1. Create and Select Catalog
CREATE CATALOG IF NOT EXISTS healthone_lakehouse
MANAGED LOCATION 'abfss://catalog@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'HealthOne Enterprise Lakehouse - All data layers';

USE CATALOG healthone_lakehouse;

-- 2. Create Schemas with Target Storage Locations
CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.bronze
COMMENT 'Raw landing ingestion layer (Parquet, CSV, and multi-format files)';

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.silver
MANAGED LOCATION 'abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'Cleansed, validated, SCD2 data (Delta tables)';

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.gold
MANAGED LOCATION 'abfss://gold@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'Aggregated business-ready data (Delta tables)';

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.test
MANAGED LOCATION 'abfss://test@sthealthonelakehouseci.dfs.core.windows.net/'
COMMENT 'test (Delta tables)';

CREATE SCHEMA IF NOT EXISTS healthone_lakehouse.metadata
COMMENT 'Control tables, configs, reference data';

-- 3. Create Bronze External Tables (Corporate HR)
CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.hospitals
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/hospitals/';

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.departments
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/departments/';

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.employees
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/employees/';

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.payroll
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-corporate-hr/payroll/';

-- 4. Create Bronze External Tables (Hospital Operations)
CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.patients
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/patients/';

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.doctors
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/doctors/';

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.appointments
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/appointments/';

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.admissions
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/admissions/';

CREATE TABLE IF NOT EXISTS healthone_lakehouse.bronze.billing
USING PARQUET
LOCATION 'abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/sql-healthone-lakehouse-central-india.database.windows.net/sqldb-healthone-ops/billing/';

-- 5. Permissions
GRANT USE SCHEMA, SELECT ON SCHEMA healthone_lakehouse.bronze TO `account users`;
GRANT USE SCHEMA, SELECT, MODIFY ON SCHEMA healthone_lakehouse.silver TO `account users`;
GRANT USE SCHEMA, SELECT, MODIFY ON SCHEMA healthone_lakehouse.gold TO `account users`;
GRANT USE SCHEMA, SELECT, MODIFY ON SCHEMA healthone_lakehouse.test TO `account users`;
GRANT USE SCHEMA ON SCHEMA healthone_lakehouse.metadata TO `account users`;

/*
%sql
USE CATALOG healthone_lakehouse;
-- List schemas in this catalog
SHOW SCHEMAS;
-- List tables inside the bronze schema
SHOW TABLES IN bronze;

OR
print("Catalog and schemas created successfully!")
display(spark.sql("SHOW SCHEMAS IN healthone_lakehouse"))
display(spark.sql("SHOW TABLES IN healthone_lakehouse.bronze"))
*/
