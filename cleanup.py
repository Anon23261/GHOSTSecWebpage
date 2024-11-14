import os

files_to_remove = [
    "debug_app.py",
    "debug_server.py",
    "ghostsec_app.py",
    "gunicorn_config.py",
    "host.py",
    "ngrok_server.py",
    "production_server.py",
    "run_debug.py",
    "run_production.py",
    "run_public.py",
    "run_server.py",
    "run_with_ngrok.py",
    "simple_server.py",
    "start_server.py",
    "waitress_server.py",
    "wsgi.py",
    "test_redis.py",
    "run.py",
    "deploy.py",
    "Procfile",
    "render.yaml",
    "ngrok.yml",
    "Memurai-Developer.msi"
]

for file in files_to_remove:
    try:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")
    except Exception as e:
        print(f"Error removing {file}: {e}")
