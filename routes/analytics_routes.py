# routes/analytics_routes.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models.employee import Employee
from utils.chart_generator import generate_department_gaps, generate_top_missing_skills, generate_readiness_distribution

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('analytics.html')

@analytics_bp.route('/data/department_gaps')
@login_required
def department_gaps():
    try:
        data = generate_department_gaps()
        return jsonify(data)
    except Exception as e:
        return jsonify({'labels': ['No data'], 'values': [0], 'error': str(e)}), 200

@analytics_bp.route('/data/top_missing_skills')
@login_required
def top_missing_skills():
    try:
        data = generate_top_missing_skills()
        return jsonify(data)
    except Exception as e:
        return jsonify({'labels': ['No data'], 'counts': [0], 'error': str(e)}), 200

@analytics_bp.route('/data/readiness_distribution')
@login_required
def readiness_distribution():
    try:
        data = generate_readiness_distribution()
        return jsonify(data)
    except Exception as e:
        return jsonify({'labels': ['No data'], 'counts': [1], 'error': str(e)}), 200
