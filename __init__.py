"""
GhostSec application initialization.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import config

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'))
    migrate.init_app(app, db)
    limiter.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    from .routes.forum import forum as forum_blueprint
    app.register_blueprint(forum_blueprint, url_prefix='/forum')
    
    from .routes.lab import lab as lab_blueprint
    app.register_blueprint(lab_blueprint, url_prefix='/lab')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, ForumPost=ForumPost,
                   LabInstance=LabInstance)
    
    return app

# Import models here to avoid circular imports
from .models.user import User
from .models.forum import ForumPost
from .models.lab import LabInstance
