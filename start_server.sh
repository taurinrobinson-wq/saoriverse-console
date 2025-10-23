#!/bin/bash
# FirstPerson FastAPI Startup Script
# Run this on the cPanel server

echo "Starting FirstPerson FastAPI server..."

# Navigate to the application directory
cd /home/firscius/public_html

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3."
    exit 1
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Kill any existing FastAPI processes
pkill -f "uvicorn fastapi_app:app"

# Start the FastAPI server in background
echo "Starting FastAPI server on port 8000..."
nohup python3 -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 > app.log 2>&1 &

# Get the process ID
sleep 2
PID=$(pgrep -f "uvicorn fastapi_app:app")

if [ ! -z "$PID" ]; then
    echo "FastAPI server started successfully with PID: $PID"
    echo "Server running on http://127.0.0.1:8000"
    echo "Check logs with: tail -f app.log"
else
    echo "Failed to start FastAPI server"
    echo "Check the log file: cat app.log"
    exit 1
fi