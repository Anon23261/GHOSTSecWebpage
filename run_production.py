from ghostsec import create_app
from waitress import serve
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ghostsec.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Create Flask app with production config
    app = create_app()
    
    # Configure production settings
    host = '0.0.0.0'
    port = 80  # Changed back to port 80
    
    logger.info(f'Starting GhostSec platform on {host}:{port}')
    
    # Run with production server
    serve(app, host=host, port=port, threads=4)

if __name__ == '__main__':
    main()
