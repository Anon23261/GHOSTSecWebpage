"""
Lab models for GhostSec application.
"""
from . import db, datetime

class LabInstance(db.Model):
    """Model for tracking lab instances."""
    __tablename__ = 'lab_instance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lab_type = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='running')
    container_id = db.Column(db.String(64))
    score = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f"LabInstance(User: '{self.user_id}', Type: '{self.lab_type}', Status: '{self.status}')"

class Report(db.Model):
    """Model for lab completion reports."""
    __tablename__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lab_instance_id = db.Column(db.Integer, db.ForeignKey('lab_instance.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.JSON)
    grade = db.Column(db.String(2))
    feedback = db.Column(db.Text)
    
    def __repr__(self):
        return f"Report(User: '{self.user_id}', Lab: '{self.lab_instance_id}', Grade: '{self.grade}')"
