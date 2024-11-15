"""
GhostSec Django application initialization.
"""

# Celery configuration
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    __all__ = ()

# Load environment variables
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Django extensions
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.mail import send_mail
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.cache import caches
from django.core.cache.backends.dummy import InvalidCacheKey

# Initialize rate limiter
from django_ratelimit import RatelimitMiddleware

# Configure login manager
from django.contrib.auth import login
from django.contrib.auth.views import LoginView

# Initialize Django app
from django.apps import apps
from django.conf import settings

def create_app():
    try:
        # Configuration
        config = {
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev_key_123'),
            'DATABASES': {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': os.getenv('DATABASE_URL', 'ghostsec.db'),
                }
            },
            
            # Email configuration
            'EMAIL_HOST': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            'EMAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
            'EMAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
            'EMAIL_HOST_USER': os.getenv('MAIL_USERNAME'),
            'EMAIL_HOST_PASSWORD': os.getenv('MAIL_PASSWORD'),
            
            # File upload configuration
            'DATA_UPLOAD_MAX_MEMORY_SIZE': int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)),
            'MEDIA_ROOT': os.getenv('UPLOAD_FOLDER', 'uploads'),
            
            # Rate limiting configuration
            'RATELIMIT_CACHE': os.getenv('RATELIMIT_STORAGE_URL', 'django.core.cache.backends.locmem.LocMemCache'),
            'RATELIMIT_ENABLE': True,
        }
        
        # Import and register apps
        with apps.ready():
            from ghostsec.main import main as main_app
            from ghostsec.auth import auth as auth_app
            from ghostsec.forum import forum as forum_app
            from ghostsec.marketplace import marketplace as marketplace_app
            from ghostsec.learning import learning as learning_app
            from ghostsec.ctf import ctf as ctf_app
            from ghostsec.news import news as news_app
            
            # Create database tables
            models.Model.__subclasses__()
            
            # Create required directories
            os.makedirs(config['MEDIA_ROOT'], exist_ok=True)
            os.makedirs('logs', exist_ok=True)
            os.makedirs('instance', exist_ok=True)
        
        return config
        
    except Exception as e:
        print(f"Error creating application: {str(e)}")
        raise
