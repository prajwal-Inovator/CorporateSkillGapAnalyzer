# models/department.py
from app import db

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    employees = db.relationship('Employee', backref='department', lazy='dynamic')
    job_roles = db.relationship('JobRole', backref='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'