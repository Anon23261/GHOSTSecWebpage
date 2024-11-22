import os
import sys
from pathlib import Path
from django.core.management.utils import get_random_secret_key

def setup_environment():
    """Set up GhostSec Django environment"""
    print("Setting up GhostSec environment...")
    
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Create necessary directories
    directories = [
        'logs',
        'media',
        'static',
        'staticfiles',
        os.path.join('ghostsec', 'static'),
        os.path.join('ghostsec', 'media'),
    ]
    
    for directory in directories:
        dir_path = Path(os.path.join(base_dir, directory))
        dir_path.mkdir(exist_ok=True, parents=True)
        print(f"Created directory: {directory}")
    
    # Environment variables
    env_vars = {
        'DJANGO_SECRET_KEY': get_random_secret_key(),
        'DJANGO_DEBUG': 'True',
        'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
        'DATABASE_URL': 'sqlite:///db.sqlite3',
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': '587',
        'EMAIL_USE_TLS': 'True',
        'EMAIL_HOST_USER': 'your_email@gmail.com',
        'EMAIL_HOST_PASSWORD': 'your_app_password',
        'ADMIN_EMAIL': 'admin@ghostsec.com',
        'MEDIA_ROOT': os.path.join(base_dir, 'media'),
        'STATIC_ROOT': os.path.join(base_dir, 'staticfiles'),
    }
    
    # Write to .env file
    env_path = os.path.join(base_dir, '.env')
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print("Created .env file with default configuration")
    else:
        print(".env file already exists, skipping creation")
    
    # Create a README if it doesn't exist
    readme_path = os.path.join(base_dir, 'README.md')
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("""# GhostSec Web Platform

A Django-based cybersecurity learning and collaboration platform.

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Features

- User Authentication System
- CTF (Capture The Flag) Module
- Learning Environments
- Malware Analysis Labs
- Marketplace
- Forum
- News/Blog Section
- Programming Exercises

## Development

- Framework: Django 4.2.7
- Database: SQLite (default)
- Static Files: WhiteNoise
- Forms: Crispy Forms with Bootstrap 4

## Deployment

For deployment instructions, see `docs/deployment.md`.

## License

Copyright 2024 GhostSec. All rights reserved.
""")
        print("Created README.md file")
    else:
        print("README.md already exists, skipping creation")
    
    return True

if __name__ == '__main__':
    if setup_environment():
        print("\nSetup complete! You can now run the application using:")
        print("python manage.py migrate")
        print("python manage.py createsuperuser")
        print("python manage.py runserver")
