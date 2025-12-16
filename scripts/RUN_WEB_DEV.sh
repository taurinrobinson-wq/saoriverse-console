#!/bin/bash

# Script to start the Velinor web game dev server
# This automatically sets up Node.js 20 via nvm and starts the Next.js dev server

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

# Use Node 20.11.0
nvm use 20.11.0

# Navigate to the web project
cd "$(dirname "$0")/velinor-web"

# Start the dev server
echo ""
echo "🎮 Starting Velinor Web Game Dev Server..."
echo ""
echo "📍 Access the game at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
