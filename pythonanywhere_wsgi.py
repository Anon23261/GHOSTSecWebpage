"""
WSGI config for GhostSec project.
"""

import os
import sys

# Add the project directory to the sys.path
project_home = '/home/anonymous23/GHOSTSecWebpage'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONPATH'] = project_home

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask application
from run import app as application
