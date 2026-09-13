-- DAY 2 — TABLE: departments
-- Date: 2026-08-03


-- Day 2 new department
INSERT INTO departments
    (department_id, name, hospital_id, created_at, updated_at)
VALUES
    (8, ' Dermatology', 4, '2026-08-03 09:00:00', '2026-08-03 09:00:00');

-- Day 2 department updates
UPDATE departments
SET
    name = 'Orthopedics ',
    updated_at = '2026-08-03 10:00:00'
WHERE department_id = 5;

UPDATE departments
SET
    name = 'Gynecology',
    updated_at = '2026-08-03 10:30:00'
WHERE department_id = 7;