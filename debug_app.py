from flask import Flask, render_template
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/ghostsec.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('GhostSec startup')
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_12345')
    
    # Register routes
    @app.route('/')
    def home():
        app.logger.info('Home page requested')
        return render_template('index.html')

    @app.route('/python-cybersecurity')
    def python_cyber():
        app.logger.info('Python cybersecurity page requested')
        return render_template('python_cybersecurity.html')

    @app.route('/software-engineering')
    def software_eng():
        app.logger.info('Software engineering page requested')
        return render_template('software_engineering.html')

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('Server Error: %s', error)
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error('Page not found: %s', error)
        return render_template('404.html'), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
