# Day 2 Data Quality Issue Manifest

**Operational Date:** 2026-08-03
**Baseline:** Day 1 (2026-08-02)

---

## 1. Change Summary

| Table | INSERT | UPDATE | ID Range |
|-------|--------|--------|----------|
| hospitals | 1 | 1 | 4 |
| departments | 1 | 2 | 8 |
| employees | 3 | 2 | 15-17 |
| doctors | 1 | 2 | 8 |
| payroll | 4 | 2 | 15-18 |
| patients | 5 | 3 | 7-11 |
| appointments | 6 | 2 | 9-14 |
| admissions | 4 | 2 | 4-7 |
| billing | 5 | 2 | 6-10 |

---

## 2. Data Quality Issues

| Table | Column | Issue | ID(s) |
|-------|--------|-------|-------|
| hospitals | `name` | Trailing whitespace | 4 |
| departments | `name` | Leading whitespace | 8 |
| employees | `gender` | Inconsistent (Female, MALE) | 15, 17 |
| employees | `email` | Invalid format | 16 |
| employees | `status` | Leading/trailing | 15 |
| doctors | `specialization` | Leading/trailing | 8 |
| patients | `gender` | Inconsistent (male, M, MALE) | 7, 8, 9 |
| patients | `phone` | Missing leading zero | 10 |
| patients | `patients` | Duplicate-like | 7, 11 |
| appointments | `status` | Inconsistent (completed, SCHEDULED, Done) | 10, 11, 13 |
| appointments | `appointment` | Duplicate-like | 9, 14 |
| admissions | `status` + `discharge` | Business-rule violation | 7 |
| billing | `insurance_covered` | > amount | 9 |
| billing | `insurance_covered` | NULL | 10 |
| payroll | `net_pay` | Incorrect calculation | 15, 16 |

---

## 3. CDC / Watermark

All Day 2 changes use timestamps **2026-08-03**.

- Every INSERT has `created_at` and `updated_at` = Day 2
- Every UPDATE changes only `updated_at`
- Incremental extraction: `WHERE updated_at > @watermark`

---

## 4. Expected Day 2 ID State

| Table | Previous Max | New IDs | New Max |
|-------|-------------|---------|---------|
| hospitals | 3 | 4 | **4** |
| departments | 7 | 8 | **8** |
| employees | 14 | 15-17 | **17** |
| doctors | 7 | 8 | **8** |
| payroll | 14 | 15-18 | **18** |
| patients | 6 | 7-11 | **11** |
| appointments | 8 | 9-14 | **14** |
| admissions | 3 | 4-7 | **7** |
| billing | 5 | 6-10 | **10** |