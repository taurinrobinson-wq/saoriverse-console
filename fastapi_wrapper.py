#!/usr/bin/env python3
"""
CGI Wrapper for FirstPerson FastAPI Application
Place this in your cgi-bin directory
"""

import sys
import os
from pathlib import Path

# Add the application directory to Python path
app_dir = Path('/home/firscius/public_html')
sys.path.insert(0, str(app_dir))

# Set up environment
os.chdir(str(app_dir))

# Import and run the FastAPI app
try:
    from fastapi_app import app
    from fastapi.middleware.wsgi import WSGIMiddleware
    
    # Convert FastAPI to WSGI for CGI
    wsgi_app = WSGIMiddleware(app)
    
    # CGI execution
    if __name__ == '__main__':
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(wsgi_app)
        
except Exception as e:
    print("Content-Type: text/html\n")
    print(f"<h1>Error</h1><p>{str(e)}</p>")
    import traceback
    print(f"<pre>{traceback.format_exc()}</pre>")