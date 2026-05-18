# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from db import db
from models.user import User
from models.employee import Employee
from models.department import Department
from models.job_role import JobRole

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = db.func.current_timestamp()
            db.session.commit()
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('employee.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        employee_code = request.form.get('employee_code')
        department_id = request.form.get('department_id')
        job_role_id = request.form.get('job_role_id')

        try:
            # Validation
            if password != confirm:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('auth.register'))

            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('auth.register'))

            if Employee.query.filter_by(employee_code=employee_code).first():
                flash('Employee code already exists', 'danger')
                return redirect(url_for('auth.register'))

            # Create user
            user = User(email=email, role='employee')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # to get user.id

            # Create employee profile
            employee = Employee(
                user_id=user.id,
                employee_code=employee_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department_id=department_id if department_id else None,
                job_role_id=job_role_id if job_role_id else None
            )
            db.session.add(employee)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error('Registration error: %s', e)
            flash('Registration failed due to a server error. Please try again later.', 'danger')
            return redirect(url_for('auth.register'))

    try:
        departments = Department.query.all()
        job_roles = JobRole.query.all()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('Failed to load registration options: %s', e)
        flash('Unable to load registration options. Please contact the administrator.', 'danger')
        departments = []
        job_roles = []

    return render_template('register.html', departments=departments, job_roles=job_roles)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))