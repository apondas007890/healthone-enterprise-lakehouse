-- DAY 1 — TABLE: hospitals
-- Date: 2026-08-02


INSERT INTO hospitals
    (hospital_id, name, address, city, region, capacity, opened_date, created_at, updated_at)
VALUES
    -- Day 0 hospitals (baseline)
    (1, 'Dhaka Central Medical Center', 'Dhanmondi, Dhaka', 'Dhaka', 'Dhaka Division', 350, '2018-03-15', '2026-08-01 08:00:00', '2026-08-01 08:00:00'),
    (2, 'Narayanganj General Hospital', 'Chashara, Narayanganj', 'Narayanganj', 'Dhaka Division', 220, '2020-07-10', '2026-08-01 08:05:00', '2026-08-01 08:05:00'),
    -- Day 1 new hospital
    (3, 'Gulshan City Hospital ', 'Gulshan-2, Dhaka', 'Dhaka ', 'Dhaka Division', 180, '2024-01-15', '2026-08-02 09:00:00', '2026-08-02 09:00:00');


-- Day 1 hospital update
UPDATE hospitals
SET
    capacity = 280,
    updated_at = '2026-08-02 09:30:00'
WHERE hospital_id = 2;