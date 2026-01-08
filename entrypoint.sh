#!/bin/sh
set -e

echo "[$(date)] Starting Velinor services..."

# Start Next.js in background
echo "[$(date)] Starting Next.js frontend on port 3000..."
cd /app/velinor-web
PORT=3000 npm start > /tmp/frontend.log 2>&1 &
NEXT_PID=$!
echo "[$(date)] Next.js PID: $NEXT_PID"

# Wait longer for Next.js to start and be ready
echo "[$(date)] Waiting for Next.js to be ready (up to 30s)..."
for i in $(seq 1 30); do
  if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "[$(date)] Next.js is ready"
    break
  fi
  echo "[$(date)] Waiting for Next.js... ($i/30)"
  sleep 1
done

# Start API in background  
echo "[$(date)] Starting FastAPI backend on port 8001..."
cd /app
PORT=8001 python3 velinor_api.py > /tmp/api.log 2>&1 &
API_PID=$!
echo "[$(date)] API PID: $API_PID"

# Wait for API to be ready
echo "[$(date)] Waiting for FastAPI to be ready (up to 10s)..."
for i in $(seq 1 10); do
  if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "[$(date)] FastAPI is ready"
    break
  fi
  echo "[$(date)] Waiting for FastAPI... ($i/10)"
  sleep 1
done

# Start nginx in foreground
echo "[$(date)] Starting nginx reverse proxy on port 8000..."
exec nginx -g 'daemon off;'
