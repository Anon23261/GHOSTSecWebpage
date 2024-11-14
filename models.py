"""Database models for GhostSec application."""
from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import jwt
from time import time
from typing import Optional
from sqlalchemy.ext.associationproxy import association_proxy

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
    github_username = db.Column(db.String(50))
    discord_id = db.Column(db.String(50))
    website = db.Column(db.String(200))
    location = db.Column(db.String(100))
    
    # Social fields
    status = db.Column(db.String(50), default='offline')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    labs = db.relationship('LabInstance', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)
    posts = db.relationship('ForumPost', backref='author', lazy=True)
    comments = db.relationship('ForumComment', backref='author', lazy=True)
    projects = db.relationship('Project', backref='owner', lazy=True)
    
    # Followers/Following relationship
    following = db.relationship(
        'User', secondary='followers',
        primaryjoin=('followers.c.follower_id == User.id'),
        secondaryjoin=('followers.c.followed_id == User.id'),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

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

    def follow(self, user):
        """Follow another user."""
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        """Unfollow a user."""
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        """Check if following a user."""
        return self.following.filter(
            followers.c.followed_id == user.id).count() > 0

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}')"

# Association table for followers
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class ForumCategory(db.Model):
    """Model for forum categories."""
    __tablename__ = 'forum_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    posts = db.relationship('ForumPost', backref='category', lazy=True)

class ForumPost(db.Model):
    """Model for forum posts."""
    __tablename__ = 'forum_post'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_category.id'), nullable=False)
    comments = db.relationship('ForumComment', backref='post', lazy=True)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)

class ForumComment(db.Model):
    """Model for forum comments."""
    __tablename__ = 'forum_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('forum_comment.id'))
    likes = db.Column(db.Integer, default=0)
    replies = db.relationship('ForumComment', backref=db.backref('parent', remote_side=[id]), lazy=True)

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

class ProjectMember(db.Model):
    """Model for project members."""
    __tablename__ = 'project_member'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='member')
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

class ChatRoom(db.Model):
    """Model for chat rooms."""
    __tablename__ = 'chat_room'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    is_private = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='room', lazy=True)
    members = db.relationship('ChatMember', backref='room', lazy=True)

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

class ChatMember(db.Model):
    """Model for chat room members."""
    __tablename__ = 'chat_member'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_read = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)

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

class Achievement(db.Model):
    """Model for user achievements and badges."""
    __tablename__ = 'achievement'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)
    badge_image = db.Column(db.String(20))
    category = db.Column(db.String(50))
    points = db.Column(db.Integer, default=0)
