"""Database models for GhostSec application."""
from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import jwt
from time import time
from typing import Optional

@login_manager.user_loader
def load_user(user_id: str) -> Optional['User']:
    """Load user by ID."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User model for authentication and profile management."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Profile fields
    bio = db.Column(db.String(500))
    avatar = db.Column(db.String(20), default='default.jpg')
    skill_level = db.Column(db.String(20), default='beginner')
    points = db.Column(db.Integer, default=0)
    
    # Relationships
    posts = db.relationship('ForumPost', backref='author', lazy=True)
    comments = db.relationship('ForumComment', backref='author', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)

    def get_reset_token(self, expires_in: int = 600) -> str:
        """Generate password reset token."""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            db.app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token: str) -> Optional['User']:
        """Verify password reset token."""
        try:
            id = jwt.decode(token, db.app.config['SECRET_KEY'],
                          algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}')"

class ForumPost(db.Model):
    """Model for forum posts."""
    __tablename__ = 'forum_post'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    comments = db.relationship('ForumComment', backref='post', lazy=True)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)

class ForumComment(db.Model):
    """Model for forum comments."""
    __tablename__ = 'forum_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)

class Achievement(db.Model):
    """Model for user achievements and badges."""
    __tablename__ = 'achievement'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)
    badge_image = db.Column(db.String(20))
    points = db.Column(db.Integer, default=0)
