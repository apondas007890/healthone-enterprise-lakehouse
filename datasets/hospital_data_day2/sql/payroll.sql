-- DAY 2 — TABLE: payroll
-- Date: 2026-08-03


-- Day 2 new payroll
INSERT INTO payroll
    (payroll_id, employee_id, pay_period, gross_pay, deductions, net_pay, paid_date, created_at, updated_at)
VALUES
    (15, 15, '2026-08', 38000.00, 3800.00, 45000.00, '2026-08-03', '2026-08-03 10:00:00', '2026-08-03 10:00:00'),
    (16, 16, '2026-08', 45000.00, 4500.00, 39000.00, '2026-08-03', '2026-08-03 10:05:00', '2026-08-03 10:05:00'),
    (17, 17, '2026-08', 42000.00, 4200.00, 37800.00, '2026-08-03', '2026-08-03 10:10:00', '2026-08-03 10:10:00'),
    (18, 15, '2026-08', 38000.00, 3800.00, 34200.00, '2026-08-03', '2026-08-03 10:15:00', '2026-08-03 10:15:00');

-- Day 2 payroll updates
UPDATE payroll
SET
    net_pay = 43200.00,
    updated_at = '2026-08-03 11:00:00'
WHERE payroll_id = 3;

UPDATE payroll
SET
    net_pay = 46800.00,
    updated_at = '2026-08-03 11:15:00'
WHERE payroll_id = 4;