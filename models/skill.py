# models/skill.py
from db import db

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # Relationships
    employee_skills = db.relationship('EmployeeSkill', backref='skill', cascade='all, delete-orphan')
    role_required = db.relationship('RoleRequiredSkill', backref='skill', cascade='all, delete-orphan')
    training_resources = db.relationship('TrainingResource', backref='skill', lazy='dynamic')
    
    def __repr__(self):
        return f'<Skill {self.name}>'