#!/bin/bash

# Script to start both the Velinor Web Frontend (Next.js) and Backend (FastAPI)
# This is useful for full-stack development

PROJECT_DIR="$(dirname "$0")"
export NVM_DIR="$HOME/.nvm"

# Load nvm
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Velinor Game - Full Stack Dev Server              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Start FastAPI backend in background
echo "🐍 Starting FastAPI backend..."
cd "$PROJECT_DIR"
python velinor_api.py > /tmp/velinor_backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID (logs in /tmp/velinor_backend.log)"
sleep 2

# Start Next.js frontend in the foreground
echo ""
echo "⚛️  Starting Next.js frontend..."
echo ""
nvm use 20.11.0 > /dev/null 2>&1
cd "$PROJECT_DIR/velinor-web"

echo "════════════════════════════════════════════════════════════"
echo "📍 Frontend:  http://localhost:3000"
echo "🔌 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

npm run dev

# Kill backend when frontend is stopped
echo ""
echo "Stopping backend server..."
kill $BACKEND_PID 2>/dev/null
wait $BACKEND_PID 2>/dev/null

echo "✅ All servers stopped"
