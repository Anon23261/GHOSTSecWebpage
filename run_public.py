from ghostsec import create_app
from waitress import serve
from pyngrok import ngrok
import logging
import webbrowser
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_server():
    try:
        # Create and configure Flask app
        app = create_app()
        
        # Start ngrok tunnel (simplified configuration)
        public_url = ngrok.connect(8000)
        logger.info(f"Public URL: {public_url}")
        
        # Print access information
        print("\n=== GhostSec Website is now ONLINE! ===")
        print(f"Public URL: {public_url}")
        print("\nShare this URL with your friends!")
        print("\nLocal Testing URLs:")
        print("- http://localhost:8000")
        print("- http://127.0.0.1:8000")
        print("\nAdmin Login:")
        print("- Email: admin@ghostsec.com")
        print("- Password: Anonymous@23!")
        print("\nNgrok Dashboard: http://localhost:4040")
        print("\nPress Ctrl+C to stop the server")
        
        # Open ngrok dashboard
        time.sleep(2)
        webbrowser.open('http://localhost:4040')
        
        # Start server
        serve(app, host='0.0.0.0', port=8000, threads=4)
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        try:
            ngrok.kill()
            print("Server shutdown complete.")
        except:
            pass

if __name__ == '__main__':
    start_server()
