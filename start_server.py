from ghostsec import create_app
from waitress import serve
from pyngrok import ngrok
import logging
import webbrowser
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_server():
    # Create and configure Flask app
    app = create_app()
    app.debug = True
    app.static_folder = 'static'
    app.template_folder = 'templates'
    
    try:
        # Start ngrok
        logger.info("Starting ngrok tunnel...")
        public_url = ngrok.connect(5000)
        logger.info(f"Public URL: {public_url}")
        
        # Open ngrok interface in browser
        time.sleep(2)  # Give ngrok time to start
        webbrowser.open('http://localhost:4040')
        
        # Print access information
        print("\n=== GhostSec Website is now ONLINE! ===")
        print(f"Public URL: {public_url}")
        print("\nLocal Access:")
        print("- Local URL: http://localhost:5000")
        print("- Network URL: http://192.168.0.29:5000")
        print("\nAdmin Login:")
        print("- Email: admin@ghostsec.com")
        print("- Password: Anonymous@23!")
        print("\nNgrok Interface: http://localhost:4040")
        print("\nPress Ctrl+C to stop the server")
        
        # Start the server
        serve(app, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
    finally:
        # Clean up ngrok tunnel
        try:
            ngrok.kill()
        except:
            pass

if __name__ == '__main__':
    start_server()
