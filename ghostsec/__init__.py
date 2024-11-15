from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_restful import Api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
socketio = SocketIO()
api = Api()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window"
)

def create_app():
    try:
        # Configuration
        config = {
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev_key_123'),
            'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL', 'sqlite:///ghostsec.db'),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            
            # Email configuration
            'MAIL_SERVER': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            'MAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
            'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
            'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
            
            # File upload configuration
            'MAX_CONTENT_LENGTH': int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)),
            'UPLOAD_FOLDER': os.getenv('UPLOAD_FOLDER', 'uploads'),
            
            # Rate limiting configuration
            'RATELIMIT_STORAGE_URL': os.getenv('RATELIMIT_STORAGE_URL', 'memory://'),
            'RATELIMIT_HEADERS_ENABLED': True,
        }
        
        # Import and register blueprints
        with app.app_context():
            from ghostsec.main import main as main_blueprint
            from ghostsec.auth import auth as auth_blueprint
            from ghostsec.forum import forum as forum_blueprint
            from ghostsec.marketplace import marketplace as marketplace_blueprint
            from ghostsec.learning import learning as learning_blueprint
            from ghostsec.ctf import ctf as ctf_blueprint
            from ghostsec.news import news as news_blueprint
            
            # Create database tables
            db.create_all()
            
            # Create required directories
            os.makedirs(config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs('logs', exist_ok=True)
            os.makedirs('instance', exist_ok=True)
        
        return config
        
    except Exception as e:
        print(f"Error creating application: {str(e)}")
        raise

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    __all__ = ()

default_app_config = 'ghostsec.apps.GhostSecConfig'
