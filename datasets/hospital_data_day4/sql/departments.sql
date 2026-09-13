-- ============================================================
-- DAY 4 — TABLE: departments
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new departments
INSERT INTO departments
    (department_id, name, hospital_id, created_at, updated_at)
VALUES
    (11, 'Nephrology', 6, '2026-08-05 09:00:00', '2026-08-05 09:00:00'),
    (12, 'Urology', 6, '2026-08-05 09:05:00', '2026-08-05 09:05:00'),
    (13, ' Gastroenterology', 1, '2026-08-05 09:10:00', '2026-08-05 09:10:00');

-- Day 4 department updates
UPDATE departments
SET
    name = 'Pediatrics ',
    updated_at = '2026-08-05 10:00:00'
WHERE department_id = 4;

UPDATE departments
SET
    name = 'Orthopedic Surgery',
    updated_at = '2026-08-05 10:30:00'
WHERE department_id = 5;