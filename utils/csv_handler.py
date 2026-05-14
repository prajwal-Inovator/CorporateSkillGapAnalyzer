# utils/csv_handler.py
"""
CSV Handler
Import employee and skill data from CSV files.
Uses Python built-in csv parsing.
"""

import csv
from app import db
from models.employee import Employee
from models.department import Department
from models.job_role import JobRole
from models.skill import Skill
from models.user import User


def _read_csv_rows(filepath):
    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader if any((value or '').strip() for value in row.values())]


def process_employee_csv(filepath):
    """
    Import employees from a CSV file.
    
    Expected CSV columns:
    employee_code, first_name, last_name, email, department, job_role
    
    If department or job_role names match existing records, they are linked.
    Otherwise, the department/job_role fields are left NULL.
    
    Parameters:
    filepath (str): Path to the CSV file.
    
    Returns:
    dict: {'success': count, 'errors': count}
    """
    try:
        rows = _read_csv_rows(filepath)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {'success': 0, 'errors': 1}
    
    success = 0
    errors = 0
    
    for index, row in enumerate(rows, start=1):
        try:
            # Extract data
            emp_code = str(row['employee_code']).strip()
            first_name = str(row['first_name']).strip()
            last_name = str(row['last_name']).strip()
            email = str(row['email']).strip()
            dept_name = str(row.get('department') or '').strip() or None
            job_title = str(row.get('job_role') or '').strip() or None
            
            # Check if employee already exists (by email or employee_code)
            existing = Employee.query.filter(
                (Employee.email == email) | (Employee.employee_code == emp_code)
            ).first()
            if existing:
                print(f"Skipping duplicate employee: {emp_code} / {email}")
                errors += 1
                continue
            
            # Find or create department (optional – we don't auto-create, just match)
            department = None
            if dept_name:
                department = Department.query.filter_by(name=dept_name).first()
                if not department:
                    print(f"Department '{dept_name}' not found. Leaving NULL.")
            
            # Find job role
            job_role = None
            if job_title:
                job_role = JobRole.query.filter_by(title=job_title).first()
                if not job_role:
                    print(f"Job role '{job_title}' not found. Leaving NULL.")
            
            # Create a user account for the employee (default password = 'employee123')
            # Check if user already exists with same email
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email, role='employee')
                user.set_password('employee123')
                db.session.add(user)
                db.session.flush()  # get user.id
            
            # Create employee
            employee = Employee(
                user_id=user.id,
                employee_code=emp_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department_id=department.id if department else None,
                job_role_id=job_role.id if job_role else None
            )
            db.session.add(employee)
            success += 1
            
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            errors += 1
    
    db.session.commit()
    return {'success': success, 'errors': errors}


def process_skills_csv(filepath):
    """
    Import skills from a CSV file.
    
    Expected columns: name, category (category optional)
    
    Parameters:
    filepath (str): Path to the CSV file.
    
    Returns:
    dict: {'success': count, 'errors': count}
    """
    try:
        rows = _read_csv_rows(filepath)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {'success': 0, 'errors': 1}
    
    success = 0
    errors = 0
    
    for index, row in enumerate(rows, start=1):
        try:
            name = str(row.get('name') or '').strip()
            # Skip if skill already exists
            if Skill.query.filter_by(name=name).first():
                print(f"Skill '{name}' already exists, skipping.")
                errors += 1
                continue
            
            category = str(row.get('category') or '').strip() or 'General'
            skill = Skill(name=name, category=category)
            db.session.add(skill)
            success += 1
            
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            errors += 1
    
    db.session.commit()
    return {'success': success, 'errors': errors}


def process_employee_skills_csv(filepath):
    """
    Import employee skill mappings from CSV.
    
    Expected columns: employee_code, skill_name, proficiency_level
    
    Parameters:
    filepath (str): Path to the CSV file.
    
    Returns:
    dict: {'success': count, 'errors': count}
    """
    try:
        rows = _read_csv_rows(filepath)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {'success': 0, 'errors': 1}
    
    from models.employee_skill import EmployeeSkill
    
    success = 0
    errors = 0
    
    for index, row in enumerate(rows, start=1):
        try:
            emp_code = str(row.get('employee_code') or '').strip()
            skill_name = str(row.get('skill_name') or '').strip()
            proficiency = str(row.get('proficiency_level') or '').strip().lower()
            
            # Validate proficiency
            if proficiency not in ['beginner', 'intermediate', 'advanced', 'expert']:
                proficiency = 'beginner'
            
            # Find employee
            employee = Employee.query.filter_by(employee_code=emp_code).first()
            if not employee:
                print(f"Employee {emp_code} not found")
                errors += 1
                continue
            
            # Find skill
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                print(f"Skill {skill_name} not found")
                errors += 1
                continue
            
            # Check if mapping already exists
            existing = EmployeeSkill.query.filter_by(employee_id=employee.id, skill_id=skill.id).first()
            if existing:
                # Update proficiency
                existing.proficiency_level = proficiency
            else:
                new_map = EmployeeSkill(employee_id=employee.id, skill_id=skill.id, proficiency_level=proficiency)
                db.session.add(new_map)
            success += 1
            
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            errors += 1
    
    db.session.commit()
    return {'success': success, 'errors': errors}