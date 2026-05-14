# utils/chart_generator.py
"""
Chart Data Generator
Provides JSON data for frontend charts (department gaps, top missing skills, etc.)
"""

from db import db
from models.employee import Employee
from models.department import Department
from models.gap_analysis import GapAnalysis
from models.skill import Skill


def generate_department_gaps():
    """
    Calculate average gap score per department.
    
    Returns:
    dict: {'labels': [dept_names], 'values': [avg_gap_scores]}
    """
    departments = Department.query.all()
    labels = []
    avg_gaps = []
    
    for dept in departments:
        # Get all employees in this department
        employees = Employee.query.filter_by(department_id=dept.id).all()
        if not employees:
            labels.append(dept.name)
            avg_gaps.append(0)
            continue
        
        total_gap_sum = 0
        total_skills_count = 0
        
        for emp in employees:
            # Sum all gap scores for this employee
            gaps = GapAnalysis.query.filter_by(employee_id=emp.id).all()
            total_gap_sum += sum(g.gap_score for g in gaps)
            total_skills_count += len(gaps)
        
        avg = (total_gap_sum / total_skills_count) if total_skills_count > 0 else 0
        labels.append(dept.name)
        avg_gaps.append(round(avg, 2))
    
    return {'labels': labels, 'values': avg_gaps}


def generate_top_missing_skills(limit=5):
    """
    Find the skills that are most frequently missing or under-proficient (gap_score=2).
    
    Parameters:
    limit (int): Number of top skills to return.
    
    Returns:
    dict: {'labels': [skill_names], 'counts': [missing_counts]}
    """
    # Query gaps with major gap (score=2) and count per skill
    from sqlalchemy import func
    results = db.session.query(
        Skill.name,
        func.count(GapAnalysis.id).label('missing_count')
    ).join(GapAnalysis, GapAnalysis.skill_id == Skill.id) \
     .filter(GapAnalysis.gap_score == 2) \
     .group_by(Skill.id) \
     .order_by(func.count(GapAnalysis.id).desc()) \
     .limit(limit).all()
    
    labels = [r[0] for r in results]
    counts = [r[1] for r in results]
    
    return {'labels': labels, 'counts': counts}


def generate_readiness_distribution():
    """
    Group employees by readiness score percentage.
    
    Returns:
    dict: {
        'labels': ['0-25%', '26-50%', '51-75%', '76-100%'],
        'counts': [counts_in_each_range]
    }
    """
    employees = Employee.query.all()
    ranges = {
        '0-25%': 0,
        '26-50%': 0,
        '51-75%': 0,
        '76-100%': 0
    }
    
    for emp in employees:
        score = emp.get_readiness_score()
        if score <= 25:
            ranges['0-25%'] += 1
        elif score <= 50:
            ranges['26-50%'] += 1
        elif score <= 75:
            ranges['51-75%'] += 1
        else:
            ranges['76-100%'] += 1
    
    return {
        'labels': list(ranges.keys()),
        'counts': list(ranges.values())
    }


def generate_skill_coverage_by_department():
    """
    For each department, calculate the percentage of required skills owned by employees.
    (Bonus: Not used in main charts but available for future expansion)
    """
    # Placeholder – can be implemented similarly
    pass