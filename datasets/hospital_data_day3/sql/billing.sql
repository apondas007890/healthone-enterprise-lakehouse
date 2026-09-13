-- ============================================================
-- DAY 3 — TABLE: billing
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new billing (IDs start from 11)
INSERT INTO billing
    (bill_id, admission_id, patient_id, amount, insurance_covered, payment_status, bill_datetime, created_at, updated_at)
VALUES
    (11, 8, 12, 18000.00, 12000.00, 'Pending', '2026-08-04 10:00:00', '2026-08-04 10:00:00', '2026-08-04 10:00:00'),
    (12, 9, 14, 28000.00, 20000.00, 'Paid', '2026-08-04 11:00:00', '2026-08-04 11:00:00', '2026-08-04 11:00:00'),
    (13, 10, 15, 15000.00, 18000.00, 'Partially Paid', '2026-08-04 12:00:00', '2026-08-04 12:00:00', '2026-08-04 12:00:00'),
    (14, NULL, 16, 11000.00, NULL, 'Pending', '2026-08-04 13:00:00', '2026-08-04 13:00:00', '2026-08-04 13:00:00'),
    (15, 11, 12, 22000.00, 15000.00, 'Pending', '2026-08-04 14:00:00', '2026-08-04 14:00:00', '2026-08-04 14:00:00');

-- Day 3 billing updates
UPDATE billing
SET
    payment_status = 'Partially Paid',
    updated_at = '2026-08-04 15:00:00'
WHERE bill_id = 6;

UPDATE billing
SET
    payment_status = 'Paid',
    updated_at = '2026-08-04 16:00:00'
WHERE bill_id = 8;