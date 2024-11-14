from ghostsec import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    print("Starting local server...")
    print("Local URL: http://localhost:8000")
    serve(app, host='0.0.0.0', port=8000)
