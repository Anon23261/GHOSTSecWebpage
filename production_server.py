from ghostsec import create_app
from waitress import serve
from pyngrok import ngrok, conf
import logging
import webbrowser
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def start_production_server():
    try:
        # Configure ngrok
        conf.get_default().auth_token = os.getenv('NGROK_AUTH_TOKEN')
        conf.get_default().region = 'us'  # Use 'us' for better US performance
        
        # Set up ngrok tunnel with optimized settings
        tunnel = ngrok.connect(
            8000,  # Port to expose
            bind_tls=True,  # Force HTTPS
            options={
                "verify_webhook_provider": False,
                "verify_webhook_secret": False,
                "compression": True,  # Enable compression
                "schemes": ["https"]  # HTTPS only
            }
        )
        
        # Get the public URL
        public_url = tunnel.public_url
        logger.info(f"Public URL: {public_url}")
        
        # Create and configure Flask app
        app = create_app()
        app.config['SERVER_NAME'] = None  # Allow any host
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        
        # Print access information
        print("\n=== GhostSec Cybersecurity Platform is ONLINE! ===")
        print(f"Public URL: {public_url}")
        print("\nAccess Methods:")
        print("1. Public Access (Share this with friends):")
        print(f"   {public_url}")
        print("\n2. Local Testing:")
        print("   http://localhost:8000")
        print("   http://127.0.0.1:8000")
        print("\n3. Network Access (LAN):")
        print("   http://192.168.0.29:8000")
        print("\nAdmin Login:")
        print("- Email: admin@ghostsec.com")
        print("- Password: Anonymous@23!")
        print("\nServer Management:")
        print("- Ngrok Dashboard: http://localhost:4040")
        print("- Log File: ghostsec.log")
        print("\nPress Ctrl+C to stop the server")
        
        # Open ngrok interface
        time.sleep(2)
        webbrowser.open('http://localhost:4040')
        
        # Start production server with optimized settings
        serve(
            app,
            host='0.0.0.0',
            port=8000,
            threads=6,  # Increased thread count for multiple users
            connection_limit=1000,  # Maximum concurrent connections
            channel_timeout=30,  # Timeout in seconds
            cleanup_interval=30,  # Cleanup every 30 seconds
            url_scheme='https'  # Force HTTPS
        )
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.exception("Detailed traceback:")
    finally:
        # Clean up
        try:
            ngrok.kill()
            print("\nServer shutdown complete.")
        except:
            pass

if __name__ == '__main__':
    start_production_server()
