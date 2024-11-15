from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import os
import secrets

def get_encryption_key():
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        key = urlsafe_b64encode(secrets.token_bytes(32)).decode()
    return key.encode()

ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='ghostsec_user_set',
        related_query_name='ghostsec_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='ghostsec_user_set',
        related_query_name='ghostsec_user',
    )
    
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    github = models.URLField(max_length=200, blank=True)
    twitter = models.URLField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    image_file = models.ImageField(upload_to='profile_pics', default='default.jpg')
    account_type = models.CharField(max_length=20, default='user')
    date_joined = models.DateTimeField(default=timezone.now)
    github_id = models.CharField(max_length=120, unique=True, null=True, blank=True)
    google_id = models.CharField(max_length=120, unique=True, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    linkedin = models.CharField(max_length=100, null=True, blank=True)
    reputation_points = models.IntegerField(default=0)
    python_points = models.IntegerField(default=0)
    kali_points = models.IntegerField(default=0)
    malware_points = models.IntegerField(default=0)
    pentest_points = models.IntegerField(default=0)
    cpp_points = models.IntegerField(default=0)
    total_achievements = models.IntegerField(default=0)
    skill_level = models.CharField(max_length=20, default='Beginner')

    def encrypt_data(self, data):
        return cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        return cipher_suite.decrypt(encrypted_data.encode()).decode()

    def set_phone_number(self, phone):
        if phone:
            self.phone_number = self.encrypt_data(phone)
        else:
            self.phone_number = None

    def get_phone_number(self):
        if self.phone_number:
            return self.decrypt_data(self.phone_number)
        return None

    def get_reputation_level(self):
        if self.reputation_points < 100:
            return 'Novice'
        elif self.reputation_points < 500:
            return 'Intermediate'
        elif self.reputation_points < 1000:
            return 'Advanced'
        else:
            return 'Expert'

    def _update_skill_level(self):
        total_points = (
            self.python_points + self.kali_points +
            self.malware_points + self.pentest_points + self.cpp_points
        )
        if total_points < 100:
            self.skill_level = 'Beginner'
        elif total_points < 500:
            self.skill_level = 'Intermediate'
        elif total_points < 1000:
            self.skill_level = 'Advanced'
        else:
            self.skill_level = 'Expert'
        self.save()

    def __str__(self):
        return self.username

class LearningModule(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    content = models.TextField()
    order = models.IntegerField()
    prerequisites = models.CharField(max_length=200, null=True, blank=True)

class LearningProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_progress')
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    progress_percent = models.FloatField(default=0.0)
    last_accessed = models.DateTimeField(default=timezone.now)

class MarketplaceItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    category = models.CharField(max_length=50)
    image_file = models.ImageField(upload_to='marketplace', default='default_item.jpg')
    date_posted = models.DateTimeField(default=timezone.now)
    stock = models.IntegerField(default=1)
    is_digital = models.BooleanField(default=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketplace_items')
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)

    def calculate_rating(self):
        reviews = self.reviews.all()
        if reviews:
            self.rating = sum(review.rating for review in reviews) / len(reviews)
            self.save()

    def is_available(self):
        return self.stock > 0 or self.is_digital

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE, related_name='orders')
    date_ordered = models.DateTimeField(default=timezone.now)
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField()
    status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)

class ItemReview(models.Model):
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

class NewsTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.CharField(max_length=500, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    category = models.CharField(max_length=50)
    image_file = models.ImageField(upload_to='news', default='default_news.jpg')
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    tags = models.ManyToManyField(NewsTag, related_name='articles')

    def increment_view(self):
        self.views += 1
        self.save()

class NewsComment(models.Model):
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_comments')
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

class PythonExercise(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    starter_code = models.TextField(null=True, blank=True)
    solution = models.TextField()
    test_cases = models.TextField()
    points = models.IntegerField(default=10)
    hints = models.TextField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_exercises')

class KaliLab(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    tools_required = models.TextField(null=True, blank=True)
    instructions = models.TextField()
    solution_guide = models.TextField(null=True, blank=True)
    points = models.IntegerField(default=20)
    estimated_time = models.IntegerField(null=True, blank=True)
    prerequisites = models.TextField(null=True, blank=True)
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_labs')

class MalwareAnalysisLab(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=20)
    malware_type = models.CharField(max_length=50)
    tools_required = models.TextField(null=True, blank=True)
    environment_setup = models.TextField()
    analysis_steps = models.TextField()
    safety_precautions = models.TextField()
    points = models.IntegerField(default=30)
    estimated_time = models.IntegerField(null=True, blank=True)
    prerequisites = models.TextField(null=True, blank=True)
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_malware_labs')

class PenTestLab(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=20)
    target_setup = models.TextField()
    tools_required = models.TextField(null=True, blank=True)
    methodology = models.TextField()
    objectives = models.TextField()
    points = models.IntegerField(default=40)
    estimated_time = models.IntegerField(null=True, blank=True)
    prerequisites = models.TextField(null=True, blank=True)
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_pentest_labs')

class CPPExercise(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=20)
    language = models.CharField(max_length=10)
    starter_code = models.TextField(null=True, blank=True)
    solution = models.TextField()
    test_cases = models.TextField()
    memory_constraints = models.TextField(null=True, blank=True)
    security_focus = models.TextField(null=True, blank=True)
    points = models.IntegerField(default=25)
    hints = models.TextField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_cpp_exercises')

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='achievements', default='default_achievement.png')
    points = models.IntegerField(default=10)
    criteria = models.TextField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='achievements')
