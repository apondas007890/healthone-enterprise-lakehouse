-- =======================================================
-- Database: sqldb-corporate-hr
-- =======================================================

-- 1. Drop existing tables in reverse dependency order
IF OBJECT_ID('dbo.payroll', 'U') IS NOT NULL DROP TABLE dbo.payroll;
IF OBJECT_ID('dbo.employees', 'U') IS NOT NULL DROP TABLE dbo.employees;
IF OBJECT_ID('dbo.departments', 'U') IS NOT NULL DROP TABLE dbo.departments;
IF OBJECT_ID('dbo.hospitals', 'U') IS NOT NULL DROP TABLE dbo.hospitals;

-- 2. Hospitals Table
CREATE TABLE dbo.hospitals (
    hospital_id   INT NOT NULL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    address       VARCHAR(200),
    city          VARCHAR(50),
    region        VARCHAR(50),
    capacity      INT,
    opened_date   DATE,
    created_at    DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at    DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 3. Departments Table
CREATE TABLE dbo.departments (
    department_id INT NOT NULL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    hospital_id   INT NOT NULL REFERENCES dbo.hospitals(hospital_id),
    created_at    DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at    DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 4. Employees Table
CREATE TABLE dbo.employees (
    employee_id   INT NOT NULL PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    dob           DATE,
    gender        VARCHAR(10),
    address       VARCHAR(200),
    phone         VARCHAR(20),
    email         VARCHAR(100),
    role          VARCHAR(50),
    department_id INT NOT NULL REFERENCES dbo.departments(department_id),
    hire_date     DATE,
    salary        DECIMAL(10,2),
    status        VARCHAR(20),
    hospital_id   INT NOT NULL REFERENCES dbo.hospitals(hospital_id),
    created_at    DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at    DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 5. Payroll Table
CREATE TABLE dbo.payroll (
    payroll_id    INT NOT NULL PRIMARY KEY,
    employee_id   INT NOT NULL REFERENCES dbo.employees(employee_id),
    pay_period    VARCHAR(20),
    gross_pay     DECIMAL(10,2),
    deductions    DECIMAL(10,2),
    net_pay       DECIMAL(10,2),
    paid_date     DATE,
    created_at    DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at    DATETIME2 DEFAULT SYSUTCDATETIME()
);
GO




-- =======================================================
-- Database: sqldb-hospital-ops
-- =======================================================

-- 1. Drop existing tables in reverse dependency order
IF OBJECT_ID('dbo.billing', 'U') IS NOT NULL DROP TABLE dbo.billing;
IF OBJECT_ID('dbo.admissions', 'U') IS NOT NULL DROP TABLE dbo.admissions;
IF OBJECT_ID('dbo.appointments', 'U') IS NOT NULL DROP TABLE dbo.appointments;
IF OBJECT_ID('dbo.doctors', 'U') IS NOT NULL DROP TABLE dbo.doctors;
IF OBJECT_ID('dbo.patients', 'U') IS NOT NULL DROP TABLE dbo.patients;

-- 2. Patients Table
CREATE TABLE dbo.patients (
    patient_id     INT NOT NULL PRIMARY KEY,
    first_name     VARCHAR(50)  NOT NULL,
    last_name      VARCHAR(50)  NOT NULL,
    dob            DATE,
    gender         VARCHAR(10),
    phone          VARCHAR(20),
    address        VARCHAR(200),
    email          VARCHAR(100),
    blood_group    VARCHAR(5),
    hospital_id    INT NOT NULL,
    created_at     DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at     DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 3. Doctors Table
CREATE TABLE dbo.doctors (
    doctor_id       INT NOT NULL PRIMARY KEY,
    specialization  VARCHAR(100),
    employee_id     INT NOT NULL,
    hospital_id     INT NOT NULL,
    created_at      DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at      DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 4. Appointments Table
CREATE TABLE dbo.appointments (
    appointment_id       INT NOT NULL PRIMARY KEY,
    patient_id           INT NOT NULL REFERENCES dbo.patients(patient_id),
    doctor_id            INT NOT NULL REFERENCES dbo.doctors(doctor_id),
    hospital_id          INT NOT NULL,
    appointment_datetime DATETIME2 NOT NULL,
    status               VARCHAR(20),
    reason               VARCHAR(200),
    created_at           DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at           DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 5. Admissions Table
CREATE TABLE dbo.admissions (
    admission_id       INT NOT NULL PRIMARY KEY,
    patient_id         INT NOT NULL REFERENCES dbo.patients(patient_id),
    hospital_id        INT NOT NULL,
    admit_datetime     DATETIME2 NOT NULL,
    discharge_datetime DATETIME2 NULL,
    ward               VARCHAR(50),
    bed_no             VARCHAR(10),
    status             VARCHAR(20),
    created_at         DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at         DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 6. Billing Table
CREATE TABLE dbo.billing (
    bill_id           INT NOT NULL PRIMARY KEY,
    admission_id      INT NULL REFERENCES dbo.admissions(admission_id),
    patient_id        INT NOT NULL REFERENCES dbo.patients(patient_id),
    amount            DECIMAL(10,2) NOT NULL,
    insurance_covered DECIMAL(10,2) DEFAULT 0,
    payment_status    VARCHAR(20),
    bill_datetime     DATETIME2 NOT NULL,
    created_at        DATETIME2 DEFAULT SYSUTCDATETIME(),
    updated_at        DATETIME2 DEFAULT SYSUTCDATETIME()
);
GO
