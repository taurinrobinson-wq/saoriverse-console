#!/usr/bin/env python3
"""DraftShift API Server"""
import os
import sys
import subprocess
import threading

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 DraftShift Renamer Starting")
print("-" * 50)

def install_deps():
    """Install npm dependencies in background (if needed)"""
    if not os.path.exists("node_modules"):
        print("📦 Installing npm dependencies...")
        subprocess.run("npm install", shell=True, check=False)
    print("✅ Dependencies ready!")

# Start dependency installation in background (fast if node_modules exists)
install_thread = threading.Thread(target=install_deps, daemon=True)
install_thread.start()

# Start server immediately (dist is pre-built and committed)
print("\n🌐 Starting API server...")
port = int(os.getenv("PORT", 8000))
print(f"📍 Using port: {port}")
print("-" * 50 + "\n")

import uvicorn
from api import app

uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


