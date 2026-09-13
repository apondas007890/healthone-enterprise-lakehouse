-- ============================================================
-- DAY 4 — TABLE: admissions
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new admissions (IDs start from 12)
INSERT INTO admissions
    (admission_id, patient_id, hospital_id, admit_datetime, discharge_datetime, ward, bed_no, status, created_at, updated_at)
VALUES
    (12, 18, 6, '2026-08-05 08:00:00', NULL, 'General Ward', 'G-501', 'Admitted', '2026-08-05 07:00:00', '2026-08-05 07:00:00'),
    (13, 20, 1, '2026-08-05 09:00:00', '2026-08-05 18:00:00', 'Gastroenterology', 'G-101', 'Discharged', '2026-08-05 07:05:00', '2026-08-05 07:05:00'),
    (14, 21, 5, '2026-08-05 10:00:00', NULL, 'Neonatology', 'N-102', 'Admitted', '2026-08-05 07:10:00', '2026-08-05 07:10:00'),
    (15, 22, 2, '2026-08-05 11:00:00', '2026-08-05 16:30:00', 'Orthopedics', 'O-201', 'Admitted', '2026-08-05 07:15:00', '2026-08-05 07:15:00');

-- Day 4 admission updates
UPDATE admissions
SET
    discharge_datetime = '2026-08-05 20:00:00',
    status = 'Discharged',
    updated_at = '2026-08-05 20:05:00'
WHERE admission_id = 8;

UPDATE admissions
SET
    discharge_datetime = '2026-08-05 17:00:00',
    status = 'Discharged',
    updated_at = '2026-08-05 17:05:00'
WHERE admission_id = 14;