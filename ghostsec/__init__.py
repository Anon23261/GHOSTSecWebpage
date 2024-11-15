from flask import Flask
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
        app = Flask(__name__)
        
        # Configuration
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_123')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ghostsec.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Email configuration
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        
        # File upload configuration
        app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
        app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
        
        # Rate limiting configuration
        app.config['RATELIMIT_STORAGE_URL'] = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
        app.config['RATELIMIT_HEADERS_ENABLED'] = True
        
        # Initialize extensions with app
        db.init_app(app)
        bcrypt.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        migrate.init_app(app, db)
        limiter.init_app(app)
        socketio.init_app(app)
        api.init_app(app)
        
        # Import and register blueprints
        with app.app_context():
            from ghostsec.main import main as main_blueprint
            from ghostsec.auth import auth as auth_blueprint
            from ghostsec.forum import forum as forum_blueprint
            from ghostsec.marketplace import marketplace as marketplace_blueprint
            from ghostsec.learning import learning as learning_blueprint
            from ghostsec.ctf import ctf as ctf_blueprint
            from ghostsec.news import news as news_blueprint
            
            app.register_blueprint(main_blueprint)
            app.register_blueprint(auth_blueprint, url_prefix='/auth')
            app.register_blueprint(forum_blueprint, url_prefix='/forum')
            app.register_blueprint(marketplace_blueprint, url_prefix='/marketplace')
            app.register_blueprint(learning_blueprint, url_prefix='/learn')
            app.register_blueprint(ctf_blueprint, url_prefix='/ctf')
            app.register_blueprint(news_blueprint, url_prefix='/news')
            
            # Create database tables
            db.create_all()
            
            # Create required directories
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs('logs', exist_ok=True)
            os.makedirs('instance', exist_ok=True)
        
        return app
        
    except Exception as e:
        print(f"Error creating application: {str(e)}")
        raise

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    pass
