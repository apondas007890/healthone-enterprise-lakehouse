-- ============================================================
-- DAY 4 — TABLE: hospitals
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new hospital
INSERT INTO hospitals
    (hospital_id, name, address, city, region, capacity, opened_date, created_at, updated_at)
VALUES
    (6, ' Chittagong Medical Center ', 'Agrabad, Chittagong', 'Chittagong', 'Chittagong Division', 320, '2019-11-20', '2026-08-05 09:00:00', '2026-08-05 09:00:00');

-- Day 4 hospital updates
UPDATE hospitals
SET
    capacity = 400,
    updated_at = '2026-08-05 10:00:00'
WHERE hospital_id = 1;

UPDATE hospitals
SET
    address = 'Gulshan-2, Dhaka-1212',
    updated_at = '2026-08-05 10:30:00'
WHERE hospital_id = 3;

UPDATE hospitals
SET
    name = 'Mirpur General and Trauma Center ',
    updated_at = '2026-08-05 11:00:00'
WHERE hospital_id = 4;