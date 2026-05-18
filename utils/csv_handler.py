# utils/csv_handler.py
"""
CSV Handler
Import employee and skill data from CSV files.
Uses Python built-in csv parsing.
"""

import csv
from db import db
from models.employee import Employee
from models.department import Department
from models.job_role import JobRole
from models.skill import Skill
from models.training_resource import TrainingResource
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
            
            # Find or create department
            department = None
            if dept_name:
                department = Department.query.filter_by(name=dept_name).first()
                if not department:
                    department = Department(name=dept_name)
                    db.session.add(department)
                    db.session.flush()

            # Find or create job role
            job_role = None
            if job_title:
                job_role = JobRole.query.filter_by(title=job_title).first()
                if not job_role:
                    job_role = JobRole(title=job_title, department_id=department.id if department else None)
                    db.session.add(job_role)
                    db.session.flush()
            
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
            if not name:
                raise ValueError('Missing skill name')

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


def process_job_roles_csv(filepath):
    """
    Import job roles from a CSV file.

    Expected columns: title, department, description, min_experience_years
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
            title = str(row.get('title') or '').strip()
            if not title:
                raise ValueError('Missing job role title')

            if JobRole.query.filter_by(title=title).first():
                print(f"Job role '{title}' already exists, skipping.")
                errors += 1
                continue

            department_name = str(row.get('department') or '').strip() or None
            department = None
            if department_name:
                department = Department.query.filter_by(name=department_name).first()
                if not department:
                    department = Department(name=department_name)
                    db.session.add(department)
                    db.session.flush()

            description = str(row.get('description') or '').strip() or None
            min_exp = row.get('min_experience_years')
            min_experience_years = int(min_exp) if min_exp and str(min_exp).isdigit() else 0

            job_role = JobRole(
                title=title,
                department_id=department.id if department else None,
                description=description,
                min_experience_years=min_experience_years
            )
            db.session.add(job_role)
            success += 1

        except Exception as e:
            print(f"Error processing row {index}: {e}")
            errors += 1

    db.session.commit()
    return {'success': success, 'errors': errors}


def process_role_required_skills_csv(filepath):
    """
    Import role required skills from a CSV file.

    Expected columns: job_role, skill, required_proficiency, is_mandatory, weight
    """
    try:
        rows = _read_csv_rows(filepath)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {'success': 0, 'errors': 1}

    from models.role_required_skill import RoleRequiredSkill

    success = 0
    errors = 0

    for index, row in enumerate(rows, start=1):
        try:
            job_title = str(row.get('job_role') or row.get('job_role_title') or '').strip()
            skill_name = str(row.get('skill') or row.get('skill_name') or '').strip()
            if not job_title or not skill_name:
                raise ValueError('Missing job role or skill name')

            job_role = JobRole.query.filter_by(title=job_title).first()
            skill = Skill.query.filter_by(name=skill_name).first()
            if not job_role or not skill:
                raise ValueError('Job role or skill not found')

            required_proficiency = str(row.get('required_proficiency') or '').strip().lower()
            if required_proficiency not in ['beginner', 'intermediate', 'advanced', 'expert']:
                required_proficiency = 'intermediate'

            is_mandatory_str = str(row.get('is_mandatory') or '').strip().lower()
            is_mandatory = is_mandatory_str in ['true', '1', 'yes', 'y']

            weight_value = row.get('weight')
            weight = int(weight_value) if weight_value and str(weight_value).isdigit() else 1

            existing = RoleRequiredSkill.query.filter_by(job_role_id=job_role.id, skill_id=skill.id).first()
            if existing:
                existing.required_proficiency = required_proficiency
                existing.is_mandatory = is_mandatory
                existing.weight = weight
            else:
                new_role_skill = RoleRequiredSkill(
                    job_role_id=job_role.id,
                    skill_id=skill.id,
                    required_proficiency=required_proficiency,
                    is_mandatory=is_mandatory,
                    weight=weight,
                )
                db.session.add(new_role_skill)
            success += 1

        except Exception as e:
            print(f"Error processing row {index}: {e}")
            errors += 1

    db.session.commit()
    return {'success': success, 'errors': errors}


def process_training_resources_csv(filepath):
    """
    Import training resources from a CSV file.

    Expected columns: title, provider, url, skill, difficulty_level, duration_hours, cost, description, is_free
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
            title = str(row.get('title') or '').strip()
            if not title:
                raise ValueError('Missing training resource title')

            provider = str(row.get('provider') or '').strip() or None
            url = str(row.get('url') or '').strip() or None
            skill_name = str(row.get('skill') or '').strip() or None
            difficulty_level = str(row.get('difficulty_level') or '').strip().lower()
            if difficulty_level not in ['beginner', 'intermediate', 'advanced']:
                difficulty_level = None

            duration_hours = row.get('duration_hours')
            duration_hours = int(duration_hours) if duration_hours and str(duration_hours).isdigit() else None
            cost_value = row.get('cost')
            try:
                cost = float(cost_value) if cost_value else 0
            except ValueError:
                cost = 0

            description = str(row.get('description') or '').strip() or None
            is_free = str(row.get('is_free') or '').strip().lower() in ['true', '1', 'yes', 'y']

            skill = None
            if skill_name:
                skill = Skill.query.filter_by(name=skill_name).first()
                if not skill:
                    print(f"Skill '{skill_name}' not found for resource '{title}'")

            training = TrainingResource(
                title=title,
                provider=provider,
                url=url,
                skill_id=skill.id if skill else None,
                difficulty_level=difficulty_level,
                duration_hours=duration_hours,
                cost=cost,
                description=description,
                is_free=is_free,
            )
            db.session.add(training)
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