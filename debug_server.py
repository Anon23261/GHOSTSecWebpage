from ghostsec import create_app
import logging
import sys

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_debug_app():
    try:
        app = create_app()
        app.debug = True
        
        # Add error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            logger.error(f'Page not found: {error}')
            return 'Page not found', 404

        @app.errorhandler(500)
        def internal_error(error):
            logger.error(f'Server Error: {error}')
            logger.exception("Detailed traceback:")
            return 'Internal server error', 500

        return app
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        logger.exception("Detailed traceback:")
        raise

if __name__ == '__main__':
    try:
        app = create_debug_app()
        print("\nStarting server in debug mode...")
        print("URL: http://localhost:5000")
        print("\nAdmin Login:")
        print("Email: admin@ghostsec.com")
        print("Password: Anonymous@23!")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        logger.exception("Detailed traceback:")
