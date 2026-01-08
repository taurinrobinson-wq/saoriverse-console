#!/bin/bash
set -e

echo "Starting FirstPerson services..."

# Start Python backend
echo "Starting FastAPI backend on port 8000..."
python firstperson_backend.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

# Start Next.js frontend
echo "Starting Next.js frontend on port 3001..."
cd /app/firstperson-web
npm install --production --legacy-peer-deps > /dev/null 2>&1
npm run start > /var/log/nextjs.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:3001 > /dev/null 2>&1; then
        echo "✓ Frontend is ready"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

# Start nginx
echo "Starting nginx reverse proxy..."
nginx -g "daemon off;"
