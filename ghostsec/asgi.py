"""
ASGI config for ghostsec project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghostsec.settings.local')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # WebSocket handler will be added here
})
