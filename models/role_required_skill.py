# models/role_required_skill.py
from db import db

class RoleRequiredSkill(db.Model):
    __tablename__ = 'role_required_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    required_proficiency = db.Column(db.Enum('beginner', 'intermediate', 'advanced', 'expert'), default='intermediate')
    is_mandatory = db.Column(db.Boolean, default=True)
    weight = db.Column(db.Integer, default=1)
    
    __table_args__ = (db.UniqueConstraint('job_role_id', 'skill_id', name='unique_role_skill'),)
    
    def __repr__(self):
        return f'<RoleRequired role={self.job_role_id} skill={self.skill_id}>'