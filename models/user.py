"""
User models for GhostSec application.
"""
from . import db, UserMixin, datetime, jwt, time, Optional

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
