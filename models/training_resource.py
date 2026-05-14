# models/training_resource.py
from app import db

class TrainingResource(db.Model):
    __tablename__ = 'training_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100))
    url = db.Column(db.String(500))
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    difficulty_level = db.Column(db.Enum('beginner', 'intermediate', 'advanced'))
    duration_hours = db.Column(db.Integer)
    cost = db.Column(db.Numeric(10,2), default=0)
    description = db.Column(db.Text)
    is_free = db.Column(db.Boolean, default=True)
    
    # Relationship to employee recommendations
    employee_recommendations = db.relationship('EmployeeRecommendation', backref='training_resource', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Training {self.title}>'