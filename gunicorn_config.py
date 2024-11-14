import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'eventlet'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Process naming
proc_name = 'ghostsec'

# Server mechanics
daemon = False
pidfile = 'logs/gunicorn.pid'
user = None
group = None
umask = 0
tmp_upload_dir = None

# SSL
# keyfile = 'ssl/private.key'
# certfile = 'ssl/cert.pem'
