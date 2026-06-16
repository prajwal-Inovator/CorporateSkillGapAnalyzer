# models/employee.py
import difflib
from db import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
    employee_code = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'))
    joining_date = db.Column(db.Date)
    experience_years = db.Column(db.Numeric(4,1), default=0)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    profile_pic = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Self-referential relationship for manager
    manager = db.relationship('Employee', remote_side=[id], backref='subordinates')
    
    # Relationships
    employee_skills = db.relationship('EmployeeSkill', backref='employee', cascade='all, delete-orphan')
    gap_analyses = db.relationship('GapAnalysis', backref='employee', cascade='all, delete-orphan')
    recommendations = db.relationship('EmployeeRecommendation', backref='employee', cascade='all, delete-orphan')
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_readiness_score(self):
        """Calculate skill readiness percentage based on required vs owned skills"""
        if not self.job_role_id:
            return 0
        from models.role_required_skill import RoleRequiredSkill
        from models.employee_skill import EmployeeSkill
        
        required_skills = RoleRequiredSkill.query.filter_by(job_role_id=self.job_role_id).all()
        if not required_skills:
            required_skills = self._get_fallback_required_skills()
        if not required_skills:
            return 100

        required_skill_ids = [rs.skill_id for rs in required_skills]
        if not required_skill_ids:
            return 100

        try:
            owned_skills = EmployeeSkill.query.filter_by(employee_id=self.id).filter(EmployeeSkill.skill_id.in_(required_skill_ids)).count()
        except Exception:
            return 0

        return round((owned_skills / len(required_skills)) * 100, 1)

    def _get_fallback_required_skills(self):
        from models.role_required_skill import RoleRequiredSkill
        from models.job_role import JobRole
        import difflib

        if not self.job_role or not self.job_role.title:
            return []

        title = self.job_role.title.strip()
        if not title:
            return []

        candidate_roles = JobRole.query.join(RoleRequiredSkill).group_by(JobRole.id).all()
        if not candidate_roles:
            return []

        titles = [role.title for role in candidate_roles]
        lower_titles = [t.lower() for t in titles]
        matches = difflib.get_close_matches(title.lower(), lower_titles, n=1, cutoff=0.4)
        if matches:
            matched_title = next((t for t in titles if t.lower() == matches[0]), None)
            if matched_title:
                fallback_role = next((role for role in candidate_roles if role.title == matched_title), None)
                if fallback_role:
                    return RoleRequiredSkill.query.filter_by(job_role_id=fallback_role.id).all()

        for role in candidate_roles:
            role_title_lower = role.title.lower()
            if title.lower() in role_title_lower or role_title_lower in title.lower():
                return RoleRequiredSkill.query.filter_by(job_role_id=role.id).all()

        return []
    
    def __repr__(self):
        return f'<Employee {self.employee_code}>'