-- DAY 2 — TABLE: appointments
-- Date: 2026-08-03


-- Day 2 new appointments (NO Day 0/1 data, IDs start from 9)
INSERT INTO appointments
    (appointment_id, patient_id, doctor_id, hospital_id, appointment_datetime, status, reason, created_at, updated_at)
VALUES
    (9, 7, 8, 3, '2026-08-03 09:00:00', 'Scheduled', 'Neurology consultation', '2026-08-03 08:00:00', '2026-08-03 08:00:00'),
    (10, 8, 1, 1, '2026-08-03 10:00:00', 'completed', 'Cardiology follow-up', '2026-08-03 08:05:00', '2026-08-03 08:05:00'),
    (11, 9, 5, 1, '2026-08-03 11:00:00', 'SCHEDULED', 'General checkup', '2026-08-03 08:10:00', '2026-08-03 08:10:00'),
    (12, 10, 3, 2, '2026-08-03 12:00:00', 'Scheduled', 'Pediatric vaccination', '2026-08-03 08:15:00', '2026-08-03 08:15:00'),
    (13, 11, 4, 4, '2026-08-03 13:00:00', 'Done', 'Orthopedic consultation', '2026-08-03 08:20:00', '2026-08-03 08:20:00'),
    (14, 7, 8, 3, '2026-08-03 09:00:00', 'Scheduled', 'Neurology consultation', '2026-08-03 09:00:00', '2026-08-03 09:00:00');

-- Day 2 appointment updates
UPDATE appointments
SET
    status = 'Completed',
    updated_at = '2026-08-03 10:30:00'
WHERE appointment_id = 9;

UPDATE appointments
SET
    status = 'Cancelled',
    updated_at = '2026-08-03 11:00:00'
WHERE appointment_id = 12;