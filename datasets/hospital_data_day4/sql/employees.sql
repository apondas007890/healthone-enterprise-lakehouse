-- ============================================================
-- DAY 4 — TABLE: employees
-- Date: 2026-08-05
-- ============================================================

-- Day 4 new employees
INSERT INTO employees
    (employee_id, first_name, last_name, dob, gender, address, phone, email, role, department_id, hire_date, salary, status, hospital_id, created_at, updated_at)
VALUES
    (22, 'Jahangir', 'Alam', '1984-08-15', 'Male', 'Agrabad, Chittagong', '01712345678', 'jahangir.alam@gmail.com', 'Nurse', 11, '2020-06-01', 44000.00, 'Active', 6, '2026-08-05 09:00:00', '2026-08-05 09:00:00'),
    (23, 'Shabnam', 'Ara', '1990-12-03', 'Female', 'Chittagong', '01899887766', 'shabnam.ara@gmail.com', 'Technician', 12, '2021-09-15', 39000.00, 'Active', 6, '2026-08-05 09:05:00', '2026-08-05 09:05:00'),
    (24, 'Mizanur', 'Rahman', '1987-04-22', 'male', 'Dhanmondi, Dhaka', '01988776655', 'mizanur.rahman@gmail.com', 'Nurse', 13, '2020-11-01', 43000.00, 'Active', 1, '2026-08-05 09:10:00', '2026-08-05 09:10:00'),
    (25, 'Sajeda', 'Akter', '1994-06-10', 'F', 'Mirpur, Dhaka', '01711223344', 'sajeda.akter@gmail.com', 'Lab Technician', 3, '2022-03-01', 37000.00, 'Active', 1, '2026-08-05 09:15:00', '2026-08-05 09:15:00'),
    (26, 'Rana', 'Miah', '1992-10-28', 'Male', 'Uttara, Dhaka', '1785679266', 'rana.miah@gmail.com', 'Accountant', 8, '2023-11-15', 46000.00, 'Active', 4, '2026-08-05 09:20:00', '2026-08-05 09:20:00');

-- Day 4 employee updates
UPDATE employees
SET
    salary = 55000.00,
    role = 'Head Nurse',
    updated_at = '2026-08-05 10:00:00'
WHERE employee_id = 2;

UPDATE employees
SET
    department_id = 10,
    updated_at = '2026-08-05 10:30:00'
WHERE employee_id = 15;

UPDATE employees
SET
    status = 'On Leave',
    updated_at = '2026-08-05 11:00:00'
WHERE employee_id = 6;

UPDATE employees
SET
    salary = 50000.00,
    updated_at = '2026-08-05 11:30:00'
WHERE employee_id = 10;