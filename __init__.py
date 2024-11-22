"""
GhostSec application initialization.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'pythonanywhere':
        from .config.pythonanywhere import PythonAnywhereConfig
        app.config.from_object(PythonAnywhereConfig)
        PythonAnywhereConfig.init_app(app)
    else:
        from .config import config
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from .routes import init_routes
    init_routes(app)
    
    # Create required directories
    for directory in ['logs', 'uploads', 'yara_rules']:
        path = os.path.join(app.root_path, directory)
        if not os.path.exists(path):
            os.makedirs(path)
    
    return app
