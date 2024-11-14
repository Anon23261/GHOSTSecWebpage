import os
import sys
from pathlib import Path
from cryptography.fernet import Fernet

def setup_environment():
    print("Setting up GhostSec environment...")
    
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'ghostsec.db')
    
    # Create necessary directories with proper permissions
    directories = ['logs', 'uploads', 'instance']
    for directory in directories:
        dir_path = Path(os.path.join(base_dir, directory))
        dir_path.mkdir(exist_ok=True)
        # Ensure directory has write permissions
        os.chmod(dir_path, 0o777)
        print(f"Created directory: {directory}")
    
    # Generate encryption key
    encryption_key = Fernet.generate_key()
    
    # Environment variables
    env_vars = {
        'SECRET_KEY': 'dev_secret_key_12345',
        'DATABASE_URL': f'sqlite:///{db_path}',
        'FLASK_APP': 'ghostsec',
        'FLASK_ENV': 'development',
        'DEBUG': 'True',
        'ENCRYPTION_KEY': encryption_key.decode(),
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': '587',
        'MAIL_USE_TLS': 'True',
        'MAIL_USERNAME': 'your_email@gmail.com',
        'MAIL_PASSWORD': 'your_app_password',
        'ADMIN_EMAIL': 'admin@ghostsec.com',
        'MAX_CONTENT_LENGTH': str(16 * 1024 * 1024),  # 16MB
        'UPLOAD_FOLDER': os.path.join(base_dir, 'uploads'),
        'RATELIMIT_STORAGE_URL': 'memory://',
        'RATELIMIT_DEFAULT': '200/day;50/hour',
        'RATELIMIT_HEADERS_ENABLED': 'True'
    }
    
    # Write to .env file
    with open(os.path.join(base_dir, '.env'), 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print("Created .env file with default configuration")
    
    # Initialize database
    print("Initializing database...")
    try:
        # Create the database directory if it doesn't exist
        db_dir = Path(instance_dir)
        db_dir.mkdir(exist_ok=True)
        os.chmod(db_dir, 0o777)
        
        # Touch the database file to ensure it exists with proper permissions
        with open(db_path, 'a') as f:
            pass
        os.chmod(db_path, 0o666)
        
        from init_db import init_database
        init_database()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False
    
    print("\nSetup completed successfully!")
    print("\nDefault admin credentials:")
    print("Email: admin@ghostsec.com")
    print("Password: Anonymous@23!")
    return True

if __name__ == '__main__':
    if setup_environment():
        print("\nYou can now run the application using:")
        print("python debug_app.py")
    else:
        print("\nSetup failed. Please check the error messages above.")
