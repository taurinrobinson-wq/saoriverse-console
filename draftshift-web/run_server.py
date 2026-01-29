#!/usr/bin/env python3
"""DraftShift API Server"""
import os
import sys
import subprocess
import threading
import time

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 DraftShift Renamer Starting")
print("-" * 50)

def build_frontend():
    """Build frontend in background"""
    time.sleep(1)  # Wait a bit for server to start
    
    # Install npm deps if needed
    if not os.path.exists("node_modules"):
        print("📦 Installing npm dependencies...")
        subprocess.run("npm install", shell=True, check=False)
    
    # Build React if needed
    if not os.path.exists("dist"):
        print("🏗️  Building React frontend...")
        subprocess.run("npm run build", shell=True, check=False)
    
    print("✅ Frontend ready!")

# Start build in background thread
build_thread = threading.Thread(target=build_frontend, daemon=True)
build_thread.start()

# Start server immediately
print("\n🌐 Starting API server...")
port = int(os.getenv("PORT", 8000))
print(f"📍 Using port: {port}")
print("-" * 50 + "\n")

import uvicorn
from api import app

uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


