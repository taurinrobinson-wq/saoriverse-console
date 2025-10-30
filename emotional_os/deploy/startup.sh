# cPanel Startup Script for FirstPerson FastAPI Application
#!/bin/bash

# Set environment variables
export PYTHONPATH=/home/firscius/public_html:$PYTHONPATH
export PORT=8000

# Navigate to application directory
cd /home/firscius/public_html

# Start FastAPI application using Gunicorn
exec gunicorn fastapi_app:app --bind 0.0.0.0:$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker