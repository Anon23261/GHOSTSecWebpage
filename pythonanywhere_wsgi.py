import os
import sys

# Add the project directory to the sys.path
project_home = '/home/anonymous23/GhostSec'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'ghostsec.settings.pythonanywhere'
os.environ['PYTHONPATH'] = project_home

# Import Django WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
