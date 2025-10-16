"""
FirstPerson Admin Portal - FastAPI Router
Comprehensive admin interface for system management
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import secrets
import os

# Admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Templates
templates = Jinja2Templates(directory="templates")

# Admin credentials (in production, use database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "firstperson_admin_2025"

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

# Pydantic models
class AdminLogin(BaseModel):
    username: str
    password: str

# Session management
admin_sessions = {}

def verify_admin_password(password: str) -> bool:
    """Verify admin password"""
    return password == ADMIN_PASSWORD

def create_admin_session(username: str) -> str:
    """Create admin session token"""
    token = secrets.token_hex(32)
    admin_sessions[token] = {
        "username": username,
        "created": datetime.now(),
        "expires": datetime.now() + timedelta(hours=24)
    }
    return token

def verify_admin_session(token: str) -> bool:
    """Verify admin session token"""
    if token not in admin_sessions:
        return False
    
    session = admin_sessions[token]
    if datetime.now() > session["expires"]:
        del admin_sessions[token]
        return False
    
    return True

def get_admin_session(request: Request) -> dict:
    """Get admin session from request"""
    token = request.cookies.get("admin_token")
    if not token or not verify_admin_session(token):
        raise HTTPException(status_code=401, detail="Admin authentication required")
    return admin_sessions[token]

# Routes
@admin_router.get("/test")
async def admin_test():
    """Test route to verify admin router is working"""
    return {"message": "Admin router is working!"}

@admin_router.get("/", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@admin_router.post("/login")
async def admin_login_post(request: Request, username: str = Form(), password: str = Form()):
    """Process admin login"""
    if username == ADMIN_USERNAME and verify_admin_password(password):
        token = create_admin_session(username)
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        response.set_cookie(key="admin_token", value=token, httponly=True, max_age=86400)
        return response
    else:
        return templates.TemplateResponse("admin_login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, session: dict = Depends(get_admin_session)):
    """Admin dashboard"""
    
    # Mock system stats (replace with real data)
    system_stats = {
        "total_users": 42,
        "active_sessions": 8,
        "total_conversations": 156,
        "system_uptime": "2 days, 4 hours",
        "avg_response_time": "2.3s",
        "error_rate": "0.1%"
    }
    
    # Mock recent activity
    recent_activity = [
        {
            "timestamp": "2025-10-15 14:30:15",
            "type": "user_login", 
            "user": "demo_user",
            "description": "User logged in via demo mode"
        },
        {
            "timestamp": "2025-10-15 14:25:42",
            "type": "conversation",
            "user": "john_doe", 
            "description": "Started new conversation about stress management"
        },
        {
            "timestamp": "2025-10-15 14:20:33",
            "type": "user_registration",
            "user": "sarah_m",
            "description": "New user registered"
        }
    ]
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "session": session,
        "system_stats": system_stats,
        "recent_activity": recent_activity
    })

@admin_router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, session: dict = Depends(get_admin_session)):
    """User management"""
    
    # Mock user data (replace with Supabase queries)
    users = [
        {
            "id": 1,
            "username": "demo_user",
            "email": "demo@example.com",
            "created_at": "2025-10-15",
            "last_active": "2025-10-15 14:30:15",
            "total_conversations": 5,
            "status": "active"
        },
        {
            "id": 2,
            "username": "john_doe", 
            "email": "john@example.com",
            "created_at": "2025-10-14",
            "last_active": "2025-10-15 14:25:42",
            "total_conversations": 12,
            "status": "active"
        },
        {
            "id": 3,
            "username": "sarah_m",
            "email": "sarah@example.com", 
            "created_at": "2025-10-15",
            "last_active": "2025-10-15 14:20:33",
            "total_conversations": 1,
            "status": "active"
        }
    ]
    
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "session": session,
        "users": users
    })

@admin_router.get("/system", response_class=HTMLResponse)
async def admin_system(request: Request, session: dict = Depends(get_admin_session)):
    """System monitoring"""
    
    # Mock system metrics
    metrics = {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 34.1,
        "network_io": "1.2 MB/s",
        "response_times": [2.1, 2.3, 1.9, 2.8, 2.2],
        "error_logs": [
            {
                "timestamp": "2025-10-15 14:28:33",
                "level": "WARNING",
                "message": "High response time detected for Supabase query"
            },
            {
                "timestamp": "2025-10-15 14:15:22", 
                "level": "INFO",
                "message": "New deployment successful"
            }
        ]
    }
    
    return templates.TemplateResponse("admin_system.html", {
        "request": request,
        "session": session,
        "metrics": metrics
    })

@admin_router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, session: dict = Depends(get_admin_session)):
    """System settings"""
    
    # Mock configuration settings
    settings = {
        "ai_processing_mode": "hybrid",
        "max_concurrent_users": 100,
        "session_timeout": 48,  # hours
        "enable_registration": True,
        "enable_demo_mode": True,
        "maintenance_mode": False
    }
    
    return templates.TemplateResponse("admin_settings.html", {
        "request": request,
        "session": session,
        "settings": settings
    })

@admin_router.post("/logout")
async def admin_logout(request: Request):
    """Admin logout"""
    token = request.cookies.get("admin_token")
    if token and token in admin_sessions:
        del admin_sessions[token]
    
    response = RedirectResponse(url="/admin/", status_code=302)
    response.delete_cookie("admin_token")
    return response