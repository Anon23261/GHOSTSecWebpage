"""
PythonAnywhere specific settings for GhostSec project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_value(key, default=None):
    """Get environment variable value with a default."""
    return os.environ.get(key, default)

from .base import *

# Debug settings - Always False in production
DEBUG = False

# Host settings - Replace with your PythonAnywhere username
PYTHONANYWHERE_USERNAME = get_env_value('PYTHONANYWHERE_USERNAME', 'anonymous23')
ALLOWED_HOSTS = [f'{PYTHONANYWHERE_USERNAME}.pythonanywhere.com']

# Database settings - Using SQLite for free tier
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files configuration
STATIC_ROOT = f'/home/{PYTHONANYWHERE_USERNAME}/GhostSec/staticfiles'
STATIC_URL = '/static/'

# Configure WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 604800  # 7 days

# Media files configuration
MEDIA_ROOT = f'/home/{PYTHONANYWHERE_USERNAME}/GhostSec/media'
MEDIA_URL = '/media/'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Cache settings - Using local memory cache for free tier
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env_value('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_value('EMAIL_HOST_PASSWORD')

# Django Axes Configuration
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']
AXES_BEHIND_REVERSE_PROXY = True
AXES_PROXY_COUNT = 1

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")  # Allow inline styles
CSP_SCRIPT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:", "data:")
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_REPORT_URI = '/csp-report/'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': f'/home/{PYTHONANYWHERE_USERNAME}/GhostSec/ghostsec.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
