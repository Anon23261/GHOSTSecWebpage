import subprocess
import sys
import time
import webbrowser

def main():
    # Start the Flask application with waitress
    flask_process = subprocess.Popen([sys.executable, 'waitress_server.py'])
    
    # Start ngrok
    ngrok_process = subprocess.Popen(['ngrok', 'http', '8000'], 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    
    print("Starting servers...")
    time.sleep(3)  # Give servers time to start
    
    print("\nYour website is now live!")
    print("Local URL: http://localhost:8000")
    print("To see your public URL, visit: http://localhost:4040")
    print("\nAdmin credentials:")
    print("Email: admin@ghostsec.com")
    print("Password: Anonymous@23!")
    print("\nPress Ctrl+C to stop the servers")
    
    try:
        # Open the ngrok web interface
        webbrowser.open('http://localhost:4040')
        # Keep the script running
        flask_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        flask_process.terminate()
        ngrok_process.terminate()
        sys.exit(0)

if __name__ == '__main__':
    main()
