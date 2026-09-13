-- ============================================================
-- DAY 3 — TABLE: admissions
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new admissions (IDs start from 8)
INSERT INTO admissions
    (admission_id, patient_id, hospital_id, admit_datetime, discharge_datetime, ward, bed_no, status, created_at, updated_at)
VALUES
    (8, 12, 5, '2026-08-04 08:00:00', NULL, 'Neonatology', 'N-101', 'Admitted', '2026-08-04 07:00:00', '2026-08-04 07:00:00'),
    (9, 14, 1, '2026-08-04 09:00:00', '2026-08-04 17:00:00', 'Cardiology', 'C-301', 'Discharged', '2026-08-04 07:05:00', '2026-08-04 07:05:00'),
    (10, 15, 3, '2026-08-04 10:00:00', NULL, 'General Ward', 'G-303', 'Admitted', '2026-08-04 07:10:00', '2026-08-04 07:10:00'),
    (11, 16, 2, '2026-08-04 11:00:00', '2026-08-04 16:00:00', 'Orthopedics', 'O-102', 'Admitted', '2026-08-04 07:15:00', '2026-08-04 07:15:00');

-- Day 3 admission updates
UPDATE admissions
SET
    discharge_datetime = '2026-08-04 19:00:00',
    status = 'Discharged',
    updated_at = '2026-08-04 19:05:00'
WHERE admission_id = 6;

UPDATE admissions
SET
    discharge_datetime = '2026-08-04 14:00:00',
    status = 'Discharged',
    updated_at = '2026-08-04 14:05:00'
WHERE admission_id = 10;