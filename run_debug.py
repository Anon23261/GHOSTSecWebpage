from ghostsec import create_app
from waitress import serve
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    # Enable debug mode
    app.debug = True
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.error(f'Page not found: {error}')
        return 'Page not found', 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Server Error: {error}')
        return 'Internal server error', 500

    print("Starting server in debug mode...")
    print("Local URL: http://localhost:8000")
    
    try:
        serve(app, host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
