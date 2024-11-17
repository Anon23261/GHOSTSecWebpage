"""
Database initialization script for GhostSec.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to the sys.path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from __init__ import create_app, db, bcrypt

def init_database():
    """Initialize the database with required tables."""
    app = create_app('production')
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        from ghostsec.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@ghostsec.com',
                password=bcrypt.generate_password_hash('changeme123').decode('utf-8'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Initialize the database
    init_database()
