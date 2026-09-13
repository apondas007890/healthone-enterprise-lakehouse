-- DAY 1 — TABLE: doctors
-- Date: 2026-08-02


-- Day 0 doctors (baseline)
INSERT INTO doctors
    (doctor_id, specialization, employee_id, hospital_id, created_at, updated_at)
VALUES
    (1, 'Cardiology', 4, 1, '2026-08-01 08:35:00', '2026-08-01 08:35:00'),
    (2, 'Neurology', 3, 2, '2026-08-01 08:36:00', '2026-08-01 08:36:00'),
    (3, 'Pediatrics', 6, 2, '2026-08-01 08:37:00', '2026-08-01 08:37:00'),
    (4, ' Orthopedics ', 9, 2, '2026-08-01 08:38:00', '2026-08-01 08:38:00'),
    (5, 'GENERAL MEDICINE', 1, 1, '2026-08-01 08:39:00', '2026-08-01 08:39:00'),
    (6, 'Dermatology', 5, 1, '2026-08-01 08:40:00', '2026-08-01 08:40:00'),
    -- Day 1 new doctor
    (7, 'Cardiology ', 13, 1, '2026-08-02 10:00:00', '2026-08-02 10:00:00');


-- Day 1 doctor update
UPDATE doctors
SET
    specialization = 'Orthopedics',
    updated_at = '2026-08-02 10:30:00'
WHERE doctor_id = 4;