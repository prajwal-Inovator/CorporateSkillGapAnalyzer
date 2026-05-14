# models/employee_skill.py
from db import db

class EmployeeSkill(db.Model):
    __tablename__ = 'employee_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    proficiency_level = db.Column(db.Enum('beginner', 'intermediate', 'advanced', 'expert'), default='beginner')
    years_of_experience = db.Column(db.Numeric(3,1), default=0)
    last_used_year = db.Column(db.Integer)
    certification = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    __table_args__ = (db.UniqueConstraint('employee_id', 'skill_id', name='unique_employee_skill'),)
    
    def __repr__(self):
        return f'<EmployeeSkill emp={self.employee_id} skill={self.skill_id}>'