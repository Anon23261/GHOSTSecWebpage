"""
PythonAnywhere-specific configuration settings.
"""
import os
from datetime import timedelta
from config import Config, ProductionConfig

class PythonAnywhereConfig(ProductionConfig):
    """PythonAnywhere-specific configuration."""
    
    # Override database configuration for PythonAnywhere MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # File paths adjusted for PythonAnywhere
    BASE_DIR = '/home/anonymous23/GHOSTSecWebpage'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    YARA_RULES_PATH = os.path.join(BASE_DIR, 'yara_rules')
    
    # Disable features not available on PythonAnywhere
    ENABLE_DOCKER = False
    ENABLE_KALI_LABS = False
    
    # WebSocket configuration for PythonAnywhere
    SOCKET_IO_ASYNC_MODE = 'threading'
    SOCKET_IO_PING_TIMEOUT = 5
    SOCKET_IO_PING_INTERVAL = 25
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Configure logging
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)
        
        # Ensure upload directory exists
        if not os.path.exists(cls.UPLOAD_FOLDER):
            os.makedirs(cls.UPLOAD_FOLDER)
        
        # Ensure YARA rules directory exists
        if not os.path.exists(cls.YARA_RULES_PATH):
            os.makedirs(cls.YARA_RULES_PATH)
