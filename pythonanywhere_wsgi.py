"""
WSGI config for GhostSec project.
"""

import os
import sys

# Add the project directory to the sys.path
project_home = '/home/anonymous23/GhostSec'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghostsec.settings.pythonanywhere')

# Import Django WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
