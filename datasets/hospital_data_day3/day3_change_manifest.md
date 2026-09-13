# Day 3 Data Quality Issue Manifest

**Operational Date:** 2026-08-04
**Baseline:** Day 2 (2026-08-03)

---

## 1. Change Summary

| Table | INSERT | UPDATE | ID Range |
|-------|--------|--------|----------|
| hospitals | 1 | 2 | 5 |
| departments | 2 | 2 | 9-10 |
| employees | 4 | 3 | 18-21 |
| doctors | 2 | 2 | 9-10 |
| payroll | 4 | 2 | 19-22 |
| patients | 6 | 3 | 12-17 |
| appointments | 6 | 3 | 15-20 |
| admissions | 4 | 2 | 8-11 |
| billing | 5 | 2 | 11-15 |

---

## 2. Data Quality Issues

| Table | Column | Issue | ID(s) |
|-------|--------|-------|-------|
| hospitals | `name` | Trailing whitespace | 5 |
| departments | `name` | Trailing whitespace | 2 |
| employees | `gender` | Inconsistent (male, F) | 19, 20 |
| employees | `status` | Active/Resigned change | 8 |
| employees | `phone` | Missing leading zero | 21 |
| employees | `email` | Invalid format | 19 |
| doctors | `specialization` | Inconsistent capitalization | 7, 8 |
| patients | `gender` | Inconsistent (male, M) | 13, 14 |
| patients | `address` | Leading/trailing whitespace | 14 |
| patients | `patients` | Duplicate-like | 12, 17 |
| appointments | `status` | Inconsistent (scheduled, SCHEDULED, Done) | 17, 18, 19 |
| appointments | `appointment` | Duplicate-like | 15, 20 |
| admissions | `status` + `discharge` | Business-rule violation | 11 |
| billing | `insurance_covered` | > amount | 13 |
| billing | `insurance_covered` | NULL | 14 |
| payroll | `net_pay` | Incorrect calculation | 21 |

---

## 3. CDC / Watermark

All Day 3 changes use timestamps **2026-08-04**.

- Every INSERT has `created_at` and `updated_at` = Day 3
- Every UPDATE changes only `updated_at`
- Incremental extraction: `WHERE updated_at > @watermark`

---

## 4. Expected Day 3 ID State

| Table | Previous Max | New IDs | New Max |
|-------|-------------|---------|---------|
| hospitals | 4 | 5 | **5** |
| departments | 8 | 9-10 | **10** |
| employees | 17 | 18-21 | **21** |
| doctors | 8 | 9-10 | **10** |
| payroll | 18 | 19-22 | **22** |
| patients | 11 | 12-17 | **17** |
| appointments | 14 | 15-20 | **20** |
| admissions | 7 | 8-11 | **11** |
| billing | 10 | 11-15 | **15** |