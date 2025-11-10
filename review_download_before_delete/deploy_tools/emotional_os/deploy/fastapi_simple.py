"""
FirstPerson Chat - Simplified FastAPI Backend for cPanel Testing
"""

import os
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FirstPerson - Personal AI Companion",
    description="Your private space for emotional processing and growth",
    version="2.0.1"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - using names from .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
SUPABASE_FUNCTION_URL = os.getenv("SUPABASE_FUNCTION_URL")

# Pydantic models
class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str

# Routes
@app.get("/")
async def home():
    """Main landing page - simple JSON response for testing"""
    return {
        "message": "FirstPerson Chat is running!",
        "timestamp": datetime.now().isoformat(),
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment_check": {
            "supabase_url": "✓" if SUPABASE_URL else "✗",
            "supabase_key": "✓" if SUPABASE_KEY else "✗",
            "supabase_function_url": "✓" if SUPABASE_FUNCTION_URL else "✗"
        },
        "python_version": "3.9.23",
        "app_version": "2.0.1"
    }

@app.post("/api/register")
async def register(register_data: RegisterRequest):
    """User registration endpoint - simplified for testing"""
    if register_data.password != register_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if len(register_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # For testing - just return success without actually creating user
    return {
        "success": True,
        "message": "Registration endpoint is working! (Test mode)",
        "username": register_data.username,
        "environment_vars_loaded": bool(SUPABASE_URL and SUPABASE_KEY and SUPABASE_FUNCTION_URL)
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "Test endpoint working!",
        "environment_vars": {
            "SUPABASE_URL": SUPABASE_URL[:50] + "..." if SUPABASE_URL else None,
            "SUPABASE_KEY": "***" if SUPABASE_KEY else None,
            "SUPABASE_FUNCTION_URL": SUPABASE_FUNCTION_URL[:50] + "..." if SUPABASE_FUNCTION_URL else None
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
