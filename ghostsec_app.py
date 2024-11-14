"""
GhostSec - Cybersecurity Learning Platform
Main application module
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
migrate = Migrate()
ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    limiter.init_app(app)

    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from routes.social import bp as social_bp
    app.register_blueprint(social_bp, url_prefix='/social')

    from routes.labs import bp as labs_bp
    app.register_blueprint(labs_bp, url_prefix='/labs')

    from routes.projects import bp as projects_bp
    app.register_blueprint(projects_bp, url_prefix='/projects')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'ForumPost': ForumPost,
            'ForumCategory': ForumCategory,
            'ChatRoom': ChatRoom
        }

    return app

# Import models after db is defined
from models import User, ForumPost, ForumCategory, ChatRoom
