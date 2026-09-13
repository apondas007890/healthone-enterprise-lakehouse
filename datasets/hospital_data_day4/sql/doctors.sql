-- ============================================================
-- DAY 4 — TABLE: doctors
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new doctors
INSERT INTO doctors
    (doctor_id, specialization, employee_id, hospital_id, created_at, updated_at)
VALUES
    (11, 'Nephrology', 22, 6, '2026-08-05 09:00:00', '2026-08-05 09:00:00'),
    (12, 'Urology', 23, 6, '2026-08-05 09:05:00', '2026-08-05 09:05:00'),
    (13, 'Gastroenterology', 24, 1, '2026-08-05 09:10:00', '2026-08-05 09:10:00');

-- Day 4 doctor updates
UPDATE doctors
SET
    specialization = 'Pediatric Cardiology',
    updated_at = '2026-08-05 10:00:00'
WHERE doctor_id = 3;

UPDATE doctors
SET
    specialization = 'Orthopedic Surgery',
    updated_at = '2026-08-05 10:30:00'
WHERE doctor_id = 4;