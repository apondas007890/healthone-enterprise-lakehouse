# Data Catalog for Gold Layer

## Overview

The Gold Layer is the business-level data representation of the HealthOne Enterprise Lakehouse. It is designed to support analytical and reporting use cases.

The Gold Layer follows a **star schema** structure and contains:

* **5 Dimension Views** for descriptive information
* **4 Fact Views** for business events and measurements

All Gold views are created from the cleaned and historized **Silver Layer** tables. Only the current **SCD Type 2** records are exposed in the Gold Layer.

---

# Dimension Views

## 1. `healthone_lakehouse.gold.dim_hospitals`

* **Purpose:** Stores hospital information used to describe and analyze hospital operations.
* **Source:** `healthone_lakehouse.silver.hospitals`
* **SCD Type 2:** Only current records are included.

### Columns

| Column Name        | Data Type | Description                                                    |
| ------------------ | --------- | -------------------------------------------------------------- |
| `hospital_id`      | INT       | Unique identifier assigned to each hospital.                   |
| `hospital_name`    | STRING    | Name of the hospital. Renamed from `name` in the Silver layer. |
| `address`          | STRING    | Full address of the hospital.                                  |
| `city`             | STRING    | City where the hospital is located.                            |
| `region`           | STRING    | Region or geographical area where the hospital is located.     |
| `capacity`         | INT       | Number of patients or beds the hospital can accommodate.       |
| `established_date` | DATE      | Date when the hospital was opened or established.              |

---

## 2. `healthone_lakehouse.gold.dim_departments`

* **Purpose:** Stores department information and its relationship with hospitals.
* **Source:** `healthone_lakehouse.silver.departments`
* **SCD Type 2:** Only current records are included.

### Columns

| Column Name             | Data Type | Description                                                      |
| ----------------------- | --------- | ---------------------------------------------------------------- |
| `department_id`         | INT       | Unique identifier assigned to each department.                   |
| `department_name`       | STRING    | Name of the department. Renamed from `name` in the Silver layer. |
| `hospital_id`           | INT       | Identifier of the hospital where the department belongs.         |
| `department_created_at` | TIMESTAMP | Date and time when the department record was created.            |
| `department_updated_at` | TIMESTAMP | Date and time when the department record was last updated.       |

---

## 3. `healthone_lakehouse.gold.dim_employees`

* **Purpose:** Stores employee information used for HR and hospital workforce analysis.
* **Source:** `healthone_lakehouse.silver.employees`
* **SCD Type 2:** Only current employee records are included.

### Columns

| Column Name         | Data Type | Description                                                    |
| ------------------- | --------- | -------------------------------------------------------------- |
| `employee_id`       | INT       | Unique identifier assigned to each employee.                   |
| `employee_name`     | STRING    | Employee's full name. Renamed from `name` in the Silver layer. |
| `dob`               | DATE      | Employee's date of birth.                                      |
| `gender`            | STRING    | Gender of the employee.                                        |
| `address`           | STRING    | Employee's address.                                            |
| `phone`             | STRING    | Employee's phone number.                                       |
| `email`             | STRING    | Employee's email address.                                      |
| `role`              | STRING    | Job role or position of the employee.                          |
| `department_id`     | INT       | Identifier of the department where the employee works.         |
| `hospital_id`       | INT       | Identifier of the hospital where the employee works.           |
| `hire_date`         | DATE      | Date when the employee joined the organization.                |
| `salary`            | DECIMAL   | Current salary of the employee.                                |
| `employment_status` | STRING    | Current employment status of the employee.                     |

---

## 4. `healthone_lakehouse.gold.dim_doctors`

* **Purpose:** Stores doctor information enriched with related employee details.
* **Source:** `healthone_lakehouse.silver.doctors` and `healthone_lakehouse.silver.employees`
* **SCD Type 2:** Only current doctor records and current employee records are included.

The doctor dimension uses the employee table to enrich doctor records with contact, department, hospital, and employment information.

### Columns

| Column Name         | Data Type | Description                                                      |
| ------------------- | --------- | ---------------------------------------------------------------- |
| `doctor_id`         | INT       | Unique identifier assigned to each doctor.                       |
| `employee_id`       | INT       | Identifier linking the doctor to the employee record.            |
| `specialization`    | STRING    | Medical specialization of the doctor.                            |
| `doctor_name`       | STRING    | Full name of the doctor. Taken from the related employee record. |
| `gender`            | STRING    | Gender of the doctor.                                            |
| `doctor_phone`      | STRING    | Phone number of the doctor.                                      |
| `doctor_email`      | STRING    | Email address of the doctor.                                     |
| `hospital_id`       | INT       | Identifier of the hospital where the doctor works.               |
| `department_id`     | INT       | Identifier of the department where the doctor works.             |
| `hire_date`         | DATE      | Date when the doctor joined the organization.                    |
| `employment_status` | STRING    | Current employment status of the doctor.                         |

