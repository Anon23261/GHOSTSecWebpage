import os
import sys

def create_log_dirs():
    log_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'),
    ]
    
    for directory in log_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except Exception as e:
            print(f"Error creating {directory}: {e}", file=sys.stderr)

if __name__ == '__main__':
    create_log_dirs()
