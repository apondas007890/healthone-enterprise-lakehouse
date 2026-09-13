-- ============================================================
-- DAY 3 — TABLE: appointments
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new appointments (IDs start from 15)
INSERT INTO appointments
    (appointment_id, patient_id, doctor_id, hospital_id, appointment_datetime, status, reason, created_at, updated_at)
VALUES
    (15, 12, 9, 5, '2026-08-04 09:00:00', 'Scheduled', 'Newborn checkup', '2026-08-04 08:00:00', '2026-08-04 08:00:00'),
    (16, 13, 10, 5, '2026-08-04 10:00:00', 'Completed', 'ENT consultation', '2026-08-04 08:05:00', '2026-08-04 08:05:00'),
    (17, 14, 5, 1, '2026-08-04 11:00:00', 'scheduled', 'General checkup', '2026-08-04 08:10:00', '2026-08-04 08:10:00'),
    (18, 15, 2, 3, '2026-08-04 12:00:00', 'SCHEDULED', 'Neurology follow-up', '2026-08-04 08:15:00', '2026-08-04 08:15:00'),
    (19, 16, 4, 2, '2026-08-04 13:00:00', 'Done', 'Orthopedic assessment', '2026-08-04 08:20:00', '2026-08-04 08:20:00'),
    (20, 12, 9, 5, '2026-08-04 09:00:00', 'Scheduled', 'Newborn checkup', '2026-08-04 09:00:00', '2026-08-04 09:00:00');

-- Day 3 appointment updates
UPDATE appointments
SET
    status = 'Completed',
    updated_at = '2026-08-04 10:30:00'
WHERE appointment_id = 13;

UPDATE appointments
SET
    status = 'Cancelled',
    updated_at = '2026-08-04 11:00:00'
WHERE appointment_id = 11;

UPDATE appointments
SET
    status = 'Completed',
    updated_at = '2026-08-04 11:30:00'
WHERE appointment_id = 15;