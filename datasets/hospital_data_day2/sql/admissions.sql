-- DAY 2 — TABLE: admissions
-- Date: 2026-08-03


-- Day 2 new admissions (NO Day 0/1 data, IDs start from 4)
INSERT INTO admissions
    (admission_id, patient_id, hospital_id, admit_datetime, discharge_datetime, ward, bed_no, status, created_at, updated_at)
VALUES
    (4, 7, 4, '2026-08-03 08:00:00', NULL, 'General Ward', 'G-401', 'Admitted', '2026-08-03 07:00:00', '2026-08-03 07:00:00'),
    (5, 8, 1, '2026-08-03 09:00:00', '2026-08-03 17:00:00', 'Cardiology', 'C-201', 'Discharged', '2026-08-03 07:05:00', '2026-08-03 07:05:00'),
    (6, 9, 3, '2026-08-03 10:00:00', NULL, 'General Ward', 'G-302', 'Admitted', '2026-08-03 07:10:00', '2026-08-03 07:10:00'),
    (7, 10, 2, '2026-08-03 11:00:00', '2026-08-03 15:00:00', 'Pediatrics', 'P-102', 'Admitted', '2026-08-03 07:15:00', '2026-08-03 07:15:00');

-- Day 2 admission updates
UPDATE admissions
SET
    status = 'Discharged',
    discharge_datetime = '2026-08-03 20:00:00',
    updated_at = '2026-08-03 20:05:00'
WHERE admission_id = 4;

UPDATE admissions
SET
    discharge_datetime = '2026-08-03 18:00:00',
    updated_at = '2026-08-03 18:05:00'
WHERE admission_id = 6;