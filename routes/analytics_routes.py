# routes/analytics_routes.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app import db
from models.employee import Employee
from models.skill import Skill
from models.employee_skill import EmployeeSkill
from models.role_required_skill import RoleRequiredSkill
from utils.chart_generator import generate_department_gaps, generate_top_missing_skills

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('analytics.html')

@analytics_bp.route('/data/department_gaps')
@login_required
def department_gaps():
    data = generate_department_gaps()
    return jsonify(data)

@analytics_bp.route('/data/top_missing_skills')
@login_required
def top_missing_skills():
    data = generate_top_missing_skills()
    return jsonify(data)

@analytics_bp.route('/data/readiness_distribution')
@login_required
def readiness_distribution():
    employees = Employee.query.all()
    readiness = [emp.get_readiness_score() for emp in employees]
    return jsonify({
        'labels': ['0-25%', '26-50%', '51-75%', '76-100%'],
        'counts': [
            sum(1 for r in readiness if r <= 25),
            sum(1 for r in readiness if 26 <= r <= 50),
            sum(1 for r in readiness if 51 <= r <= 75),
            sum(1 for r in readiness if r >= 76)
        ]
    })