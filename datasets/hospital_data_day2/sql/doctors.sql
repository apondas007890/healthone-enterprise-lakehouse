-- DAY 2 — TABLE: doctors
-- Date: 2026-08-03


-- Day 2 new doctor
INSERT INTO doctors
    (doctor_id, specialization, employee_id, hospital_id, created_at, updated_at)
VALUES
    (8, ' Neurology ', 15, 3, '2026-08-03 09:00:00', '2026-08-03 09:00:00');

-- Day 2 doctor updates
UPDATE doctors
SET
    specialization = 'Cardiology',
    updated_at = '2026-08-03 10:00:00'
WHERE doctor_id = 2;

UPDATE doctors
SET
    specialization = 'Orthopedics',
    updated_at = '2026-08-03 10:30:00'
WHERE doctor_id = 6;