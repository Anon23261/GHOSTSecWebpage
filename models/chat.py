"""
Chat models for GhostSec application.
"""
from . import db, datetime

class ChatRoom(db.Model):
    """Model for chat rooms."""
    __tablename__ = 'chat_room'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    is_private = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='room', lazy=True)
    members = db.relationship('ChatMember', backref='room', lazy=True)
    
    def __repr__(self):
        return f"ChatRoom('{self.name}', Private: {self.is_private})"

class ChatMessage(db.Model):
    """Model for chat messages."""
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_type = db.Column(db.String(20), default='text')
    file_url = db.Column(db.String(200))
    
    def __repr__(self):
        return f"ChatMessage(Room: '{self.room_id}', Sender: '{self.sender_id}')"

class ChatMember(db.Model):
    """Model for chat room members."""
    __tablename__ = 'chat_member'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_read = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"ChatMember(Room: '{self.room_id}', User: '{self.user_id}')"
