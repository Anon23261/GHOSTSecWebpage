from waitress import serve
from app import app
import os
import webbrowser
from threading import Timer

def open_browser():
    """Open the browser to the application URL"""
    try:
        webbrowser.open('http://localhost:8000')
    except Exception as e:
        print(f"Failed to open browser: {e}")

if __name__ == '__main__':
    # Create required directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    
    # Open browser after 1.5 seconds
    Timer(1.5, open_browser).start()
    
    # Start the server
    print("Starting GhostSec server...")
    print("Access URLs:")
    print("- Local: http://localhost:8000")
    print("- Network: http://your-ip:8000")
    print("\nPress Ctrl+C to quit")
    
    serve(app, host='0.0.0.0', port=8000, threads=6)