---

## 5. `healthone_lakehouse.gold.dim_patients`

* **Purpose:** Stores patient information used to analyze patient activity and healthcare operations.
* **Source:** `healthone_lakehouse.silver.patients`
* **SCD Type 2:** Only current patient records are included.

### Columns

| Column Name    | Data Type | Description                                                 |
| -------------- | --------- | ----------------------------------------------------------- |
| `patient_id`   | INT       | Unique identifier assigned to each patient.                 |
| `patient_name` | STRING    | Full patient name created by combining first and last name. |
| `dob`          | DATE      | Patient's date of birth.                                    |
| `gender`       | STRING    | Gender of the patient.                                      |
| `phone`        | STRING    | Patient's phone number.                                     |
| `address`      | STRING    | Patient's address.                                          |
| `email`        | STRING    | Patient's email address.                                    |
| `blood_group`  | STRING    | Patient's blood group.                                      |
| `hospital_id`  | INT       | Identifier of the hospital associated with the patient.     |

---

# Fact Views

## 6. `healthone_lakehouse.gold.fact_appointments`

* **Purpose:** Stores patient appointment events for operational and analytical reporting.
* **Source:** `healthone_lakehouse.silver.appointments`
* **SCD Type 2:** Only the current appointment record is included.

Date attributes are derived from `appointment_datetime` to make time-based reporting easier.

### Columns

| Column Name               | Data Type | Description                                                   |
| ------------------------- | --------- | ------------------------------------------------------------- |
| `appointment_id`          | INT       | Unique identifier assigned to each appointment.               |
| `patient_id`              | INT       | Identifier of the patient associated with the appointment.    |
| `doctor_id`               | INT       | Identifier of the doctor associated with the appointment.     |
| `hospital_id`             | INT       | Identifier of the hospital where the appointment takes place. |
| `appointment_datetime`    | TIMESTAMP | Date and time of the appointment.                             |
| `appointment_date`        | DATE      | Date of the appointment derived from `appointment_datetime`.  |
| `appointment_year`        | INT       | Year of the appointment.                                      |
| `appointment_month`       | INT       | Month of the appointment.                                     |
| `appointment_day`         | INT       | Day of the month when the appointment takes place.            |
| `appointment_day_of_week` | INT       | Day of the week of the appointment.                           |
| `status`                  | STRING    | Current status of the appointment.                            |
| `reason`                  | STRING    | Reason or purpose of the appointment.                         |

---

## 7. `healthone_lakehouse.gold.fact_admissions`

* **Purpose:** Stores patient admission events and their current lifecycle status.
* **Source:** `healthone_lakehouse.silver.admissions`
* **SCD Type 2:** Only the current admission record is included.

The view also calculates the patient's length of stay and whether the patient is currently admitted.

### Columns

| Column Name           | Data Type | Description                                                                                                 |
| --------------------- | --------- | ----------------------------------------------------------------------------------------------------------- |
| `admission_id`        | INT       | Unique identifier assigned to each admission.                                                               |
| `patient_id`          | INT       | Identifier of the admitted patient.                                                                         |
| `hospital_id`         | INT       | Identifier of the hospital where the patient was admitted.                                                  |
| `admit_datetime`      | TIMESTAMP | Date and time when the patient was admitted.                                                                |
| `discharge_datetime`  | TIMESTAMP | Date and time when the patient was discharged. NULL when the patient has not been discharged.               |
| `admission_date`      | DATE      | Admission date derived from `admit_datetime`.                                                               |
| `discharge_date`      | DATE      | Discharge date derived from `discharge_datetime`.                                                           |
| `admission_year`      | INT       | Year of the admission.                                                                                      |
| `admission_month`     | INT       | Month of the admission.                                                                                     |
| `ward`                | STRING    | Ward where the patient was admitted.                                                                        |
| `bed_no`              | STRING    | Bed number assigned to the patient.                                                                         |
| `status`              | STRING    | Current status of the admission.                                                                            |
| `length_of_stay_days` | INT       | Number of days between admission and discharge. NULL when the patient is still admitted.                    |
| `currently_admitted`  | INT       | Indicates whether the patient is currently admitted. `1` means currently admitted and `0` means discharged. |

---

## 8. `healthone_lakehouse.gold.fact_billing`

