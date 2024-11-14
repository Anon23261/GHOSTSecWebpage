import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure main application logger
    app.logger.setLevel(logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s\n'
        'Path: %(pathname)s\n'
        'Function: %(funcName)s\n'
        'Line: %(lineno)d\n'
        'Additional Info: %(exc_info)s\n'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    )

    # Error log - Rotating file handler (10MB max size, keep 10 backup files)
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10*1024*1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    # General application log
    app_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,
        backupCount=10
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(simple_formatter)

    # Access log
    access_handler = RotatingFileHandler(
        'logs/access.log',
        maxBytes=10*1024*1024,
        backupCount=10
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(simple_formatter)

    # Add handlers to app logger
    app.logger.addHandler(error_handler)
    app.logger.addHandler(app_handler)
    app.logger.addHandler(access_handler)

    # Create a function to log unhandled exceptions
    def log_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Call the default handler for Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        app.logger.error(
            "Uncaught exception:",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    # Set the exception hook
    import sys
    sys.excepthook = log_exception

    return app
