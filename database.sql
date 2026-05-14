-- =====================================================
-- Corporate Skill Gap Analyzer Database Schema
-- =====================================================

-- Create and use database
CREATE DATABASE IF NOT EXISTS corporate_skill_gap;
USE corporate_skill_gap;

-- =====================================================
-- 1. departments table
-- =====================================================
CREATE TABLE IF NOT EXISTS departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. job_roles table
-- =====================================================
CREATE TABLE IF NOT EXISTS job_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL UNIQUE,
    department_id INT,
    description TEXT,
    min_experience_years INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- =====================================================
-- 3. users table (authentication)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'employee') DEFAULT 'employee',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- =====================================================
-- 4. employees table
-- =====================================================
CREATE TABLE IF NOT EXISTS employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,
    employee_code VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department_id INT,
    job_role_id INT,
    joining_date DATE,
    experience_years DECIMAL(4,1) DEFAULT 0,
    manager_id INT NULL,
    profile_pic VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (job_role_id) REFERENCES job_roles(id),
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- =====================================================
-- 5. skills table
-- =====================================================
CREATE TABLE IF NOT EXISTS skills (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100),
    description TEXT
);

-- =====================================================
-- 6. employee_skills (many-to-many with proficiency)
-- =====================================================
CREATE TABLE IF NOT EXISTS employee_skills (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('beginner','intermediate','advanced','expert') DEFAULT 'beginner',
    years_of_experience DECIMAL(3,1) DEFAULT 0,
    last_used_year YEAR,
    certification VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_skill (employee_id, skill_id)
);

-- =====================================================
-- 7. role_required_skills
-- =====================================================
CREATE TABLE IF NOT EXISTS role_required_skills (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_role_id INT NOT NULL,
    skill_id INT NOT NULL,
    required_proficiency ENUM('beginner','intermediate','advanced','expert') DEFAULT 'intermediate',
    is_mandatory BOOLEAN DEFAULT TRUE,
    weight INT DEFAULT 1,
    FOREIGN KEY (job_role_id) REFERENCES job_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_role_skill (job_role_id, skill_id)
);

-- =====================================================
-- 8. training_resources
-- =====================================================
CREATE TABLE IF NOT EXISTS training_resources (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    provider VARCHAR(100),
    url VARCHAR(500),
    skill_id INT,
    difficulty_level ENUM('beginner','intermediate','advanced'),
    duration_hours INT,
    cost DECIMAL(10,2) DEFAULT 0,
    description TEXT,
    is_free BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL
);

-- =====================================================
-- 9. gap_analysis (stores computed gaps)
-- =====================================================
CREATE TABLE IF NOT EXISTS gap_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    skill_id INT NOT NULL,
    required_proficiency VARCHAR(20),
    current_proficiency VARCHAR(20),
    gap_score INT,  -- 0 = no gap, 1 = minor, 2 = major
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_employee (employee_id)
);

-- =====================================================
-- 10. employee_recommendations (join table for recommendations)
-- =====================================================
CREATE TABLE IF NOT EXISTS employee_recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    training_resource_id INT NOT NULL,
    status ENUM('pending','completed','ignored') DEFAULT 'pending',
    recommended_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (training_resource_id) REFERENCES training_resources(id) ON DELETE CASCADE
);

-- =====================================================
-- INDEXES for performance
-- =====================================================
CREATE INDEX idx_employee_skills_employee ON employee_skills(employee_id);
CREATE INDEX idx_employee_skills_skill ON employee_skills(skill_id);
CREATE INDEX idx_role_skill_role ON role_required_skills(job_role_id);
CREATE INDEX idx_gap_employee ON gap_analysis(employee_id);

-- =====================================================
-- VIEW: Employee Skill Gap Summary
-- =====================================================
CREATE OR REPLACE VIEW vw_employee_gap_summary AS
SELECT 
    e.id AS employee_id,
    e.first_name,
    e.last_name,
    jr.title AS job_role,
    COUNT(DISTINCT rrs.skill_id) AS total_required_skills,
    COUNT(DISTINCT es.skill_id) AS skills_owned,
    (COUNT(DISTINCT rrs.skill_id) - COUNT(DISTINCT es.skill_id)) AS missing_skills_count,
    ROUND((COUNT(DISTINCT es.skill_id) / NULLIF(COUNT(DISTINCT rrs.skill_id),0)) * 100, 1) AS readiness_percent
FROM employees e
JOIN job_roles jr ON e.job_role_id = jr.id
LEFT JOIN role_required_skills rrs ON jr.id = rrs.job_role_id
LEFT JOIN employee_skills es ON e.id = es.employee_id AND rrs.skill_id = es.skill_id
GROUP BY e.id, e.first_name, e.last_name, jr.title;

-- =====================================================
-- SAMPLE DATA (Realistic Indian Corporate Dataset)
-- =====================================================

