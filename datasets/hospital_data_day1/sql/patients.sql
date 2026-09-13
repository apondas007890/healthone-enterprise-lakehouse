-- DAY 1 — TABLE: patients
-- Date: 2026-08-02


-- Day 1 new patients (NO Day 0 data, IDs start from 1)
INSERT INTO patients
    (patient_id, first_name, last_name, dob, gender, phone, address, email, blood_group, hospital_id, created_at, updated_at)
VALUES
    (1, 'Rashed', 'Khan', '1992-09-15', 'Male', '01712345678', 'Gulshan, Dhaka', 'rashed.khan@gmail.com', 'A+', 3, '2026-08-02 09:00:00', '2026-08-02 09:00:00'),
    (2, 'Nadia', 'Sultana', '1987-03-22', 'female', '01898765432', 'Mohammadpur, Dhaka', 'nadia.sultana@gmail.com', 'B+', 1, '2026-08-02 09:05:00', '2026-08-02 09:05:00'),
    (3, 'Kamal', 'Hossain', '2000-12-10', 'M', '01912345678', ' Banani, Dhaka ', 'kamal.hossain@gmail.com', 'O+', 1, '2026-08-02 09:10:00', '2026-08-02 09:10:00'),
    (4, 'Sohel', 'Rana', '1995-06-30', 'male', '01711223344', 'Uttara, Dhaka', 'sohel.rana@gmail.com', 'AB-', 2, '2026-08-02 09:15:00', '2026-08-02 09:15:00'),
    (5, 'Rina', 'Akter', '2028-05-20', 'Female', '01812345678', 'Dhanmondi, Dhaka', 'rina.akter@gmail.com', 'A-', 1, '2026-08-02 09:20:00', '2026-08-02 09:20:00');

-- Duplicate-like patient (similar to ID 1)
INSERT INTO patients
    (patient_id, first_name, last_name, dob, gender, phone, address, email, blood_group, hospital_id, created_at, updated_at)
VALUES
    (6, 'Rashed', 'Khan', '1992-09-15', 'Male', '01712345678', 'Gulshan, Dhaka', 'rashed.khan12@gmail.com', 'A+', 3, '2026-08-02 09:25:00', '2026-08-02 09:25:00');

-- Patient updates
UPDATE patients
SET
    phone = '01712345678',
    updated_at = '2026-08-02 10:00:00'
WHERE patient_id = 2;

UPDATE patients
SET
    address = 'Dhanmondi, Dhaka',
    updated_at = '2026-08-02 10:05:00'
WHERE patient_id = 4;