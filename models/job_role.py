# models/job_role.py
from app import db

class JobRole(db.Model):
    __tablename__ = 'job_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    description = db.Column(db.Text)
    min_experience_years = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    employees = db.relationship('Employee', backref='job_role', lazy='dynamic')
    required_skills = db.relationship('RoleRequiredSkill', backref='job_role', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<JobRole {self.title}>'