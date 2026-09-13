-- DAY 1 — TABLE: billing
-- Date: 2026-08-02


-- Day 1 new billing (NO Day 0 data, IDs start from 1)
INSERT INTO billing
    (bill_id, admission_id, patient_id, amount, insurance_covered, payment_status, bill_datetime, created_at, updated_at)
VALUES
    (1, 1, 1, 15000.00, 10000.00, 'Pending', '2026-08-02 10:00:00', '2026-08-02 10:00:00', '2026-08-02 10:00:00'),
    (2, 2, 3, 32000.00, 25000.00, 'Paid', '2026-08-02 11:00:00', '2026-08-02 11:00:00', '2026-08-02 11:00:00'),
    (3, 3, 5, 8500.00, 4000.00, 'Pending', '2026-08-02 12:00:00', '2026-08-02 12:00:00', '2026-08-02 12:00:00');

-- Billing with issues
INSERT INTO billing
    (bill_id, admission_id, patient_id, amount, insurance_covered, payment_status, bill_datetime, created_at, updated_at)
VALUES
    (4, NULL, 4, 20000.00, NULL, 'Pending', '2026-08-02 13:00:00', '2026-08-02 13:00:00', '2026-08-02 13:00:00'),
    (5, 1, 2, 18000.00, 22000.00, 'Partially Paid', '2026-08-02 14:00:00', '2026-08-02 14:00:00', '2026-08-02 14:00:00');

-- Billing updates (payment progress)
UPDATE billing
SET
    payment_status = 'Partially Paid',
    updated_at = '2026-08-02 15:00:00'
WHERE bill_id = 1;

UPDATE billing
SET
    payment_status = 'Paid',
    updated_at = '2026-08-02 16:00:00'
WHERE bill_id = 3;