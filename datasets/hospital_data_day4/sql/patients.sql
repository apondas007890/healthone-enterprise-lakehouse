-- ============================================================
-- DAY 4 — TABLE: patients
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new patients (IDs start from 18)
INSERT INTO patients
    (patient_id, first_name, last_name, dob, gender, phone, address, email, blood_group, hospital_id, created_at, updated_at)
VALUES
    (18, 'Kazi', 'Kamal', '1986-09-15', 'Male', '01712345678', 'Agrabad, Chittagong', 'kazi.kamal@gmail.com', 'A+', 6, '2026-08-05 09:00:00', '2026-08-05 09:00:00'),
    (19, 'Moushumi', 'Akter', '1992-05-12', 'female', '01899887766', 'Chittagong', 'moushumi.akter@gmail.com', 'B+', 6, '2026-08-05 09:05:00', '2026-08-05 09:05:00'),
    (20, 'Jamil', 'Hossain', '1998-11-30', 'M', '01988776655', 'Gulshan, Dhaka', 'jamil.hossain@gmail.com', 'O+', 1, '2026-08-05 09:10:00', '2026-08-05 09:10:00'),
    (21, 'Rehana', 'Begum', '1985-07-18', 'Female', '01711223344', 'Uttara, Dhaka', 'rehana.begum@gmail.com', 'AB-', 5, '2026-08-05 09:15:00', '2026-08-05 09:15:00'),
    (22, 'Shafiq', 'Islam', '1993-02-28', 'MALE', '1785679266', 'Mirpur, Dhaka', 'shafiq.islam@gmail.com', 'A-', 2, '2026-08-05 09:20:00', '2026-08-05 09:20:00');

-- Day 4 duplicate-like patient (similar to ID 18)
INSERT INTO patients
    (patient_id, first_name, last_name, dob, gender, phone, address, email, blood_group, hospital_id, created_at, updated_at)
VALUES
    (23, 'Kazi', 'Kamal', '1986-09-15', 'Male', '01712345678', 'Agrabad, Chittagong', 'kazi.kamal2@gmail.com', 'A+', 6, '2026-08-05 09:25:00', '2026-08-05 09:25:00');

-- Day 4 patient updates
UPDATE patients
SET
    address = 'Dhanmondi-15, Dhaka',
    updated_at = '2026-08-05 10:00:00'
WHERE patient_id = 2;

UPDATE patients
SET
    phone = '01712345678',
    updated_at = '2026-08-05 10:30:00'
WHERE patient_id = 8;

UPDATE patients
SET
    gender = 'Female',
    updated_at = '2026-08-05 11:00:00'
WHERE patient_id = 14;

UPDATE patients
SET
    address = 'Mohammadpur, Dhaka-1207',
    updated_at = '2026-08-05 11:30:00'
WHERE patient_id = 15;