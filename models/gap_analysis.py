# models/gap_analysis.py
from db import db

class GapAnalysis(db.Model):
    __tablename__ = 'gap_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    required_proficiency = db.Column(db.String(20))
    current_proficiency = db.Column(db.String(20))
    gap_score = db.Column(db.Integer)  # 0=no gap,1=minor,2=major
    analysis_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    __table_args__ = (db.Index('idx_employee', 'employee_id'),)
    
    def __repr__(self):
        return f'<GapAnalysis emp={self.employee_id} skill={self.skill_id} gap={self.gap_score}>'