-- Departments
INSERT INTO departments (name, description) VALUES
('Engineering', 'Software development and IT infrastructure'),
('Human Resources', 'Recruitment, payroll, employee relations'),
('Sales & Marketing', 'Lead generation, brand management, customer acquisition'),
('Finance', 'Accounting, budgeting, financial planning'),
('Operations', 'Supply chain, logistics, vendor management');

-- Job Roles
INSERT INTO job_roles (title, department_id, description, min_experience_years) VALUES
('Software Engineer', 1, 'Develop and maintain applications', 2),
('Senior Software Engineer', 1, 'Lead development and mentor juniors', 5),
('HR Generalist', 2, 'Handle recruitment and employee engagement', 2),
('Sales Executive', 3, 'Achieve sales targets and client meetings', 1),
('Financial Analyst', 4, 'Analyze financial data and create reports', 3),
('Operations Manager', 5, 'Oversee daily operations and process improvement', 6);

-- Skills
INSERT INTO skills (name, category) VALUES
('Python', 'Programming'),
('Java', 'Programming'),
('SQL', 'Database'),
('JavaScript', 'Frontend'),
('React', 'Frontend'),
('Node.js', 'Backend'),
('Django', 'Framework'),
('Machine Learning', 'Data Science'),
('Tableau', 'Data Visualization'),
('Communication', 'Soft Skills'),
('Leadership', 'Soft Skills'),
('Project Management', 'Management'),
('Recruitment', 'HR'),
('Payroll Processing', 'HR'),
('Sales Negotiation', 'Sales'),
('Financial Modeling', 'Finance');

-- Role Required Skills
-- Software Engineer (id=1) needs: Python(1), SQL(3), JavaScript(4) -> mandatory
INSERT INTO role_required_skills (job_role_id, skill_id, required_proficiency, is_mandatory) VALUES
(1, 1, 'intermediate', TRUE),
(1, 3, 'intermediate', TRUE),
(1, 4, 'beginner', TRUE),
(2, 1, 'advanced', TRUE),
(2, 3, 'advanced', TRUE),
(2, 6, 'intermediate', TRUE),
(2, 11, 'intermediate', TRUE),
(3, 13, 'intermediate', TRUE),
(3, 14, 'intermediate', TRUE),
(3, 10, 'advanced', TRUE),
(4, 15, 'advanced', TRUE),
(4, 10, 'intermediate', TRUE),
(5, 16, 'advanced', TRUE),
(5, 3, 'intermediate', TRUE),
(5, 9, 'intermediate', TRUE);

-- Training Resources
INSERT INTO training_resources (title, provider, url, skill_id, difficulty_level, duration_hours, is_free) VALUES
('Python for Everybody', 'Coursera', 'https://coursera.org/python', 1, 'beginner', 40, FALSE),
('Advanced SQL Queries', 'Udemy', 'https://udemy.com/sql', 3, 'intermediate', 8, FALSE),
('React Complete Guide', 'Academind', 'https://academind.com/react', 5, 'intermediate', 30, FALSE),
('Leadership Essentials', 'Harvard Online', 'https://harvard.edu/leadership', 11, 'intermediate', 10, FALSE),
('Sales Negotiation Masterclass', 'LinkedIn Learning', 'https://linkedin.com/sales', 15, 'advanced', 6, FALSE),
('Financial Modeling in Excel', 'Corporate Finance Institute', 'https://corporatefinanceinstitute.com', 16, 'advanced', 20, FALSE);

-- Create admin user (password = admin123, will be hashed by Flask later, but for SQL we store dummy)
-- Actual password hashing done via Flask. We'll insert manually after app runs or use sample.
INSERT INTO users (email, password_hash, role) VALUES 
('admin@corporateskillgap.com', 'scrypt:32768:8:1$...', 'admin') ON DUPLICATE KEY UPDATE email=email;

-- Add sample employees (for CSV we generate separately, but minimal to start)
INSERT INTO employees (employee_code, first_name, last_name, email, department_id, job_role_id, joining_date, experience_years) VALUES
('EMP001', 'Rajesh', 'Kumar', 'rajesh.kumar@company.com', 1, 1, '2021-06-01', 3.5),
('EMP002', 'Priya', 'Sharma', 'priya.sharma@company.com', 1, 2, '2018-01-15', 6.0),
('EMP003', 'Amit', 'Verma', 'amit.verma@company.com', 3, 4, '2022-03-10', 1.8);

-- Assign employee skills
INSERT INTO employee_skills (employee_id, skill_id, proficiency_level) VALUES
(1, 1, 'intermediate'), (1, 3, 'beginner'),
(2, 1, 'advanced'), (2, 3, 'advanced'), (2, 6, 'intermediate'), (2, 11, 'beginner'),
(3, 15, 'advanced'), (3, 10, 'intermediate');

COMMIT;