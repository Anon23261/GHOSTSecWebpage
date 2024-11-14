from waitress import serve
from ghostsec import create_app

app = create_app()

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8000, threads=6)
