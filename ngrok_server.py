from waitress import serve
from ghostsec import create_app
from pyngrok import ngrok
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create Flask app
app = create_app()

# Start ngrok
public_url = ngrok.connect(8000)
logging.info(f" * Public URL: {public_url}")

if __name__ == '__main__':
    # Run the app
    serve(app, host='0.0.0.0', port=8000, threads=6)
