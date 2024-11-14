import os
import sys
import time
import subprocess
import webbrowser
from ghostsec import create_app
from waitress import serve

def start_ngrok():
    ngrok_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ngrok')
    config_path = os.path.join(os.getcwd(), 'ngrok.yml')
    
    # Copy config file to ngrok directory
    if not os.path.exists(ngrok_path):
        os.makedirs(ngrok_path)
    
    # Start ngrok
    ngrok_process = subprocess.Popen(
        ['ngrok', 'start', '--config', config_path, 'website'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return ngrok_process

def main():
    # Start ngrok first
    print("Starting ngrok tunnel...")
    ngrok_process = start_ngrok()
    time.sleep(3)  # Give ngrok time to start
    
    # Create and run Flask app
    print("\nStarting web server...")
    app = create_app()
    
    print("\n=== GhostSec Website is now live! ===")
    print("Local URL: http://localhost:8000")
    print("To see your public URL, visit: http://localhost:4040")
    print("\nAdmin credentials:")
    print("Email: admin@ghostsec.com")
    print("Password: Anonymous@23!")
    print("\nPress Ctrl+C to stop the servers")
    
    # Open ngrok interface
    webbrowser.open('http://localhost:4040')
    
    try:
        serve(app, host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        ngrok_process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        ngrok_process.terminate()
        sys.exit(1)

if __name__ == '__main__':
    main()
