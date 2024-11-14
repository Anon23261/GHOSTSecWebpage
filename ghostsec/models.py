from datetime import datetime
from ghostsec import db, login_manager, bcrypt
from flask_login import UserMixin
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from base64 import urlsafe_b64encode
from dotenv import load_dotenv
import os
import secrets

# Load environment variables
load_dotenv()

# Generate a proper Fernet key if not exists
def get_encryption_key():
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        # Generate a new key
        key = urlsafe_b64encode(secrets.token_bytes(32)).decode()
        # Save to .env file
        with open('.env', 'a') as f:
            f.write(f"\nENCRYPTION_KEY={key}")
    return key.encode()

# Initialize encryption
ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    account_type = db.Column(db.String(20), nullable=False, default='user')
    is_verified = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # OAuth fields
    github_id = db.Column(db.String(120), unique=True, nullable=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    
    # Profile fields
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    country = db.Column(db.String(50), nullable=True)
    phone_number = db.Column(db.String(200), nullable=True)  # Encrypted
    
    # Social media
    twitter = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(100), nullable=True)
    github = db.Column(db.String(100), nullable=True)
    
    # Two-factor authentication
    two_factor_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    
    # Account status
    reputation_points = db.Column(db.Integer, default=0)
    
    # Relationships
    posts = db.relationship('ForumPost', backref='author', lazy=True)
    comments = db.relationship('ForumComment', backref='author', lazy=True)
    ctf_scores = db.relationship('CTFScore', backref='user', lazy=True)
    learning_progress = db.relationship('LearningProgress', backref='user', lazy=True)
    marketplace_items = db.relationship('MarketplaceItem', backref='seller', lazy=True)
    orders = db.relationship('Order', backref='buyer', lazy=True)
    news_comments = db.relationship('NewsComment', backref='author', lazy=True)
    
    # Learning progress
    ctf_points = db.Column(db.Integer, default=0)
    python_points = db.Column(db.Integer, default=0)
    kali_points = db.Column(db.Integer, default=0)
    malware_points = db.Column(db.Integer, default=0)
    pentest_points = db.Column(db.Integer, default=0)
    cpp_points = db.Column(db.Integer, default=0)
    total_achievements = db.Column(db.Integer, default=0)
    skill_level = db.Column(db.String(20), default='Beginner')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return bcrypt.check_password_hash(self.password, password)
    
    def get_reset_token(self):
        """Generate a password reset token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token):
        """Verify a password reset token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def encrypt_data(self, data):
        if data:
            return cipher_suite.encrypt(data.encode()).decode()
        return None

    def decrypt_data(self, encrypted_data):
        if encrypted_data:
            try:
                return cipher_suite.decrypt(encrypted_data.encode()).decode()
            except:
                return None
        return None

    def set_phone_number(self, phone):
        self.phone_number = self.encrypt_data(phone)

    def get_phone_number(self):
        return self.decrypt_data(self.phone_number)

    def set_card_details(self, card_number, expiry):
        self.card_number = self.encrypt_data(card_number)
        self.card_expiry = self.encrypt_data(expiry)

    def get_card_details(self):
        """Safely retrieve card details"""
        return {
            'number': self.decrypt_data(self.card_number),
            'expiry': self.decrypt_data(self.card_expiry)
        }

    def set_address(self, address):
        """Encrypt address data"""
        self.address = self.encrypt_data(address)

    def get_address(self):
        """Decrypt address data"""
        return self.decrypt_data(self.address)

    def get_reputation_level(self):
        """Calculate user's reputation level"""
        if self.reputation_points < 100:
            return 'Beginner'
        elif self.reputation_points < 500:
            return 'Intermediate'
        elif self.reputation_points < 1000:
            return 'Advanced'
        else:
            return 'Expert'

    def add_ctf_points(self, points):
        self.ctf_points += points
        self._update_skill_level()
        
    def add_python_points(self, points):
        self.python_points += points
        self._update_skill_level()
        
    def add_kali_points(self, points):
        self.kali_points += points
        self._update_skill_level()
        
    def add_malware_points(self, points):
        self.malware_points += points
        self._update_skill_level()
        
    def add_pentest_points(self, points):
        self.pentest_points += points
        self._update_skill_level()
        
    def add_cpp_points(self, points):
        self.cpp_points += points
        self._update_skill_level()
        
    def _update_skill_level(self):
        total_points = (self.ctf_points + self.python_points + self.kali_points +
                       self.malware_points + self.pentest_points + self.cpp_points)
        if total_points < 100:
            self.skill_level = 'Beginner'
        elif total_points < 500:
            self.skill_level = 'Intermediate'
        else:
            self.skill_level = 'Advanced'

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.account_type}')"

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('ForumComment', backref='post', lazy=True)

class ForumComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)

class CTFChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.String(100), nullable=False)
    hints = db.relationship('CTFHint', backref='challenge', lazy=True)
    scores = db.relationship('CTFScore', backref='challenge', lazy=True)

class CTFHint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('ctf_challenge.id'), nullable=False)

class CTFScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('ctf_challenge.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class LearningModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    prerequisites = db.Column(db.String(200))
    progress = db.relationship('LearningProgress', backref='module', lazy=True)

class LearningProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('learning_module.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    progress_percent = db.Column(db.Float, default=0.0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

class MarketplaceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default_item.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    stock = db.Column(db.Integer, nullable=False, default=1)
    is_digital = db.Column(db.Boolean, default=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Item status
    is_approved = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    
    orders = db.relationship('Order', backref='item', lazy=True)
    reviews = db.relationship('ItemReview', backref='item', lazy=True)

    def calculate_rating(self):
        """Calculate average rating from reviews"""
        if not self.reviews:
            return 0.0
        total = sum(review.rating for review in self.reviews)
        return round(total / len(self.reviews), 1)
    
    def update_stock(self, quantity):
        """Update item stock safely"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def is_available(self):
        """Check if item is available for purchase"""
        return self.stock > 0 and self.is_approved

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('marketplace_item.id'), nullable=False)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    
    # Payment info (encrypted)
    transaction_id = db.Column(db.String(255))
    payment_method = db.Column(db.String(50))

    def get_transaction_details(self):
        """Safely retrieve transaction details"""
        return {
            'id': self.decrypt_data(self.transaction_id),
            'method': self.payment_method,
            'status': self.status
        }
        
    def set_transaction_id(self, transaction_id):
        """Securely store transaction ID"""
        self.transaction_id = cipher_suite.encrypt(transaction_id.encode()).decode()

class ItemReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('marketplace_item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default_news.jpg')
    
    # Article metadata
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    
    comments = db.relationship('NewsComment', backref='article', lazy=True)
    tags = db.relationship('NewsTag', secondary='article_tags', lazy='subquery',
        backref=db.backref('articles', lazy=True))

    def increment_view(self):
        """Safely increment view count"""
        self.views += 1
        db.session.commit()
    
    def toggle_like(self, user_id):
        """Toggle like status for a user"""
        # Implementation for like/unlike functionality
        pass
    
    def get_related_articles(self, limit=5):
        """Get related articles based on tags"""
        related = NewsArticle.query\
            .join(article_tags)\
            .join(NewsTag)\
            .filter(NewsArticle.id != self.id)\
            .filter(NewsArticle.is_approved == True)\
            .filter(NewsTag.id.in_([tag.id for tag in self.tags]))\
            .order_by(NewsArticle.date_posted.desc())\
            .limit(limit)\
            .all()
        return related

class NewsComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('news_article.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('news_comment.id'))
    
    # Nested comments
    replies = db.relationship(
        'NewsComment', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

class NewsTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('news_article.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('news_tag.id'), primary_key=True)
)

# Python Learning Models
class PythonExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    starter_code = db.Column(db.Text)
    solution = db.Column(db.Text, nullable=False)
    test_cases = db.Column(db.Text, nullable=False)  # JSON string of test cases
    points = db.Column(db.Integer, nullable=False, default=10)
    hints = db.Column(db.Text)  # JSON string of hints
    order = db.Column(db.Integer)
    completed_by = db.relationship('User', secondary='python_exercise_completion',
                                 backref=db.backref('completed_exercises', lazy='dynamic'))

# Association table for tracking completed Python exercises
python_exercise_completion = db.Table('python_exercise_completion',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('exercise_id', db.Integer, db.ForeignKey('python_exercise.id'), primary_key=True),
    db.Column('completed_at', db.DateTime, default=datetime.utcnow)
)

# Kali Linux Learning Models
class KaliLab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tools_required = db.Column(db.Text)  # JSON string of required Kali tools
    instructions = db.Column(db.Text, nullable=False)
    solution_guide = db.Column(db.Text)
    points = db.Column(db.Integer, nullable=False, default=20)
    estimated_time = db.Column(db.Integer)  # in minutes
    prerequisites = db.Column(db.Text)  # JSON string of prerequisite lab IDs
    completed_by = db.relationship('User', secondary='kali_lab_completion',
                                 backref=db.backref('completed_labs', lazy='dynamic'))

# Association table for tracking completed Kali labs
kali_lab_completion = db.Table('kali_lab_completion',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('lab_id', db.Integer, db.ForeignKey('kali_lab.id'), primary_key=True),
    db.Column('completed_at', db.DateTime, default=datetime.utcnow),
    db.Column('time_taken', db.Integer)  # in minutes
)

# Malware Analysis Learning Models
class MalwareAnalysisLab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., Analysis, Reverse Engineering, Modern Types
    difficulty = db.Column(db.String(20), nullable=False)
    malware_type = db.Column(db.String(50), nullable=False)  # e.g., Ransomware, Trojan, Worm
    tools_required = db.Column(db.Text)  # JSON string of required analysis tools
    environment_setup = db.Column(db.Text, nullable=False)  # Setup instructions for safe analysis
    analysis_steps = db.Column(db.Text, nullable=False)
    safety_precautions = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=30)
    estimated_time = db.Column(db.Integer)  # in minutes
    prerequisites = db.Column(db.Text)  # JSON string of prerequisite lab IDs
    completed_by = db.relationship('User', secondary='malware_lab_completion',
                                 backref=db.backref('completed_malware_labs', lazy='dynamic'))

# Penetration Testing Models
class PenTestLab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., Web, Network, Wireless
    difficulty = db.Column(db.String(20), nullable=False)
    target_setup = db.Column(db.Text, nullable=False)  # Setup instructions for target environment
    tools_required = db.Column(db.Text)  # JSON string of required pentesting tools
    methodology = db.Column(db.Text, nullable=False)  # Step-by-step penetration testing methodology
    objectives = db.Column(db.Text, nullable=False)  # JSON string of lab objectives
    points = db.Column(db.Integer, nullable=False, default=40)
    estimated_time = db.Column(db.Integer)  # in minutes
    prerequisites = db.Column(db.Text)  # JSON string of prerequisite lab IDs
    completed_by = db.relationship('User', secondary='pentest_lab_completion',
                                 backref=db.backref('completed_pentest_labs', lazy='dynamic'))

# C/C++ Learning Models
class CPPExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., Basics, Memory Management, Security
    difficulty = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(10), nullable=False)  # 'C' or 'C++'
    starter_code = db.Column(db.Text)
    solution = db.Column(db.Text, nullable=False)
    test_cases = db.Column(db.Text, nullable=False)  # JSON string of test cases
    memory_constraints = db.Column(db.Text)  # Memory usage requirements/limits
    security_focus = db.Column(db.Text)  # Security considerations for the exercise
    points = db.Column(db.Integer, nullable=False, default=25)
    hints = db.Column(db.Text)  # JSON string of hints
    order = db.Column(db.Integer)
    completed_by = db.relationship('User', secondary='cpp_exercise_completion',
                                 backref=db.backref('completed_cpp_exercises', lazy='dynamic'))

# Association tables for tracking completion
malware_lab_completion = db.Table('malware_lab_completion',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('lab_id', db.Integer, db.ForeignKey('malware_analysis_lab.id'), primary_key=True),
    db.Column('completed_at', db.DateTime, default=datetime.utcnow),
    db.Column('time_taken', db.Integer)  # in minutes
)

pentest_lab_completion = db.Table('pentest_lab_completion',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('lab_id', db.Integer, db.ForeignKey('pen_test_lab.id'), primary_key=True),
    db.Column('completed_at', db.DateTime, default=datetime.utcnow),
    db.Column('time_taken', db.Integer)  # in minutes
)

cpp_exercise_completion = db.Table('cpp_exercise_completion',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('exercise_id', db.Integer, db.ForeignKey('cpp_exercise.id'), primary_key=True),
    db.Column('completed_at', db.DateTime, default=datetime.utcnow)
)

# Achievement system
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(20), default='default_achievement.png')
    points = db.Column(db.Integer, nullable=False, default=10)
    criteria = db.Column(db.Text, nullable=False)  # JSON string of achievement criteria
    users = db.relationship('User', secondary='user_achievements',
                          backref=db.backref('achievements', lazy='dynamic'))

# Association table for user achievements
user_achievements = db.Table('user_achievements',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('achievement_id', db.Integer, db.ForeignKey('achievement.id'), primary_key=True),
    db.Column('earned_at', db.DateTime, default=datetime.utcnow)
)
