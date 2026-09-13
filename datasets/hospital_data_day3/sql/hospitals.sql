-- ============================================================
-- DAY 3 — TABLE: hospitals
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new hospital
INSERT INTO hospitals
    (hospital_id, name, address, city, region, capacity, opened_date, created_at, updated_at)
VALUES
    (5, 'Uttara Women and Children Hospital', 'Uttara-12, Dhaka', 'Dhaka', 'Dhaka Division', 150, '2026-01-10', '2026-08-04 09:00:00', '2026-08-04 09:00:00');

-- Day 3 hospital updates
UPDATE hospitals
SET
    capacity = 300,
    updated_at = '2026-08-04 10:00:00'
WHERE hospital_id = 4;

UPDATE hospitals
SET
    name = 'Gulshan City General Hospital',
    address = 'Gulshan-1, Dhaka',
    updated_at = '2026-08-04 10:30:00'
WHERE hospital_id = 3;