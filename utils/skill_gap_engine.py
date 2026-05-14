# utils/skill_gap_engine.py
"""
Skill Gap Calculation Engine
Computes missing skills and gap scores for each employee.
"""

from db import db
from models.employee import Employee
from models.role_required_skill import RoleRequiredSkill
from models.employee_skill import EmployeeSkill
from models.gap_analysis import GapAnalysis


def calculate_gap_for_employee(employee_id):
    """
    Calculate skill gaps for a single employee and store in gap_analysis table.
    
    Parameters:
    employee_id (int): The ID of the employee.
    
    Returns:
    None
    """
    # Get the employee record
    employee = Employee.query.get(employee_id)
    
    # If employee doesn't exist or has no job role assigned, exit
    if not employee or not employee.job_role_id:
        print(f"Employee {employee_id} has no job role. Skipping gap calculation.")
        return
    
    # Clear any existing gap records for this employee (start fresh)
    GapAnalysis.query.filter_by(employee_id=employee_id).delete()
    
    # Get all required skills for this employee's job role
    required_skills = RoleRequiredSkill.query.filter_by(job_role_id=employee.job_role_id).all()
    
    # Build a dictionary of employee's current skills: {skill_id: proficiency_level}
    employee_skills_dict = {}
    for es in employee.employee_skills:
        employee_skills_dict[es.skill_id] = es.proficiency_level
    
    # Define order for proficiency levels (higher number = better)
    proficiency_order = {
        'beginner': 1,
        'intermediate': 2,
        'advanced': 3,
        'expert': 4
    }
    
    # For each required skill, calculate the gap
    for req in required_skills:
        # Get employee's current proficiency (if any)
        current_proficiency = employee_skills_dict.get(req.skill_id, None)
        current_level = proficiency_order.get(current_proficiency, 0)  # 0 if skill not owned
        required_level = proficiency_order.get(req.required_proficiency, 2)  # default intermediate = 2
        
        # Gap is the difference (cannot be negative)
        gap = max(0, required_level - current_level)
        
        # Convert gap into a score:
        # 0 = no gap, 1 = minor gap (1 level difference), 2 = major gap (2+ levels)
        if gap == 0:
            gap_score = 0
        elif gap == 1:
            gap_score = 1
        else:
            gap_score = 2
        
        # Create a new gap analysis record
        analysis = GapAnalysis(
            employee_id=employee_id,
            skill_id=req.skill_id,
            required_proficiency=req.required_proficiency,
            current_proficiency=current_proficiency if current_proficiency else 'none',
            gap_score=gap_score
        )
        db.session.add(analysis)
    
    # Save all changes to the database
    db.session.commit()
    print(f"Gap analysis completed for employee {employee_id}")


def calculate_all_gaps():
    """
    Calculate skill gaps for every employee in the company.
    Useful for batch processing or scheduled jobs.
    
    Returns:
    None
    """
    employees = Employee.query.all()
    for emp in employees:
        calculate_gap_for_employee(emp.id)
    print(f"Gap calculation completed for {len(employees)} employees.")