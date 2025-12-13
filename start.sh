#!/bin/bash
# Start both Next.js and FastAPI

# Start FastAPI in background on port 8001
echo "Starting FastAPI backend..."
python velinor_api.py &
BACKEND_PID=$!

# Start Next.js in foreground on port 3000, then proxy to it
echo "Starting Next.js frontend..."
cd velinor-web
npm start
