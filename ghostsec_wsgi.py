import os
import sys

# Add your project directory to the sys.path
path = '/home/anonymous23/GhostSec'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ghostsec.settings.pythonanywhere'

# Import your Django project
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
