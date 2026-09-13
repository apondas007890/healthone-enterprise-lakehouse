-- DAY 1 — TABLE: admissions
-- Date: 2026-08-02


-- Day 1 new admissions (NO Day 0 data, IDs start from 1)
INSERT INTO admissions
    (admission_id, patient_id, hospital_id, admit_datetime, discharge_datetime, ward, bed_no, status, created_at, updated_at)
VALUES
    (1, 1, 3, '2026-08-02 08:00:00', NULL, 'General Ward', 'G-301', 'Admitted', '2026-08-02 07:00:00', '2026-08-02 07:00:00'),
    (2, 3, 1, '2026-08-02 09:00:00', '2026-08-02 17:00:00', 'Cardiology', 'C-101', 'Discharged', '2026-08-02 07:05:00', '2026-08-02 07:05:00'),
    (3, 5, 2, '2026-08-02 10:00:00', '2026-08-02 16:30:00', 'Pediatrics', 'P-201', 'Admitted', '2026-08-02 07:10:00', '2026-08-02 07:10:00');

-- Admission update (lifecycle)
UPDATE admissions
SET
    discharge_datetime = '2026-08-02 18:00:00',
    status = 'Discharged',
    updated_at = '2026-08-02 18:05:00'
WHERE admission_id = 1;