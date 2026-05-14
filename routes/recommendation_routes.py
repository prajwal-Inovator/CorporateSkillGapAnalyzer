# routes/recommendation_routes.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models.employee import Employee
from models.training_resource import TrainingResource
from models.employee_recommendation import EmployeeRecommendation
from utils.recommendation_engine import generate_recommendations_for_employee

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/my_recommendations')
@login_required
def my_recommendations():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash('Employee profile not found', 'danger')
        return redirect(url_for('index'))
    
    recommendations = employee.recommendations.all()
    return render_template('recommendations.html', recommendations=recommendations)

@recommendation_bp.route('/generate/<int:employee_id>')
@login_required
def generate(employee_id):
    if current_user.role != 'admin':
        flash('Only admin can generate recommendations', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    employee = Employee.query.get_or_404(employee_id)
    generate_recommendations_for_employee(employee.id)
    flash('Recommendations generated', 'success')
    return redirect(url_for('admin.employees'))

@recommendation_bp.route('/complete/<int:rec_id>')
@login_required
def complete(rec_id):
    rec = EmployeeRecommendation.query.get_or_404(rec_id)
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if rec.employee_id != employee.id and current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    rec.status = 'completed'
    db.session.commit()
    flash('Training marked as completed', 'success')
    return redirect(url_for('recommendation.my_recommendations'))