from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
socketio = SocketIO()
mail = Mail()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Initialize rate limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"
)
api = Api()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_123')  # Temporary dev key
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ghostsec.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # OAuth configuration
    app.config['GITHUB_OAUTH_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')
    app.config['GITHUB_OAUTH_CLIENT_SECRET'] = os.getenv('GITHUB_CLIENT_SECRET')
    app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Initialize extensions with app
    db.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    api.init_app(app)
    
    # Register blueprints
    from ghostsec.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from ghostsec.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from ghostsec.oauth import oauth as oauth_blueprint
    from ghostsec.oauth.routes import github_blueprint, google_blueprint
    app.register_blueprint(oauth_blueprint)
    app.register_blueprint(github_blueprint, url_prefix='/login/github')
    app.register_blueprint(google_blueprint, url_prefix='/login/google')
    
    from ghostsec.learning import learning as learning_blueprint
    app.register_blueprint(learning_blueprint, url_prefix='/learning')
    
    from ghostsec.forum import forum as forum_blueprint
    app.register_blueprint(forum_blueprint, url_prefix='/forum')
    
    from ghostsec.ctf import ctf as ctf_blueprint
    app.register_blueprint(ctf_blueprint, url_prefix='/ctf')
    
    from ghostsec.marketplace import marketplace as marketplace_blueprint
    app.register_blueprint(marketplace_blueprint, url_prefix='/marketplace')
    
    from ghostsec.news import news as news_blueprint
    app.register_blueprint(news_blueprint, url_prefix='/news')
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    return app
