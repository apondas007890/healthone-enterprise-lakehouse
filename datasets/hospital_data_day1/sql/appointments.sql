-- DAY 1 — TABLE: appointments
-- Date: 2026-08-02


-- Day 1 new appointments (NO Day 0 data, IDs start from 1)
INSERT INTO appointments
    (appointment_id, patient_id, doctor_id, hospital_id, appointment_datetime, status, reason, created_at, updated_at)
VALUES
    (1, 1, 7, 3, '2026-08-02 09:00:00', 'Scheduled', 'Heart checkup', '2026-08-02 08:00:00', '2026-08-02 08:00:00'),
    (2, 2, 5, 1, '2026-08-02 10:00:00', 'Completed', 'Blood pressure check', '2026-08-02 08:05:00', '2026-08-02 08:05:00'),
    (3, 3, 1, 1, '2026-08-02 11:00:00', 'scheduled', 'Routine checkup', '2026-08-02 08:10:00', '2026-08-02 08:10:00'),
    (4, 4, 3, 2, '2026-08-02 12:00:00', 'SCHEDULED', 'Pediatric consultation', '2026-08-02 08:15:00', '2026-08-02 08:15:00'),
    (5, 5, 2, 2, '2026-08-02 13:00:00', 'Done', 'Neurological assessment', '2026-08-02 08:20:00', '2026-08-02 08:20:00'),
    (6, 1, 2, 1, '2026-08-02 14:00:00', 'Scheduled', 'Neurology follow-up', '2026-08-02 08:25:00', '2026-08-02 08:25:00'),
    (7, 2, 7, 3, '2026-08-02 15:00:00', 'Completed', 'Cardiology consultation', '2026-08-02 08:30:00', '2026-08-02 08:30:00');

-- Duplicate-like appointment (similar to ID 1)
INSERT INTO appointments
    (appointment_id, patient_id, doctor_id, hospital_id, appointment_datetime, status, reason, created_at, updated_at)
VALUES
    (8, 1, 7, 3, '2026-08-02 09:00:00', 'Scheduled', 'Heart checkup', '2026-08-02 09:00:00', '2026-08-02 09:00:00');

-- Appointment updates (lifecycle changes)
UPDATE appointments
SET
    status = 'Completed',
    updated_at = '2026-08-02 10:30:00'
WHERE appointment_id = 3;

UPDATE appointments
SET
    status = 'Cancelled',
    updated_at = '2026-08-02 10:35:00'
WHERE appointment_id = 5;

UPDATE appointments
SET
    status = 'Completed',
    updated_at = '2026-08-02 10:40:00'
WHERE appointment_id = 6;