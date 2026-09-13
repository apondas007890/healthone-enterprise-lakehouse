-- ============================================================
-- DAY 4 — TABLE: billing
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new billing (IDs start from 16)
INSERT INTO billing
    (bill_id, admission_id, patient_id, amount, insurance_covered, payment_status, bill_datetime, created_at, updated_at)
VALUES
    (16, 12, 18, 22000.00, 15000.00, 'Pending', '2026-08-05 10:00:00', '2026-08-05 10:00:00', '2026-08-05 10:00:00'),
    (17, 13, 20, 35000.00, 25000.00, 'Paid', '2026-08-05 11:00:00', '2026-08-05 11:00:00', '2026-08-05 11:00:00'),
    (18, 14, 21, 16000.00, 20000.00, 'Partially Paid', '2026-08-05 12:00:00', '2026-08-05 12:00:00', '2026-08-05 12:00:00'),
    (19, NULL, 19, 13000.00, NULL, 'Pending', '2026-08-05 13:00:00', '2026-08-05 13:00:00', '2026-08-05 13:00:00'),
    (20, 15, 22, 29000.00, 18000.00, 'Pending', '2026-08-05 14:00:00', '2026-08-05 14:00:00', '2026-08-05 14:00:00');

-- Day 4 billing updates
UPDATE billing
SET
    payment_status = 'Paid',
    updated_at = '2026-08-05 15:00:00'
WHERE bill_id = 11;

UPDATE billing
SET
    payment_status = 'Partially Paid',
    updated_at = '2026-08-05 16:00:00'
WHERE bill_id = 15;

UPDATE billing
SET
    payment_status = 'Paid',
    updated_at = '2026-08-05 17:00:00'
WHERE bill_id = 7;