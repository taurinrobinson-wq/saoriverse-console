#!/usr/bin/env python3
"""DraftShift API Server - Pre-built production server"""
import os
import sys

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 DraftShift Starting")
print("-" * 50)
print("✅ Frontend pre-built and ready")

# Start server immediately (no npm needed - dist is pre-built)
port = int(os.getenv("PORT", 8000))
print(f"📍 Using port: {port}")
print("-" * 50 + "\n")

import uvicorn
from api import app

uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


