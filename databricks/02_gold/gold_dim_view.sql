/*
===============================================================================
                    Gold Layer - Dimension Views
===============================================================================

Purpose:
    Creates the Gold-layer dimension views for the HealthOne analytical
    star schema.

Dimensions:
    - dim_hospitals
    - dim_departments
    - dim_doctors
    - dim_employees
    - dim_patients

Design:
    - Built from the cleaned and historized Silver-layer tables.
    - Only the current SCD Type 2 record is exposed for each dimension.
    - Business-friendly column names are provided where needed.
    - Foreign keys are retained for relationships with fact views.
    - Related employee attributes are used to enrich the doctor dimension.
    - Views provide an analytical layer without duplicating Silver data.

Source:
    healthone_lakehouse.silver

Target:
    healthone_lakehouse.gold

===============================================================================
*/

USE CATALOG healthone_lakehouse;


-- =============================================================================
-- Dimension: Hospitals
-- =============================================================================

CREATE OR REPLACE VIEW healthone_lakehouse.gold.dim_hospitals AS

SELECT
    hospital_id,
    name AS hospital_name,
    address,
    city,
    region,
    capacity,
    opened_date AS established_date
FROM healthone_lakehouse.silver.hospitals
WHERE is_current = 1;


-- =============================================================================
-- Dimension: Departments
-- =============================================================================

CREATE OR REPLACE VIEW healthone_lakehouse.gold.dim_departments AS

SELECT
    department_id,
    name AS department_name,
    hospital_id,
    created_at AS department_created_at,
    updated_at AS department_updated_at
FROM healthone_lakehouse.silver.departments
WHERE is_current = 1;


-- =============================================================================
-- Dimension: Employees
-- =============================================================================

CREATE OR REPLACE VIEW healthone_lakehouse.gold.dim_employees AS

SELECT
    employee_id,
    name AS employee_name,
    dob,
    gender,
    address,
    phone,
    email,
    role,
    department_id,
    hospital_id,
    hire_date,
    salary,
    status AS employment_status
FROM healthone_lakehouse.silver.employees
WHERE is_current = 1;


-- =============================================================================
-- Dimension: Doctors
-- =============================================================================

CREATE OR REPLACE VIEW healthone_lakehouse.gold.dim_doctors AS

SELECT
    d.doctor_id,
    d.employee_id,
    d.specialization,
    e.name AS doctor_name,
    e.gender,
    e.phone AS doctor_phone,
    e.email AS doctor_email,
    d.hospital_id,
    e.department_id,
    e.hire_date,
    e.status AS employment_status
FROM healthone_lakehouse.silver.doctors AS d
LEFT JOIN healthone_lakehouse.silver.employees AS e
    ON d.employee_id = e.employee_id
    AND e.is_current = 1
WHERE d.is_current = 1;


-- =============================================================================
-- Dimension: Patients
-- =============================================================================

CREATE OR REPLACE VIEW healthone_lakehouse.gold.dim_patients AS

SELECT
    patient_id,
    concat_ws(' ', first_name, last_name) AS patient_name,
    dob,
    gender,
    phone,
    address,
    email,
    blood_group,
    hospital_id
FROM healthone_lakehouse.silver.patients
WHERE is_current = 1;
