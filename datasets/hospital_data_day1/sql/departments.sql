-- DAY 1 — TABLE: departments
-- Date: 2026-08-02


INSERT INTO departments
    (department_id, name, hospital_id, created_at, updated_at)
VALUES
    -- Day 0 departments (baseline)
    (1, 'Emergency', 1, '2026-08-01 08:10:00', '2026-08-01 08:10:00'),
    (2, 'Cardiology', 1, '2026-08-01 08:11:00', '2026-08-01 08:11:00'),
    (3, ' Medicine', 1, '2026-08-01 08:12:00', '2026-08-01 08:12:00'),
    (4, 'Pediatrics', 2, '2026-08-01 08:13:00', '2026-08-01 08:13:00'),
    (5, 'Orthopedics', 2, '2026-08-01 08:14:00', '2026-08-01 08:14:00'),
    (6, 'Radiology', 2, '2026-08-01 08:15:00', '2026-08-01 08:15:00'),
    -- Day 1 new department
    (7, ' Neurology ', 3, '2026-08-02 09:00:00', '2026-08-02 09:00:00');


-- Day 1 department update
UPDATE departments
SET
    name = 'General Medicine',
    updated_at = '2026-08-02 09:30:00'
WHERE department_id = 3;