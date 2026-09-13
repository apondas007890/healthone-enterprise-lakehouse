-- DAY 1 — TABLE: employees
-- Date: 2026-08-02


-- Day 0 employees (baseline)
INSERT INTO employees
    (employee_id, first_name, last_name, dob, gender, address, phone, email, role, department_id, hire_date, salary, status, hospital_id, created_at, updated_at)
VALUES
    (1, 'Rahim', 'Uddin', '1988-04-12', 'Male', 'Dhanmondi, Dhaka', '01711023456', 'rahim.uddin@gmail.com', 'Nurse', 3, '2019-02-10', 42000.00, 'Active', 1, '2026-08-01 08:20:00', '2026-08-01 08:20:00'),
    (2, 'Nusrat', 'Jahan', '1992-08-21', 'female', 'Mirpur, Dhaka', '01819234567', 'nusrat.jahan@gmail.com', 'Nurse', 3, '2020-05-18', 45000.00, 'Active', 1, '2026-08-01 08:21:00', '2026-08-01 08:21:00'),
    (3, 'Tanvir', 'Ahmed', '1985-11-03', 'MALE', 'Uttara, Dhaka', '01911223344', 'tanvir.ahmed@gmail.com', 'Lab Technician', 6, '2018-09-05', 48000.00, 'Active', 2, '2026-08-01 08:22:00', '2026-08-01 08:22:00'),
    (4, 'Sadia', 'Islam', '1990-01-17', 'F', 'Mohammadpur, Dhaka', '01612345678', 'sadia.islam@gmail.com', 'Doctor Assistant', 2, '2021-01-12', 52000.00, 'Active', 1, '2026-08-01 08:23:00', '2026-08-01 08:23:00'),
    (5, 'Mehedi', 'Hasan', '1987-06-25', 'Malee', 'Badda, Dhaka', '01555667788', 'mehedi.hasan@gmail.com', 'Senior Nurse', 1, '2017-11-20', 55000.00, 'Active', 1, '2026-08-01 08:24:00', '2026-08-01 08:24:00'),
    (6, 'Farhana', 'Akter', '1994-03-09', 'Female', 'Narayanganj Sadar', '01712345678', 'farhana.akter@gmail.com', 'Nurse', 4, '2022-04-15', 40000.00, 'Active', 2, '2026-08-01 08:25:00', '2026-08-01 08:25:00'),
    (7, 'Arif', 'Hossain', '1983-09-14', 'male', 'Fatullah, Narayanganj', '01876543210', 'arif.hossain@gmail.com', 'Technician', 6, '2016-08-01', 47000.00, 'Active', 2, '2026-08-01 08:26:00', '2026-08-01 08:26:00'),
    (8, 'Jannatul', 'Ferdous', '1995-12-02', 'Female', 'Kanchpur, Narayanganj', '01988776655', 'jannatul.ferdous@gmail.com', 'Nurse', 4, '2023-02-05', 39000.00, 'On Leave', 2, '2026-08-01 08:27:00', '2026-08-01 08:27:00'),
    (9, 'Rakibul', 'Islam', '1989-07-19', 'Male', 'Chashara, Narayanganj', '01799887766', 'rakibul.islam@gmail.com', 'Nurse', 5, '2020-10-10', 46000.00, 'Active', 2, '2026-08-01 08:28:00', '2026-08-01 08:28:00'),
    (10, 'Apon', 'Kumar Das', '1994-03-09', 'Male', 'Narayanganj Sadar', '01833445566', 'apon.das@gmail.com', 'IT Support', 6, '2022-06-01', 50000.00, 'Active', 2, '2026-08-01 08:29:00', '2026-08-01 08:29:00'),
    (11, 'Shamim', 'Ahmed', '1991-05-11', ' Male ', 'Uttara, Dhaka', '1785679266', 'shamim.ahmed@gmail.com', 'Nurse', 3, '2021-07-12', 43000.00, ' Active ', 1, '2026-08-01 08:30:00', '2026-08-01 08:30:00'),
    (12, 'Mim', 'Akter', '1996-02-28', 'Female', 'Banani, Dhaka', NULL, 'mim@', 'Receptionist', 1, '2024-01-08', 36000.00, 'Active', 1, '2026-08-01 08:31:00', '2026-08-01 08:31:00'),
    -- Day 1 new employees
    (13, 'Hasan', 'Miah', '1990-06-15', 'male', ' Mirpur, Dhaka ', '01812345678', 'hasan.miah@gmail.com', 'Senior Nurse', 2, '2023-08-15', 48000.00, 'Active', 1, '2026-08-02 10:00:00', '2026-08-02 10:00:00'),
    (14, 'Taslima', 'Begum', '1988-12-01', 'F', 'Uttara, Dhaka', '0171234567', 'taslima.begum@gmail.com', 'Pharmacist', 5, '2024-03-01', 42000.00, 'Active', 2, '2026-08-02 10:05:00', '2026-08-02 10:05:00');


-- Day 1 employee updates (SCD Type 2 test cases)
UPDATE employees
SET
    role = 'Senior Nurse',
    salary = 48000.00,
    updated_at = '2026-08-02 10:10:00'
WHERE employee_id = 2;

UPDATE employees
SET
    department_id = 2,
    updated_at = '2026-08-02 10:15:00'
WHERE employee_id = 5;

UPDATE employees
SET
    status = 'Active',
    updated_at = '2026-08-02 10:20:00'
WHERE employee_id = 8;