#!/bin/bash
# DraftShift Renamer Startup Script for Replit

set -e  # Exit on any error

echo "🚀 Starting DraftShift Renamer..."
echo ""

cd "$(dirname "$0")"

# Install npm dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Build React frontend if dist doesn't exist
if [ ! -d "dist" ]; then
    echo "🏗️  Building React frontend..."
    npm run build
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Start the server
echo "🌐 Starting API server on port 8000..."
python run_server.py
