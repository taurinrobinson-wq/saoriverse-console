#!/usr/bin/env python3
"""
Startup script for FirstPerson on cPanel
Tests environment variable loading and starts the FastAPI app
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: Print environment variables (without sensitive data)
print("=== Environment Check ===")
print(f"SUPABASE_URL: {'✓ Loaded' if os.getenv('SUPABASE_URL') else '✗ Not found'}")
print(f"SUPABASE_ANON_KEY: {'✓ Loaded' if os.getenv('SUPABASE_ANON_KEY') else '✗ Not found'}")
print(f"SUPABASE_FUNCTION_URL: {'✓ Loaded' if os.getenv('SUPABASE_FUNCTION_URL') else '✗ Not found'}")
print("==========================")

# Import and run the FastAPI app
if __name__ == "__main__":
    from fastapi_app import app
    import uvicorn
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)