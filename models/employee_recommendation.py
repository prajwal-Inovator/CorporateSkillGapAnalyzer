# models/employee_recommendation.py
from db import db

class EmployeeRecommendation(db.Model):
    __tablename__ = 'employee_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    training_resource_id = db.Column(db.Integer, db.ForeignKey('training_resources.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'completed', 'ignored'), default='pending')
    recommended_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Recommendation emp={self.employee_id} resource={self.training_resource_id}>'