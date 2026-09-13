-- ============================================================
-- DAY 3 — TABLE: doctors
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new doctors
INSERT INTO doctors
    (doctor_id, specialization, employee_id, hospital_id, created_at, updated_at)
VALUES
    (9, 'Neonatology', 18, 5, '2026-08-04 09:00:00', '2026-08-04 09:00:00'),
    (10, 'ENT', 19, 5, '2026-08-04 09:05:00', '2026-08-04 09:05:00');

-- Day 3 doctor updates
UPDATE doctors
SET
    specialization = 'General Medicine',
    updated_at = '2026-08-04 10:00:00'
WHERE doctor_id = 7;

UPDATE doctors
SET
    specialization = 'Neurology',
    updated_at = '2026-08-04 10:30:00'
WHERE doctor_id = 8;