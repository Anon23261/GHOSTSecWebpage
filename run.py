"""
GhostSec Application Entry Point

This script starts the GhostSec application with the appropriate configuration
based on the environment. It supports both development and production modes.

Usage:
    Development:
        python run.py
    Production:
        FLASK_ENV=production python run.py
"""
import os
from ghostsec import create_app, socketio

# Determine environment
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    # Configure SSL in production
    ssl_context = None
    if env == 'production':
        cert_path = os.path.join('ssl', 'cert.pem')
        key_path = os.path.join('ssl', 'key.pem')
        if os.path.exists(cert_path) and os.path.exists(key_path):
            ssl_context = (cert_path, key_path)
    
    # Start the application
    print(f'Starting GhostSec in {env} mode on {host}:{port}')
    socketio.run(
        app,
        host=host,
        port=port,
        ssl_context=ssl_context,
        debug=env == 'development',
        use_reloader=env == 'development'
    )
