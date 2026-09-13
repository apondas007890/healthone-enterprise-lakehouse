-- DAY 2 — TABLE: employees
-- Date: 2026-08-03


-- Day 2 new employees
INSERT INTO employees
    (employee_id, first_name, last_name, dob, gender, address, phone, email, role, department_id, hire_date, salary, status, hospital_id, created_at, updated_at)
VALUES
    (15, 'Zahid', 'Hasan', '1993-07-20', 'Female', 'Gulshan, Dhaka', '01612345678', 'zahid.hasan@gmail.com', 'Technician', 7, '2024-06-01', 38000.00, ' Active ', 3, '2026-08-03 09:00:00', '2026-08-03 09:00:00'),
    (16, 'Salma', 'Khatun', '1990-11-25', 'Female', 'Mirpur, Dhaka', '01711223344', 'salma.khatungmail.com', 'Accountant', 8, '2023-09-15', 45000.00, 'Active', 4, '2026-08-03 09:05:00', '2026-08-03 09:05:00'),
    (17, 'Rafiq', 'Ahmed', '1985-04-10', 'MALE', 'Mohammadpur, Dhaka', '01899887766', 'rafiq.ahmed@gmail.com', 'Nurse', 1, '2024-02-01', 42000.00, 'Active', 1, '2026-08-03 09:10:00', '2026-08-03 09:10:00');


-- Day 2 employee updates
UPDATE employees
SET
    role = 'Head Nurse',
    salary = 58000.00,
    updated_at = '2026-08-03 10:00:00'
WHERE employee_id = 5;

UPDATE employees
SET
    department_id = 7,
    updated_at = '2026-08-03 10:30:00'
WHERE employee_id = 13;