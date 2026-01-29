#!/usr/bin/env python3
"""DraftShift API Server"""
import os
import sys
import subprocess

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 DraftShift Renamer Starting")
print("-" * 50)

# Install npm deps if needed
if not os.path.exists("node_modules"):
    print("📦 Installing npm dependencies...")
    subprocess.run("npm install", shell=True, check=False)

# Build React if needed
if not os.path.exists("dist"):
    print("🏗️  Building React frontend...")
    subprocess.run("npm run build", shell=True, check=False)

# Start server
print("\n🌐 Starting API server...")
port = int(os.getenv("PORT", 8000))
print(f"📍 Using port: {port}")
print("-" * 50 + "\n")

import uvicorn
from api import app

uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


