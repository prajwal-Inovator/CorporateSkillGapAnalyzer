# routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from db import db
from models.employee import Employee
from models.department import Department
from models.job_role import JobRole
from models.skill import Skill
from models.user import User
from models.employee_skill import EmployeeSkill

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    """Decorator to restrict access to admin users"""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_employees = Employee.query.count()
    total_skills = Skill.query.count()
    total_departments = Department.query.count()
    total_job_roles = JobRole.query.count()
    total_employee_skills = EmployeeSkill.query.count()
    recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()

    repo_datasets_loaded = all([
        total_employees > 0,
        total_skills > 0,
        total_job_roles > 0,
        total_employee_skills > 0,
    ])
    return render_template('admin_dashboard.html',
                          total_employees=total_employees,
                          total_skills=total_skills,
                          total_departments=total_departments,
                          total_job_roles=total_job_roles,
                          total_employee_skills=total_employee_skills,
                          repo_datasets_loaded=repo_datasets_loaded,
                          recent_employees=recent_employees)

@admin_bp.route('/employees')
@login_required
@admin_required
def employees():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    per_page = 10

    query = Employee.query
    if search_query:
        query = query.filter(
            or_(
                Employee.employee_code.ilike(f'%{search_query}%'),
                Employee.first_name.ilike(f'%{search_query}%'),
                Employee.last_name.ilike(f'%{search_query}%'),
                Employee.email.ilike(f'%{search_query}%')
            )
        )

    employees = query.order_by(Employee.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('employees.html', employees=employees, search_query=search_query)

@admin_bp.route('/add_employee', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    if request.method == 'POST':
        # Extract form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        employee_code = request.form.get('employee_code')
        department_id = request.form.get('department_id')
        job_role_id = request.form.get('job_role_id')
        phone = request.form.get('phone')
        joining_date = request.form.get('joining_date')
        
        # Create user account for employee (default password = employee123)
        user = User(email=email, role='employee')
        user.set_password('employee123')
        db.session.add(user)
        db.session.flush()
        
        employee = Employee(
            user_id=user.id,
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department_id=department_id if department_id else None,
            job_role_id=job_role_id if job_role_id else None,
            joining_date=joining_date if joining_date else None
        )
        db.session.add(employee)
        db.session.commit()
        flash('Employee added successfully', 'success')
        return redirect(url_for('admin.employees'))
    
    departments = Department.query.all()
    job_roles = JobRole.query.all()
    return render_template('add_employee.html', departments=departments, job_roles=job_roles)

@admin_bp.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        employee.first_name = request.form.get('first_name')
        employee.last_name = request.form.get('last_name')
        employee.email = request.form.get('email')
        employee.phone = request.form.get('phone')
        employee.department_id = request.form.get('department_id') or None
        employee.job_role_id = request.form.get('job_role_id') or None
        joining_date = request.form.get('joining_date')
        employee.joining_date = joining_date if joining_date else None
        try:
            db.session.commit()
            flash('Employee updated', 'success')
        except Exception:
            db.session.rollback()
            flash('Failed to update employee. Please check the data and try again.', 'danger')
            return redirect(url_for('admin.edit_employee', id=id))
        return redirect(url_for('admin.employees'))
    
    departments = Department.query.all()
    job_roles = JobRole.query.all()
    return render_template('edit_employee.html', employee=employee, departments=departments, job_roles=job_roles)

@admin_bp.route('/delete_employee/<int:id>')
@login_required
@admin_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    if employee.user:
        db.session.delete(employee.user)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted', 'success')
    return redirect(url_for('admin.employees'))

@admin_bp.route('/skills')
@login_required
@admin_required
def skills():
    skills = Skill.query.all()
    return render_template('skills.html', skills=skills)

@admin_bp.route('/add_skill', methods=['POST'])
@login_required
@admin_required
def add_skill():
    name = request.form.get('name')
    category = request.form.get('category')
    if name and not Skill.query.filter_by(name=name).first():
        skill = Skill(name=name, category=category)
        db.session.add(skill)
        db.session.commit()
        flash('Skill added', 'success')
    else:
        flash('Skill already exists or invalid', 'danger')
    return redirect(url_for('admin.skills'))

@admin_bp.route('/delete_skill/<int:id>')
@login_required
@admin_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted', 'success')
    return redirect(url_for('admin.skills'))