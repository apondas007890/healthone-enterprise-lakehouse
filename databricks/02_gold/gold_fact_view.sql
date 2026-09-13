/*
===============================================================================
                       Gold Layer - Fact Views
===============================================================================

Purpose:
    Creates the Gold-layer fact views for the HealthOne analytical
    star schema.

Facts:
    - fact_appointments
    - fact_admissions
    - fact_billing
    - fact_payroll

Design:
    - Built from the cleaned and historized Silver-layer tables.
    - Only the current SCD Type 2 record is exposed for each fact.
    - Date-related attributes are derived for analytical reporting.
    - Business calculations are added where required.
    - Views provide an analytical layer without duplicating Silver data.

Source:
    healthone_lakehouse.silver

Target:
    healthone_lakehouse.gold

===============================================================================
*/

USE CATALOG healthone_lakehouse;


-- =============================================================================
-- Fact: Appointments
-- =============================================================================
-- Represents patient appointment events and their current status.

CREATE OR REPLACE VIEW healthone_lakehouse.gold.fact_appointments AS

SELECT
    appointment_id,
    patient_id,
    doctor_id,
    hospital_id,
    appointment_datetime,
    CAST(appointment_datetime AS DATE) AS appointment_date,
    YEAR(appointment_datetime) AS appointment_year,
    MONTH(appointment_datetime) AS appointment_month,
    DAYOFMONTH(appointment_datetime) AS appointment_day,
    DAYOFWEEK(appointment_datetime) AS appointment_day_of_week,
    status,
    reason
FROM healthone_lakehouse.silver.appointments
WHERE is_current = 1;


-- =============================================================================
-- Fact: Admissions
-- =============================================================================
-- Represents patient admission events and their current lifecycle status.
-- Length of stay and current admission status are derived for analysis.

CREATE OR REPLACE VIEW healthone_lakehouse.gold.fact_admissions AS

SELECT
    admission_id,
    patient_id,
    hospital_id,
    admit_datetime,
    discharge_datetime,
    CAST(admit_datetime AS DATE) AS admission_date,
    CAST(discharge_datetime AS DATE) AS discharge_date,
    YEAR(admit_datetime) AS admission_year,
    MONTH(admit_datetime) AS admission_month,
    ward,
    bed_no,
    status,
    CASE
        WHEN discharge_datetime IS NOT NULL
        THEN DATEDIFF(
            CAST(discharge_datetime AS DATE),
            CAST(admit_datetime AS DATE)
        )
        ELSE NULL
    END AS length_of_stay_days,
    CASE
        WHEN discharge_datetime IS NULL THEN 1
        ELSE 0
    END AS currently_admitted
FROM healthone_lakehouse.silver.admissions
WHERE is_current = 1;


-- =============================================================================
-- Fact: Billing
-- =============================================================================
-- Represents billing records and their current payment status.
-- Insurance and patient payable amounts are derived for analysis.

CREATE OR REPLACE VIEW healthone_lakehouse.gold.fact_billing AS

SELECT
    bill_id,
    admission_id,
    patient_id,
    amount,
    insurance_covered,
    COALESCE(
        insurance_covered,
        CAST(0 AS DECIMAL(18,2))
    ) AS insurance_covered_amount,
    amount
        - COALESCE(
            insurance_covered,
            CAST(0 AS DECIMAL(18,2))
        ) AS patient_payable_amount,
    CASE
        WHEN insurance_covered IS NULL THEN 0
        WHEN insurance_covered > amount THEN 1
        ELSE 0
    END AS insurance_amount_invalid,
    payment_status,
    bill_datetime,
    CAST(bill_datetime AS DATE) AS billing_date,
    YEAR(bill_datetime) AS billing_year,
    MONTH(bill_datetime) AS billing_month
FROM healthone_lakehouse.silver.billing
WHERE is_current = 1;


-- =============================================================================
-- Fact: Payroll
-- =============================================================================
-- Represents employee payroll records and current salary payments.

CREATE OR REPLACE VIEW healthone_lakehouse.gold.fact_payroll AS

SELECT
    payroll_id,
    employee_id,
    pay_period,
    gross_pay,
    deductions,
    net_pay,
    paid_date,
    YEAR(paid_date) AS payment_year,
    MONTH(paid_date) AS payment_month
FROM healthone_lakehouse.silver.payroll
WHERE is_current = 1;
