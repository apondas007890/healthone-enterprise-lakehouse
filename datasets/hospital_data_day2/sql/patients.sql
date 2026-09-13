-- DAY 2 — TABLE: patients
-- Date: 2026-08-03


-- Day 2 new patients (NO Day 0/1 data, IDs start from 7)
INSERT INTO patients
    (patient_id, first_name, last_name, dob, gender, phone, address, email, blood_group, hospital_id, created_at, updated_at)
VALUES
    (7, 'Nasir', 'Ali', '1984-02-14', 'male', '01899887766', 'Mirpur, Dhaka', 'nasir.ali@gmail.com', 'B-', 4, '2026-08-03 09:00:00', '2026-08-03 09:00:00'),
    (8, 'Shila', 'Rahman', '1993-08-29', 'M', '01988776655', 'Mohammadpur, Dhaka', 'shila.rahman@gmail.com', 'A+', 1, '2026-08-03 09:05:00', '2026-08-03 09:05:00'),
    (9, 'Rafiq', 'Ahmed', '1989-12-05', 'MALE', '01711223344', 'Gulshan, Dhaka', 'rafiq.ahmed@gmail.com', 'O+', 3, '2026-08-03 09:10:00', '2026-08-03 09:10:00'),
    (10, 'Nipun', 'Akter', '2001-01-15', 'Female', '1785679266', 'Banani, Dhaka', 'nipun.akter@gmail.com', 'AB+', 2, '2026-08-03 09:15:00', '2026-08-03 09:15:00'),
    (11, 'Nasir', 'Ali', '1984-02-14', 'male', '01899887766', 'Mirpur, Dhaka', 'nasir.ali2@gmail.com', 'B-', 4, '2026-08-03 09:20:00', '2026-08-03 09:20:00');

-- Day 2 patient updates
UPDATE patients
SET
    gender = 'Female',
    updated_at = '2026-08-03 10:00:00'
WHERE patient_id = 3;

UPDATE patients
SET
    phone = '01711223344',
    updated_at = '2026-08-03 10:30:00'
WHERE patient_id = 2;

UPDATE patients
SET
    address = 'Dhanmondi, Dhaka',
    updated_at = '2026-08-03 11:00:00'
WHERE patient_id = 7;