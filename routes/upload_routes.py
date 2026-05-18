# routes/upload_routes.py
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from db import db
from models.employee import Employee
from models.skill import Skill
from models.employee_skill import EmployeeSkill
from models.department import Department
from models.job_role import JobRole
from utils.csv_handler import (
    process_employee_csv,
    process_skills_csv,
    process_employee_skills_csv,
    process_job_roles_csv,
    process_role_required_skills_csv,
    process_training_resources_csv,
)

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    if current_user.role != 'admin':
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process based on file type
            lower_name = filename.lower()
            if 'employee_skills' in lower_name:
                result = process_employee_skills_csv(filepath)
                flash(f'Employee skills imported: {result["success"]} added, {result["errors"]} errors', 'success')
            elif 'role_required_skills' in lower_name:
                result = process_role_required_skills_csv(filepath)
                flash(f'Role required skills imported: {result["success"]} added, {result["errors"]} errors', 'success')
            elif 'training_resources' in lower_name:
                result = process_training_resources_csv(filepath)
                flash(f'Training resources imported: {result["success"]} added, {result["errors"]} errors', 'success')
            elif 'job_roles' in lower_name:
                result = process_job_roles_csv(filepath)
                flash(f'Job roles imported: {result["success"]} added, {result["errors"]} errors', 'success')
            elif 'skills' in lower_name and 'role_required_skills' not in lower_name:
                result = process_skills_csv(filepath)
                flash(f'Skills imported: {result["success"]} added, {result["errors"]} errors', 'success')
            elif 'employee' in lower_name and 'employee_skills' not in lower_name:
                result = process_employee_csv(filepath)
                flash(f'Employees imported: {result["success"]} added, {result["errors"]} errors', 'success')
            else:
                flash('Unrecognized CSV type. Use filename containing one of: employee, skills, job_roles, employee_skills, role_required_skills, training_resources', 'warning')
            os.remove(filepath)
            return redirect(url_for('admin.employees'))
        else:
            flash('Only CSV files allowed', 'danger')
    return render_template('upload_csv.html')