* **Purpose:** Stores patient billing information for financial and healthcare revenue analysis.
* **Source:** `healthone_lakehouse.silver.billing`
* **SCD Type 2:** Only the current billing record is included.

The view includes calculated insurance and patient payable amounts.

### Columns

| Column Name                | Data Type | Description                                                                                   |
| -------------------------- | --------- | --------------------------------------------------------------------------------------------- |
| `bill_id`                  | INT       | Unique identifier assigned to each billing record.                                            |
| `admission_id`             | INT       | Identifier of the admission related to the bill.                                              |
| `patient_id`               | INT       | Identifier of the patient associated with the bill.                                           |
| `amount`                   | DECIMAL   | Total amount of the bill.                                                                     |
| `insurance_covered`        | DECIMAL   | Amount of the bill covered by insurance.                                                      |
| `insurance_covered_amount` | DECIMAL   | Insurance-covered amount with NULL values converted to `0`.                                   |
| `patient_payable_amount`   | DECIMAL   | Amount that the patient needs to pay after insurance coverage.                                |
| `insurance_amount_invalid` | INT       | Validation flag. `1` indicates that insurance coverage is greater than the total bill amount. |
| `payment_status`           | STRING    | Current payment status of the bill.                                                           |
| `bill_datetime`            | TIMESTAMP | Date and time when the bill was created.                                                      |
| `billing_date`             | DATE      | Billing date derived from `bill_datetime`.                                                    |
| `billing_year`             | INT       | Year when the bill was created.                                                               |
| `billing_month`            | INT       | Month when the bill was created.                                                              |

---

## 9. `healthone_lakehouse.gold.fact_payroll`

* **Purpose:** Stores employee payroll information for HR and financial reporting.
* **Source:** `healthone_lakehouse.silver.payroll`
* **SCD Type 2:** Only the current payroll record is included.

### Columns

| Column Name     | Data Type | Description                                               |
| --------------- | --------- | --------------------------------------------------------- |
| `payroll_id`    | INT       | Unique identifier assigned to each payroll record.        |
| `employee_id`   | INT       | Identifier of the employee receiving the payroll payment. |
| `pay_period`    | DATE      | Payroll period associated with the payment.               |
| `gross_pay`     | DECIMAL   | Total employee earnings before deductions.                |
| `deductions`    | DECIMAL   | Total deductions applied to the employee's gross pay.     |
| `net_pay`       | DECIMAL   | Final amount paid to the employee after deductions.       |
| `paid_date`     | DATE      | Date when the payroll payment was made.                   |
| `payment_year`  | INT       | Year when the payroll was paid.                           |
| `payment_month` | INT       | Month when the payroll was paid.                          |

---

# Gold Layer Relationships

The Gold Layer follows a star-schema style design where fact views connect to descriptive dimension views through business keys.

### Main Relationships

| Fact View           | Dimension         | Relationship    |
| ------------------- | ----------------- | --------------- |
| `fact_appointments` | `dim_patients`    | `patient_id`    |
| `fact_appointments` | `dim_doctors`     | `doctor_id`     |
| `fact_appointments` | `dim_hospitals`   | `hospital_id`   |
| `fact_admissions`   | `dim_patients`    | `patient_id`    |
| `fact_admissions`   | `dim_hospitals`   | `hospital_id`   |
| `fact_billing`      | `fact_admissions` | `admission_id`  |
| `fact_billing`      | `dim_patients`    | `patient_id`    |
| `fact_payroll`      | `dim_employees`   | `employee_id`   |
| `dim_doctors`       | `dim_employees`   | `employee_id`   |
| `dim_departments`   | `dim_hospitals`   | `hospital_id`   |
| `dim_employees`     | `dim_departments` | `department_id` |
| `dim_employees`     | `dim_hospitals`   | `hospital_id`   |

---

# Gold Layer Summary

| Type      | Object              | Main Purpose                              |
| --------- | ------------------- | ----------------------------------------- |
| Dimension | `dim_hospitals`     | Hospital information                      |
| Dimension | `dim_departments`   | Department information                    |
| Dimension | `dim_doctors`       | Doctor and specialization information     |
| Dimension | `dim_employees`     | Employee and workforce information        |
| Dimension | `dim_patients`      | Patient information                       |
| Fact      | `fact_appointments` | Patient appointment events                |
| Fact      | `fact_admissions`   | Patient admission events                  |
| Fact      | `fact_billing`      | Patient billing and insurance information |
| Fact      | `fact_payroll`      | Employee payroll information              |

The Gold Layer provides a clean analytical interface over the Silver Layer without duplicating the underlying Silver data. It is designed to make healthcare operations, patient activity, hospital performance, billing, and HR/payroll data easier to query and use for reporting.
