from ghostsec import create_app
from waitress import serve
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ghostsec.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def start_server():
    try:
        # Create Flask app
        app = create_app()
        
        # Print access information
        logger.info("Starting server...")
        logger.info("Local URL: http://localhost:8000")
        
        # Start waitress server
        serve(app, host='0.0.0.0', port=8000)
        
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise

if __name__ == '__main__':
    start_server()
