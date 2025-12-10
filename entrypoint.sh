#!/bin/sh
set -e

echo "[$(date)] Starting Velinor services..."

# Start Next.js in background
echo "[$(date)] Starting Next.js frontend on port 3000..."
cd /app/velinor-web
npm start > /tmp/frontend.log 2>&1 &
NEXT_PID=$!
echo "[$(date)] Next.js PID: $NEXT_PID"

# Wait for Next.js to start
sleep 5

# Start API in background  
echo "[$(date)] Starting FastAPI backend on port 8000..."
cd /app
python3 velinor_api.py > /tmp/api.log 2>&1 &
API_PID=$!
echo "[$(date)] API PID: $API_PID"

# Wait for API to start
sleep 3

# Start nginx in foreground
echo "[$(date)] Starting nginx reverse proxy on port 8000..."
exec nginx -g 'daemon off;'
