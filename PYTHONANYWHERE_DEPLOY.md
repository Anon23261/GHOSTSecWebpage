# Deploy GhostSec on PythonAnywhere (Free Tier)

This guide will help you deploy GhostSec on PythonAnywhere's free tier.

## Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com/registration/register/beginner/
2. Sign up for a free "Beginner" account
3. Remember your username - your site will be yourusername.pythonanywhere.com

## Step 2: Set Up Your Environment

1. After logging in, go to the Dashboard
2. Click on "Web" tab
3. Click "Add a new web app"
4. Choose:
   - Python 3.10
   - Manual configuration (not Django)

## Step 3: Set Up Virtual Environment

1. Go to "Consoles" tab
2. Click "Bash console"
3. Create and activate virtual environment:
```bash
mkvirtualenv --python=/usr/bin/python3.10 ghostsec
workon ghostsec
```

4. Install requirements:
```bash
pip install django==4.2.7 gunicorn psycopg2-binary redis django-redis whitenoise
```

## Step 4: Get the Code

1. In the Bash console:
```bash
cd ~
git clone https://github.com/YourUsername/GhostSec.git
cd GhostSec
```

## Step 5: Configure Settings

1. Create production settings:
```bash
mkdir -p ghostsec/settings
touch ghostsec/settings/__init__.py
```

2. Edit production.py:
```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

# Static files
STATIC_ROOT = '/home/yourusername/GhostSec/static'
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = '/home/yourusername/GhostSec/media'
MEDIA_URL = '/media/'

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# Use WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database - using SQLite for free tier
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Cache - using local memory for free tier
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

## Step 6: Configure WSGI

1. Go to Web tab
2. Click on your web app
3. Scroll to "Code" section
4. Click on WSGI configuration file
5. Replace contents with:
```python
import os
import sys

path = '/home/yourusername/GhostSec'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ghostsec.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Step 7: Set Up Static Files

1. In Web tab, add static files mapping:
   - URL: /static/
   - Directory: /home/yourusername/GhostSec/static

2. Collect static files:
```bash
python manage.py collectstatic
```

## Step 8: Initialize Database

1. Run migrations:
```bash
python manage.py migrate
```

2. Create superuser:
```bash
python manage.py createsuperuser
```

## Step 9: Configure Virtual Environment

1. In Web tab, set virtual environment:
   - /home/yourusername/.virtualenvs/ghostsec

## Step 10: Reload Application

1. Click the green "Reload" button in Web tab

## Step 11: Visit Your Site

1. Go to https://yourusername.pythonanywhere.com
2. Log in with your superuser credentials

## Sharing with Friends

1. Share your site URL: https://yourusername.pythonanywhere.com
2. Create accounts for them through admin interface:
   - Go to /admin
   - Log in with superuser account
   - Add new users

## Maintenance

### View Logs
- Error log: Click "Error log" in Web tab
- Server log: Click "Server log" in Web tab
- Access log: Click "Access log" in Web tab

### Update Application
```bash
cd ~/GhostSec
git pull
python manage.py migrate
python manage.py collectstatic
```
Then click "Reload" in Web tab

### Free Tier Limits
- 512MB storage
- Limited CPU usage
- SQLite database
- One web app
- yourusername.pythonanywhere.com domain

## Troubleshooting

### Site Not Loading
1. Check error logs in Web tab
2. Verify WSGI configuration
3. Check allowed hosts in settings

### Static Files Missing
1. Run collectstatic again
2. Check static files mapping
3. Verify STATIC_ROOT setting

### Database Issues
1. Check if migrations are applied
2. Verify database file permissions
3. Check available storage space

## Support

If you encounter issues:
1. Check the error logs
2. Review this guide's troubleshooting section
3. Visit PythonAnywhere Forums
4. Create an issue on GitHub
