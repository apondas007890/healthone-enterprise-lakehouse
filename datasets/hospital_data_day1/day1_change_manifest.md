# Day 1 Data Quality Issue Manifest

**Operational Date:** 2026-08-02
**Baseline:** Day 0 (2026-08-01)

---

## 1. Change Summary

| Table | INSERT | UPDATE | ID Range |
|-------|--------|--------|----------|
| hospitals | 1 | 1 | 1-3 |
| departments | 1 | 1 | 1-7 |
| employees | 2 | 3 | 1-14 |
| doctors | 1 | 1 | 1-7 |
| payroll | 2 | 1 | 1-14 |
| patients | 6 | 2 | 1-6 |
| appointments | 8 | 3 | 1-8 |
| admissions | 3 | 1 | 1-3 |
| billing | 5 | 2 | 1-5 |

---

## 2. Data Quality Issues

| Table | Column | Issue | ID(s) |
|-------|--------|-------|-------|
| hospitals | `name`, `city` | Trailing whitespace | 3 |
| departments | `name` | Leading/trailing whitespace | 7 |
| employees | `gender` | Inconsistent (male, MALE, F, Malee, female) | 2, 3, 4, 5, 7, 13, 14 |
| employees | `phone` | Missing leading zero / NULL | 11, 12 |
| employees | `email` | Malformed | 12 |
| employees | `status`, `address` | Leading/trailing whitespace | 11, 13 |
| employees | `role`, `salary`, `department` | SCD Type 2 changes | 2, 5, 8 |
| doctors | `specialization` | Leading/trailing spaces | 4, 7 |
| doctors | `specialization` | Inconsistent capitalization | 5 |
| patients | `gender` | Inconsistent (female, M, male) | 2, 3, 4 |
| patients | `dob` | Future date (2028) | 5 |
| patients | `address` | Leading/trailing whitespace | 3 |
| patients | `patients` | Duplicate-like | 1, 6 |
| appointments | `status` | Inconsistent (scheduled, SCHEDULED, Done) | 3, 4, 5 |
| appointments | `hospital_id` | Doctor/hospital mismatch | 6 |
| appointments | `appointment` | Duplicate-like | 1, 8 |
| admissions | `status` + `discharge_datetime` | Business-rule violation | 3 |
| billing | `insurance_covered` | NULL / Greater than amount | 4, 5 |
| billing | `admission_id` | NULL (no admission) | 4 |
| payroll | `net_pay` | Correction | 2 |

---

## 3. CDC / Watermark

All Day 1 changes use timestamps **2026-08-02**.

- Every INSERT has `created_at` and `updated_at` = Day 1
- Every UPDATE changes only `updated_at`
- Incremental extraction: `WHERE updated_at > @watermark`

---

## 4. Employee SCD Type 2 Test Cases

| Employee | Day 0 State | Day 1 Change | SCD2 Purpose |
|----------|-------------|--------------|--------------|
| 2 | Nurse / 45,000 | Senior Nurse / 48,000 | Role + salary change |
| 5 | Department 1 | Department 2 | Department transfer |
| 8 | On Leave | Active | Status change |

---

## 5. Expected Day 1 ID State

| Table | Previous Max | New IDs | New Max |
|-------|-------------|---------|---------|
| hospitals | 2 | 3 | **3** |
| departments | 6 | 7 | **7** |
| employees | 12 | 13-14 | **14** |
| doctors | 6 | 7 | **7** |
| payroll | 12 | 13-14 | **14** |
| patients | 0 | 1-6 | **6** |
| appointments | 0 | 1-8 | **8** |
| admissions | 0 | 1-3 | **3** |
| billing | 0 | 1-5 | **5** |