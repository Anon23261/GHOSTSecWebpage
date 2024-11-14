"""
Forum models for GhostSec application.
"""
from . import db, datetime

class ForumCategory(db.Model):
    """Model for forum categories."""
    __tablename__ = 'forum_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    posts = db.relationship('ForumPost', backref='category', lazy=True)
    order = db.Column(db.Integer, default=0)

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

    def __repr__(self):
        return f"ForumPost('{self.title}', '{self.date_posted}')"

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

    def __repr__(self):
        return f"ForumComment('{self.content[:50]}...', '{self.date_posted}')"
