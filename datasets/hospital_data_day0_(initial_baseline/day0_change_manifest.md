# Day 0 Data Quality Manifest

| Table | Column | Issue |
|-------|--------|-------|
| employees | gender | Malee invalid value |
| employees | gender | inconsistent male, MALE, F, Male |
| employees | phone | missing phone |
| employees | phone | missing leading zero |
| employees | email | malformed mim@ |
| employees | status | whitespace |
| doctors | specialization | leading/trailing spaces |
| doctors | specialization | inconsistent capitalization |
| patients | gender | inconsistent representations |
| patients | phone | NULL |
| patients | phone | invalid format |
| patients | dob | impossible age |
| patients | patients | duplicate-like patient |
| appointments | status | inconsistent capitalization |
| appointments | status | invalid Done |
| appointments | appointment | duplicate-like appointment |
| appointments | hospital_id | doctor/hospital mismatch |
| admissions | status | invalid discharge combination |
| admissions | discharge_datetime | invalid lifecycle |
| billing | amount | negative amount |
| billing | insurance_covered | NULL |
| billing | insurance_covered | greater than billing amount |
| payroll | net_pay | incorrect calculation |


# Current Maximum ID Values by Table

| Table        | Current Maximum ID |
| ------------ | -----------------: |
| hospitals    |                2   |
| departments  |                6   |
| employees    |               12   |
| doctors      |                6   |
| payroll      |               12   |
| patients     |               11   |
| appointments |               15   |
| admissions   |                7   |
| billing      |                7   |
