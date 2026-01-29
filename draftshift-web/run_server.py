#!/usr/bin/env python
"""
DraftShift API Server Startup Script
Handles frontend build and dependency installation before starting the server.
"""

import sys
import os
import subprocess

# Ensure current directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        if result.returncode == 0:
            print(f"✅ {description} complete")
            return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  {description} had issues (continuing anyway): {e}")
        return False
    return True

if __name__ == "__main__":
    print("🚀 DraftShift Renamer Startup")
    print("=" * 50)
    
    # Check if node_modules exists, if not install
    if not os.path.exists("node_modules"):
        run_command("npm install", "Installing npm dependencies")
    
    # Check if dist exists, if not build
    if not os.path.exists("dist"):
        run_command("npm run build", "Building React frontend")
    
    # Start the server
    print("\n🌐 Starting API server on port 8000...")
    print("=" * 50)
    
    import uvicorn
    from api import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

