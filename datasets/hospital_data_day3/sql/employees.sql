-- ============================================================
-- DAY 3 — TABLE: employees
-- Date: 2026-08-04
-- ============================================================

-- Day 3 new employees
INSERT INTO employees
    (employee_id, first_name, last_name, dob, gender, address, phone, email, role, department_id, hire_date, salary, status, hospital_id, created_at, updated_at)
VALUES
    (18, 'Shahida', 'Begum', '1986-05-12', 'Female', 'Uttara, Dhaka', '01712345678', 'shahida.begum@gmail.com', 'Nurse', 9, '2025-01-15', 42000.00, 'Active', 5, '2026-08-04 09:00:00', '2026-08-04 09:00:00'),
    (19, 'Kamal', 'Hossain', '1991-09-30', 'male', 'Mirpur, Dhaka', '01899887766', 'kamal.hossain@gmail.com', 'Technician', 10, '2025-03-01', 38000.00, 'Active', 5, '2026-08-04 09:05:00', '2026-08-04 09:05:00'),
    (20, 'Laila', 'Akter', '1989-11-25', 'F', 'Gulshan, Dhaka', '01988776655', 'laila.akter@gmail.com', 'Pharmacist', 5, '2024-07-01', 45000.00, 'Active', 2, '2026-08-04 09:10:00', '2026-08-04 09:10:00'),
    (21, 'Sumon', 'Khan', '1993-02-18', 'Male', 'Dhanmondi, Dhaka', '1785679266', 'sumon.khan@gmail.com', 'Nurse', 1, '2025-06-01', 40000.00, 'Active', 1, '2026-08-04 09:15:00', '2026-08-04 09:15:00');

-- Day 3 employee updates
UPDATE employees
SET
    salary = 50000.00,
    role = 'Senior Pharmacist',
    updated_at = '2026-08-04 10:00:00'
WHERE employee_id = 14;

UPDATE employees
SET
    department_id = 9,
    updated_at = '2026-08-04 10:30:00'
WHERE employee_id = 13;

UPDATE employees
SET
    status = 'Resigned',
    updated_at = '2026-08-04 11:00:00'
WHERE employee_id = 8;