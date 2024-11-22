"""
WSGI config for GhostSec project.
"""

import os
import sys

# Add the project directory to the sys.path
project_home = '/home/anonymous23/GHOSTSecWebpage'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Create required directories
for dir_name in ['logs', 'uploads', 'yara_rules']:
    dir_path = os.path.join(project_home, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONPATH'] = project_home

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env.pythonanywhere'))

# Import Flask application
from ghostsec import create_app
application = create_app('production')
