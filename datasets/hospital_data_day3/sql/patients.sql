-- ============================================================
-- DAY 3 — TABLE: patients
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new patients (IDs start from 12)
INSERT INTO patients
    (patient_id, first_name, last_name, dob, gender, phone, address, email, blood_group, hospital_id, created_at, updated_at)
VALUES
    (12, 'Shila', 'Khatun', '1996-07-10', 'Female', '01712345678', 'Uttara, Dhaka', 'shila.khatun@gmail.com', 'B+', 5, '2026-08-04 09:00:00', '2026-08-04 09:00:00'),
    (13, 'Monir', 'Islam', '1988-11-03', 'male', '01899887766', 'Mirpur, Dhaka', 'monir.islam@gmail.com', 'A+', 5, '2026-08-04 09:05:00', '2026-08-04 09:05:00'),
    (14, 'Taslima', 'Begum', '1992-04-18', 'M', '01988776655', ' Banani, Dhaka ', 'taslima.begum@gmail.com', 'O-', 1, '2026-08-04 09:10:00', '2026-08-04 09:10:00'),
    (15, 'Imran', 'Hossain', '1990-09-25', 'Male', '01711223344', 'Gulshan, Dhaka', 'imran.hossain@gmail.com', 'AB+', 3, '2026-08-04 09:15:00', '2026-08-04 09:15:00'),
    (16, 'Nadia', 'Sultana', '1985-06-30', 'Female', '01912345678', 'Dhanmondi, Dhaka', 'nadia.sultana@gmail.com', 'A-', 2, '2026-08-04 09:20:00', '2026-08-04 09:20:00');

-- Day 3 duplicate-like patient (similar to ID 12)
INSERT INTO patients
    (patient_id, first_name, last_name, dob, gender, phone, address, email, blood_group, hospital_id, created_at, updated_at)
VALUES
    (17, 'Shila', 'Khatun', '1996-07-10', 'Female', '01712345678', 'Uttara, Dhaka', 'shila.khatun2@gmail.com', 'B+', 5, '2026-08-04 09:25:00', '2026-08-04 09:25:00');

-- Day 3 patient updates
UPDATE patients
SET
    address = 'Mirpur-12, Dhaka',
    updated_at = '2026-08-04 10:00:00'
WHERE patient_id = 7;

UPDATE patients
SET
    phone = '01712345678',
    updated_at = '2026-08-04 10:30:00'
WHERE patient_id = 10;

UPDATE patients
SET
    gender = 'Female',
    updated_at = '2026-08-04 11:00:00'
WHERE patient_id = 13;