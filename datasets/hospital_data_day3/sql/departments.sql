-- ============================================================
-- DAY 3 — TABLE: departments
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new departments
INSERT INTO departments
    (department_id, name, hospital_id, created_at, updated_at)
VALUES
    (9, 'Neonatology', 5, '2026-08-04 09:00:00', '2026-08-04 09:00:00'),
    (10, 'ENT', 5, '2026-08-04 09:05:00', '2026-08-04 09:05:00');

-- Day 3 department updates
UPDATE departments
SET
    name = 'Cardiology ',
    updated_at = '2026-08-04 10:00:00'
WHERE department_id = 2;

UPDATE departments
SET
    name = 'Radiology & Imaging',
    updated_at = '2026-08-04 10:30:00'
WHERE department_id = 6;