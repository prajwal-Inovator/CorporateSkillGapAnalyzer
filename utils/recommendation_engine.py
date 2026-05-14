# utils/recommendation_engine.py
"""
Recommendation Engine
Suggests training resources to employees for skills they are missing.
"""

from app import db
from models.gap_analysis import GapAnalysis
from models.training_resource import TrainingResource
from models.employee_recommendation import EmployeeRecommendation
from utils.skill_gap_engine import calculate_gap_for_employee


def generate_recommendations_for_employee(employee_id):
    """
    Generate training recommendations for a single employee based on skill gaps.
    
    Steps:
    1. Ensure gaps are up-to-date.
    2. Find all gaps with gap_score >= 1 (minor or major).
    3. For each such skill, find training resources (up to 2 per skill).
    4. Create EmployeeRecommendation records if not already existing.
    
    Parameters:
    employee_id (int): The employee ID.
    
    Returns:
    int: Number of new recommendations created.
    """
    # First, recalculate gaps to ensure we have the latest data
    calculate_gap_for_employee(employee_id)
    
    # Get all gaps for this employee where gap_score > 0 (i.e., missing or insufficient skill)
    gaps = GapAnalysis.query.filter_by(employee_id=employee_id).filter(GapAnalysis.gap_score >= 1).all()
    
    new_recommendations_count = 0
    
    for gap in gaps:
        # Find training resources for this skill
        trainings = TrainingResource.query.filter_by(skill_id=gap.skill_id).limit(2).all()
        
        for training in trainings:
            # Check if this recommendation already exists for this employee
            existing = EmployeeRecommendation.query.filter_by(
                employee_id=employee_id,
                training_resource_id=training.id
            ).first()
            
            if not existing:
                # Create new recommendation
                rec = EmployeeRecommendation(
                    employee_id=employee_id,
                    training_resource_id=training.id,
                    status='pending'
                )
                db.session.add(rec)
                new_recommendations_count += 1
    
    db.session.commit()
    print(f"Generated {new_recommendations_count} new recommendations for employee {employee_id}")
    return new_recommendations_count


def generate_recommendations_for_all():
    """
    Generate training recommendations for every employee.
    Useful for batch processing.
    
    Returns:
    dict: Summary of recommendations generated per employee.
    """
    from models.employee import Employee
    employees = Employee.query.all()
    summary = {}
    for emp in employees:
        count = generate_recommendations_for_employee(emp.id)
        summary[emp.id] = count
    return summary