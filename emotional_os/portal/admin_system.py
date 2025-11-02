"""
FirstPerson Admin Portal
Comprehensive administrative interface for managing the FirstPerson platform
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "admin_secret_change_in_production")

# Pydantic models
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class UserModerationRequest(BaseModel):
    user_id: str
    action: str  # suspend, activate, delete
    reason: Optional[str] = None

class SystemConfigRequest(BaseModel):
    setting_name: str
    setting_value: str

# Admin Authentication Class
class AdminAuth:
    """Handle admin authentication and session management"""

    ADMIN_USERS = {
        "admin": {
            "password_hash": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # "admin"
            "permissions": ["all"]
        },
        "taurinrobinson": {  # Your admin account
            "password_hash": hashlib.sha256("firstperson2025".encode()).hexdigest(),
            "permissions": ["all"]
        }
    }

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_admin_credentials(username: str, password: str) -> bool:
        """Verify admin login credentials"""
        if username in AdminAuth.ADMIN_USERS:
            password_hash = AdminAuth.hash_password(password)
            return password_hash == AdminAuth.ADMIN_USERS[username]["password_hash"]
        return False

    @staticmethod
    def create_admin_session(username: str) -> str:
        """Create secure admin session token"""
        import base64
        session_data = {
            "username": username,
            "is_admin": True,
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(hours=8)).isoformat(),
            "permissions": AdminAuth.ADMIN_USERS[username]["permissions"]
        }
        token = base64.b64encode(json.dumps(session_data).encode()).decode()
        return token

    @staticmethod
    def validate_admin_session(token: str) -> Dict[str, Any]:
        """Validate admin session token"""
        try:
            import base64
            decoded_data = base64.b64decode(token.encode()).decode()
            session_data = json.loads(decoded_data)

            # Check expiration
            expires = datetime.fromisoformat(session_data["expires"])
            if datetime.now() < expires and session_data.get("is_admin"):
                return {"valid": True, "data": session_data}
            return {"valid": False, "error": "Session expired"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

# Admin dependency for protected routes
async def require_admin(request: Request):
    """Dependency to require admin authentication"""
    admin_token = request.cookies.get("admin_session")
    if not admin_token:
        raise HTTPException(status_code=401, detail="Admin authentication required")

    session_result = AdminAuth.validate_admin_session(admin_token)
    if not session_result["valid"]:
        raise HTTPException(status_code=401, detail="Invalid admin session")

    return session_result["data"]

# Database Interface for Admin Operations
class AdminDatabase:
    """Handle admin database operations"""

    @staticmethod
    async def get_all_users() -> List[Dict[str, Any]]:
        """Get all registered users"""
        try:
            # This would connect to your Supabase auth table
            # For now, return mock data - implement actual DB query
            return [
                {
                    "id": "user1",
                    "username": "demo_user",
                    "email": "demo@example.com",
                    "created_at": "2025-10-15T10:00:00",
                    "last_login": "2025-10-15T12:00:00",
                    "status": "active",
                    "conversation_count": 15
                },
                {
                    "id": "user2",
                    "username": "test_user",
                    "email": "test@example.com",
                    "created_at": "2025-10-14T15:30:00",
                    "last_login": "2025-10-15T09:15:00",
                    "status": "active",
                    "conversation_count": 8
                }
            ]
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    @staticmethod
    async def get_system_stats() -> Dict[str, Any]:
        """Get system statistics"""
        try:
            # Implement actual stats from your database
            return {
                "total_users": 156,
                "active_users_today": 23,
                "total_conversations": 1247,
                "conversations_today": 89,
                "avg_response_time": 2.3,
                "system_uptime": "99.8%",
                "storage_used": "2.4 GB",
                "api_calls_today": 432
            }
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {}

    @staticmethod
    async def get_recent_conversations(limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent conversations for moderation"""
        try:
            # Implement actual conversation fetching
            return [
                {
                    "id": "conv1",
                    "user_id": "user1",
                    "username": "demo_user",
                    "timestamp": "2025-10-15T14:30:00",
                    "message": "I'm feeling overwhelmed with work stress lately",
                    "response": "I understand that work stress can feel overwhelming. What specific aspects are weighing on you most?",
                    "sentiment": "negative",
                    "flagged": False
                },
                {
                    "id": "conv2",
                    "user_id": "user2",
                    "username": "test_user",
                    "timestamp": "2025-10-15T14:15:00",
                    "message": "Had a great day today, feeling optimistic",
                    "response": "That's wonderful to hear! Optimism can be such a powerful force. What made today particularly great?",
                    "sentiment": "positive",
                    "flagged": False
                }
            ]
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return []

# Admin Routes

@admin_router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})

@admin_router.post("/login")
async def admin_login(request: Request, username: str = Form(), password: str = Form()):
    """Handle admin login"""
    if AdminAuth.verify_admin_credentials(username, password):
        session_token = AdminAuth.create_admin_session(username)
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        response.set_cookie(
            key="admin_session",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=28800  # 8 hours
        )
        return response
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": "Invalid credentials"}
    )

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin_user = Depends(require_admin)):
    """Main admin dashboard"""
    stats = await AdminDatabase.get_system_stats()
    recent_users = await AdminDatabase.get_all_users()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "admin_user": admin_user,
        "stats": stats,
        "recent_users": recent_users[:10]  # Show last 10 users
    })

@admin_router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, admin_user = Depends(require_admin)):
    """User management page"""
    users = await AdminDatabase.get_all_users()

    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "admin_user": admin_user,
        "users": users
    })

@admin_router.get("/conversations", response_class=HTMLResponse)
async def admin_conversations(request: Request, admin_user = Depends(require_admin)):
    """Conversation moderation page"""
    conversations = await AdminDatabase.get_recent_conversations()

    return templates.TemplateResponse("admin/conversations.html", {
        "request": request,
        "admin_user": admin_user,
        "conversations": conversations
    })

@admin_router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, admin_user = Depends(require_admin)):
    """System settings page"""
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "admin_user": admin_user
    })

@admin_router.post("/logout")
async def admin_logout():
    """Admin logout"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_session")
    return response

# API endpoints for admin operations

@admin_router.post("/api/users/{user_id}/moderate")
async def moderate_user(
    user_id: str,
    moderation: UserModerationRequest,
    admin_user = Depends(require_admin)
):
    """Moderate user account"""
    try:
        # Implement actual user moderation
        return {
            "success": True,
            "message": f"User {user_id} {moderation.action}ed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/api/stats/export")
async def export_stats(admin_user = Depends(require_admin)):
    """Export system statistics"""
    try:
        stats = await AdminDatabase.get_system_stats()
        users = await AdminDatabase.get_all_users()
        conversations = await AdminDatabase.get_recent_conversations(1000)

        export_data = {
            "export_date": datetime.now().isoformat(),
            "stats": stats,
            "user_count": len(users),
            "conversation_count": len(conversations),
            "admin": admin_user["username"]
        }

        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/api/system/config")
async def update_system_config(
    config: SystemConfigRequest,
    admin_user = Depends(require_admin)
):
    """Update system configuration"""
    try:
        # Implement actual config updates
        return {
            "success": True,
            "message": f"Setting {config.setting_name} updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
