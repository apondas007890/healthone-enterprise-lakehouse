-- ============================================================
-- DAY 4 — TABLE: appointments
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new appointments (IDs start from 21)
INSERT INTO appointments
    (appointment_id, patient_id, doctor_id, hospital_id, appointment_datetime, status, reason, created_at, updated_at)
VALUES
    (21, 18, 11, 6, '2026-08-05 09:00:00', 'Scheduled', 'Nephrology consultation', '2026-08-05 08:00:00', '2026-08-05 08:00:00'),
    (22, 19, 12, 6, '2026-08-05 10:00:00', 'Completed', 'Urology checkup', '2026-08-05 08:05:00', '2026-08-05 08:05:00'),
    (23, 20, 13, 1, '2026-08-05 11:00:00', 'scheduled', 'Gastroenterology consultation', '2026-08-05 08:10:00', '2026-08-05 08:10:00'),
    (24, 21, 9, 5, '2026-08-05 12:00:00', 'SCHEDULED', 'Neonatology follow-up', '2026-08-05 08:15:00', '2026-08-05 08:15:00'),
    (25, 22, 4, 2, '2026-08-05 13:00:00', 'Done', 'Orthopedic consultation', '2026-08-05 08:20:00', '2026-08-05 08:20:00'),
    (26, 18, 11, 6, '2026-08-05 09:00:00', 'Scheduled', 'Nephrology consultation', '2026-08-05 09:00:00', '2026-08-05 09:00:00');

-- Day 4 appointment updates
UPDATE appointments
SET
    status = 'Completed',
    updated_at = '2026-08-05 10:30:00'
WHERE appointment_id = 17;

UPDATE appointments
SET
    status = 'Cancelled',
    updated_at = '2026-08-05 11:00:00'
WHERE appointment_id = 18;

UPDATE appointments
SET
    status = 'Completed',
    updated_at = '2026-08-05 11:30:00'
WHERE appointment_id = 21;

UPDATE appointments
SET
    status = 'Scheduled',
    updated_at = '2026-08-05 12:00:00'
WHERE appointment_id = 14;