-- DAY 2 — TABLE: hospitals
-- Date: 2026-08-03


-- Day 2 new hospital
INSERT INTO hospitals
    (hospital_id, name, address, city, region, capacity, opened_date, created_at, updated_at)
VALUES
    (4, 'Mirpur General Hospital ', 'Mirpur-10, Dhaka', 'Dhaka', 'Dhaka Division', 250, '2025-06-01', '2026-08-03 09:00:00', '2026-08-03 09:00:00');

-- Day 2 hospital update
UPDATE hospitals
SET
    capacity = 200,
    updated_at = '2026-08-03 10:00:00'
WHERE hospital_id = 3;