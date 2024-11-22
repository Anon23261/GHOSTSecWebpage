"""
WSGI config for GHOSTSec project.
For deployment on PythonAnywhere.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the sys.path
path = '/home/anonymous23/GHOSTSecWebpage'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(path, '.env.pythonanywhere')
load_dotenv(env_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ghostsec.settings'

# Set up Django
import django
django.setup()

# Get the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
