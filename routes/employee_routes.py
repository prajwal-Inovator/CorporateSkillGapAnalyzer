# routes/employee_routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models.employee import Employee
from models.employee_skill import EmployeeSkill
from models.skill import Skill
from models.role_required_skill import RoleRequiredSkill

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash('Employee profile not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get gap summary
    readiness_score = employee.get_readiness_score()
    total_required = RoleRequiredSkill.query.filter_by(job_role_id=employee.job_role_id).count()
    owned_skills = EmployeeSkill.query.filter_by(employee_id=employee.id).count()
    missing = total_required - owned_skills
    
    recent_recommendations = employee.recommendations[:5]
    
    return render_template('employee_dashboard.html',
                          employee=employee,
                          readiness_score=readiness_score,
                          total_required=total_required,
                          owned_skills=owned_skills,
                          missing_skills=missing,
                          recommendations=recent_recommendations)

@employee_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    employee = Employee.query.filter_by(user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        employee.first_name = request.form.get('first_name')
        employee.last_name = request.form.get('last_name')
        employee.phone = request.form.get('phone')
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('employee.profile'))
    return render_template('profile.html', employee=employee)

@employee_bp.route('/my_skills', methods=['GET', 'POST'])
@login_required
def my_skills():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        skill_id = request.form.get('skill_id')
        proficiency = request.form.get('proficiency')
        existing = EmployeeSkill.query.filter_by(employee_id=employee.id, skill_id=skill_id).first()
        if existing:
            existing.proficiency_level = proficiency
        else:
            new_skill = EmployeeSkill(employee_id=employee.id, skill_id=skill_id, proficiency_level=proficiency)
            db.session.add(new_skill)
        db.session.commit()
        flash('Skill updated', 'success')
        return redirect(url_for('employee.my_skills'))
    
    all_skills = Skill.query.all()
    employee_skill_ids = [es.skill_id for es in employee.employee_skills]
    return render_template('my_skills.html', all_skills=all_skills, employee_skills=employee.employee_skills, employee_skill_ids=employee_skill_ids)