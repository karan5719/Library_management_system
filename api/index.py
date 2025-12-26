# api/index.py - Vercel serverless function entry point
import sys
import os

# Add the parent directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

# Vercel serverless function handler
def handler(environ, start_response):
    """Vercel serverless function handler"""
    # Fix for static files and templates
    environ['PATH_INFO'] = environ.get('PATH_INFO', '/')
    
    # Handle static files
    if environ['PATH_INFO'].startswith('/static/'):
        try:
            from werkzeug.wsgi import get_host
            from werkzeug.urls import url_parse
            return app(environ, start_response)
        except Exception:
            pass
    
    return app(environ, start_response)

# For local testing
if __name__ == "__main__":
    app.run(debug=True, port=5000)
