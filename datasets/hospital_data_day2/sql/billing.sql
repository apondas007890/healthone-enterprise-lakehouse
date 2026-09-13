-- DAY 2 — TABLE: billing
-- Date: 2026-08-03


-- Day 2 new billing (NO Day 0/1 data, IDs start from 6)
INSERT INTO billing
    (bill_id, admission_id, patient_id, amount, insurance_covered, payment_status, bill_datetime, created_at, updated_at)
VALUES
    (6, 4, 7, 12000.00, 8000.00, 'Pending', '2026-08-03 10:00:00', '2026-08-03 10:00:00', '2026-08-03 10:00:00'),
    (7, 5, 8, 35000.00, 25000.00, 'Paid', '2026-08-03 11:00:00', '2026-08-03 11:00:00', '2026-08-03 11:00:00'),
    (8, 6, 9, 16000.00, 12000.00, 'Pending', '2026-08-03 12:00:00', '2026-08-03 12:00:00', '2026-08-03 12:00:00'),
    (9, NULL, 10, 22000.00, 28000.00, 'Partially Paid', '2026-08-03 13:00:00', '2026-08-03 13:00:00', '2026-08-03 13:00:00'),
    (10, 4, 11, 9000.00, NULL, 'Pending', '2026-08-03 14:00:00', '2026-08-03 14:00:00', '2026-08-03 14:00:00');


-- Day 2 billing updates
UPDATE billing
SET
    payment_status = 'Paid',
    updated_at = '2026-08-03 15:00:00'
WHERE bill_id = 1;

UPDATE billing
SET
    payment_status = 'Paid',
    updated_at = '2026-08-03 16:00:00'
WHERE bill_id = 3;