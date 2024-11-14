"""
Project models for GhostSec application.
"""
from . import db, datetime

class Project(db.Model):
    """Model for collaborative projects."""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repository_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')
    is_public = db.Column(db.Boolean, default=True)
    members = db.relationship('ProjectMember', backref='project', lazy=True)
    
    def __repr__(self):
        return f"Project('{self.name}', Owner: '{self.owner_id}')"

class ProjectMember(db.Model):
    """Model for project members."""
    __tablename__ = 'project_member'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='member')
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"ProjectMember(Project: '{self.project_id}', User: '{self.user_id}', Role: '{self.role}')"
