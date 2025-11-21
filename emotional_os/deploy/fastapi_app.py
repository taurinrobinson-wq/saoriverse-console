"""
FirstPerson Chat - FastAPI Backend
Professional web application for firstperson.chat
"""

import base64
import json
import os
import secrets
from datetime import datetime, timedelta
import uuid

import requests
import uvicorn
# from admin_router import admin_router  # Temporarily commented for testing
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FirstPerson - Personal AI Companion",
    description="Your private space for emotional processing and growth",
    version="2.0.1"  # Force redeploy
)


@app.on_event("startup")
async def _startup_info():
    # Print a small banner for deployment logs (Railway / Heroku / Docker logs)
    try:
        serve_static = os.environ.get("SERVE_STATIC_CHAT", "0")
        print(f"[fastapi_app] STARTUP: SERVE_STATIC_CHAT={serve_static}")
        # Print presence of key environment variables (not values for secrets)
        print(
            f"[fastapi_app] STARTUP: SUPABASE_URL={'set' if SUPABASE_URL else 'unset'}; CURRENT_SAORI_URL={'set' if CURRENT_SAORI_URL else 'unset'}")
    except Exception:
        # Do not raise on startup logging
        pass

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Force HTTPS in production


@app.middleware("http")
async def force_https(request, call_next):
    if request.headers.get("x-forwarded-proto") == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url, status_code=301)
    response = await call_next(request)
    return response

# Include routers
# app.include_router(admin_router)  # Temporarily commented for testing

# Debug route to check what routes are registered


@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to see all registered routes"""
    return {"admin_router_included": "admin_router" in str(app.routes), "total_routes": len(app.routes)}

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="emotional_os/deploy/templates")

# Configuration - using names from .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv(
    "SUPABASE_KEY")  # Support both naming conventions
SUPABASE_AUTH_URL = os.getenv(
    "SUPABASE_AUTH_URL", f"{SUPABASE_URL}/functions/v1/auth-manager" if SUPABASE_URL else None)
CURRENT_SAORI_URL = os.getenv(
    "CURRENT_SAORI_URL") or os.getenv("SUPABASE_FUNCTION_URL")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
# Development debug flag: when set, return more descriptive error messages
# and include masked response bodies in debug logs. Default is off in prod.
DEBUG_DEV = os.getenv("FP_DEBUG_UI", os.getenv("DEV", "0")) == "1"


def _mask_text(s, max_len=1000):
    try:
        if s is None:
            return None
        st = str(s)
        if len(st) > max_len:
            return st[:max_len] + "..."
        return st
    except Exception:
        return "<unserializable>"


def _is_valid_uuid(val: str) -> bool:
    """Return True if val is a valid UUID string."""
    if not val:
        return False
    try:
        uuid.UUID(str(val))
        return True
    except Exception:
        return False

# Pydantic models


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str


class ChatRequest(BaseModel):
    message: str
    mode: str = "hybrid"
    user_id: str


class SessionData(BaseModel):
    username: str
    user_id: str
    created: str
    expires: str


class FirstPersonAuth:
    """Authentication system for FirstPerson"""

    @staticmethod
    def create_session_token(username: str, user_id: str) -> str:
        """Create a secure session token"""
        session_data = {
            "username": username,
            "user_id": user_id,
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=2)).isoformat()
        }
        token = base64.b64encode(json.dumps(session_data).encode()).decode()
        return token

    @staticmethod
    def validate_session_token(token: str) -> dict:
        """Validate and decode session token"""
        try:
            decoded_data = base64.b64decode(token.encode()).decode()
            session_data = json.loads(decoded_data)

            required_fields = ["username", "user_id", "expires"]
            for field in required_fields:
                if field not in session_data:
                    return {"valid": False, "error": f"Missing field: {field}"}

            expires = datetime.fromisoformat(session_data["expires"])
            if datetime.now() < expires:
                return {"valid": True, "data": session_data}
            return {"valid": False, "error": "Session expired"}

        except Exception as e:
            return {"valid": False, "error": f"Token validation error: {str(e)}"}

    @staticmethod
    @staticmethod
    async def authenticate_user(username: str, password: str):
        """Authenticate user with Supabase"""
        try:
            auth_url = SUPABASE_AUTH_URL or f"{SUPABASE_URL}/functions/v1/auth-manager"
            response = requests.post(
                auth_url,
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "authenticate",
                    "username": username,
                    "password": password
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("authenticated"):
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "username": username
                    }
                return {"success": False, "message": "Invalid credentials"}
            # include masked response body in debug mode to aid development
            if DEBUG_DEV:
                try:
                    body = response.json()
                except Exception:
                    body = _mask_text(getattr(response, 'text', None), 2000)
                return {"success": False, "message": "Authentication service error", "debug_body": body}
            return {"success": False, "message": "Authentication service error"}

        except Exception as e:
            if DEBUG_DEV:
                return {"success": False, "message": f"Login error: {str(e)}", "debug_exception": _mask_text(str(e), 2000)}
            return {"success": False, "message": f"Login error: {str(e)}"}

    @staticmethod
    async def create_user(username: str, password: str) -> dict:
        """Create new user account"""
        try:
            auth_url = SUPABASE_AUTH_URL or f"{SUPABASE_URL}/functions/v1/auth-manager"
            response = requests.post(
                auth_url,
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "create_user",
                    "username": username,
                    "password": password,
                    "created_at": datetime.now().isoformat()
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": data.get("success"), "message": data.get("error", "Account created")}
            if DEBUG_DEV:
                try:
                    body = response.json()
                except Exception:
                    body = _mask_text(getattr(response, 'text', None), 2000)
                return {"success": False, "message": "Failed to create account", "debug_body": body}
            return {"success": False, "message": "Failed to create account"}

        except Exception as e:
            if DEBUG_DEV:
                return {"success": False, "message": f"Registration error: {str(e)}", "debug_exception": _mask_text(str(e), 2000)}
            return {"success": False, "message": f"Registration error: {str(e)}"}

# Routes


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main landing page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/app", response_class=HTMLResponse)
async def chat_app(request: Request):
    """Main chat application"""
    # Gate serving the static chat HTML behind an environment flag. For production static-host deployments
    # prefer serving the static site from a CDN/Netlify/Vercel and keep this FastAPI container for admin/dev only.
    # Set SERVE_STATIC_CHAT=1 in environments where you want the FastAPI app to serve the static template.
    if os.environ.get("SERVE_STATIC_CHAT", "0") != "1":
        # Not serving static chat from this process. Return 404 so production containers don't expose it.
        raise HTTPException(status_code=404, detail="Not available")
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/api/login")
async def login(login_data: LoginRequest):
    """User login endpoint"""
    result = await FirstPersonAuth.authenticate_user(
        login_data.username,
        login_data.password
    )

    if result["success"]:
        # Create session token
        token = FirstPersonAuth.create_session_token(
            result["username"],
            result["user_id"]
        )
        return {
            "success": True,
            "token": token,
            "user_id": result["user_id"],
            "username": result["username"]
        }
    # In dev mode return a JSON debug payload, otherwise raise standard HTTP error
    if DEBUG_DEV:
        debug_info = result.get("debug_body") or result.get("debug_exception")
        return JSONResponse(status_code=401, content={"success": False, "message": result["message"], "debug": debug_info})
    raise HTTPException(status_code=401, detail=result["message"])


@app.post("/api/register")
async def register(register_data: RegisterRequest):
    """User registration endpoint"""
    if register_data.password != register_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if len(register_data.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters")

    result = await FirstPersonAuth.create_user(
        register_data.username,
        register_data.password
    )

    if result["success"]:
        return {"success": True, "message": "Account created successfully"}
    if DEBUG_DEV:
        debug_info = result.get("debug_body") or result.get("debug_exception")
        return JSONResponse(status_code=400, content={"success": False, "message": result["message"], "debug": debug_info})
    raise HTTPException(status_code=400, detail=result["message"])


@app.post("/api/chat")
async def chat(chat_data: ChatRequest):
    """Process chat message with AI"""
    # Structured tracing/logging for debugging message flows
    saori_url = CURRENT_SAORI_URL or f"{SUPABASE_URL}/functions/v1/saori-fixed"
    # Build the outgoing payload so we can log/inspect it when debugging
    payload = {
        "message": chat_data.message,
        "mode": chat_data.mode,
        "user_id": chat_data.user_id
    }

    trace_entry = {
        "ts": datetime.utcnow().isoformat() + 'Z',
        "user_id": chat_data.user_id,
        "mode": chat_data.mode,
        "message_preview": (chat_data.message[:200] + '...') if len(chat_data.message) > 200 else chat_data.message,
        "saori_url": saori_url,
        "request_payload": _mask_text(json.dumps(payload, ensure_ascii=False), 2000)
    }

    # Quick validation: if user_id is not a UUID, fail fast in debug mode to make the error visible
    if not _is_valid_uuid(chat_data.user_id):
        if DEBUG_DEV:
            return {
                "success": False,
                "reply": "Invalid user_id format (expected UUID).",
                "debug": {"user_id": chat_data.user_id, "request_payload": trace_entry.get("request_payload")}
            }
        return {"success": False, "reply": "Invalid request."}

    start = datetime.utcnow()
    try:
        response = requests.post(
            saori_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        duration = (datetime.utcnow() - start).total_seconds()
        trace_entry.update({
            "duration_s": duration,
            "status_code": getattr(response, 'status_code', None)
        })

        try:
            result = response.json()
        except Exception:
            # If parsing JSON failed, capture raw text when in debug mode.
            result = None
            raw_text = None
            try:
                raw_text = response.text
            except Exception:
                raw_text = None

        trace_entry["response_preview"] = None
        if isinstance(result, dict):
            trace_entry["response_preview"] = {
                "reply": (result.get('reply') or '')[:200],
                "glyph": result.get('glyph'),
                "processing_time": result.get('processing_time')
            }
        else:
            # when no JSON result, include masked raw text in debug mode
            if DEBUG_DEV:
                trace_entry["response_preview"] = {
                    "raw": _mask_text(getattr(response, 'text', None), 2000)}

        # append trace to log file
        try:
            with open("/workspaces/saoriverse-console/debug_chat.log", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

        if response.status_code == 200 and isinstance(result, dict):
            try:
                from emotional_os.deploy.reply_utils import polish_ai_reply
            except Exception:
                def polish_ai_reply(x):
                    return x or "I hear you — tell me more when you're ready."

            return {
                "success": True,
                "reply": polish_ai_reply(result.get("reply", "I'm here to listen.")),
                "glyph": result.get("glyph", {}),
                "processing_time": result.get("processing_time", 0)
            }

        # Non-200 from AI service — return a more descriptive reply in debug mode
        if DEBUG_DEV:
            debug_body = None
            try:
                debug_body = response.json()
            except Exception:
                debug_body = _mask_text(getattr(response, 'text', None), 2000)
            return {
                "success": False,
                "reply": f"AI service returned HTTP {response.status_code}. See debug info.",
                "debug": {"status_code": response.status_code, "body": debug_body, "request_payload": trace_entry.get("request_payload")}
            }

        return {
            "success": False,
            "reply": f"AI service returned HTTP {response.status_code}. Please try again shortly."
        }

    except Exception as e:
        duration = (datetime.utcnow() - start).total_seconds()
        trace_entry.update({
            "duration_s": duration,
            "exception": str(e)
        })
        try:
            with open("/workspaces/saoriverse-console/debug_chat.log", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

        # On exception, include error message in debug mode to aid development.
        if DEBUG_DEV:
            return {
                "success": False,
                "reply": "I'm having trouble connecting right now.",
                "debug_exception": _mask_text(str(e), 2000),
                "request_payload": trace_entry.get("request_payload")
            }

        return {
            "success": False,
            "reply": "I'm having trouble connecting right now, but your feelings are still valid."
        }


@app.get("/api/validate-session")
async def validate_session(token: str):
    """Validate session token"""
    result = FirstPersonAuth.validate_session_token(token)
    if result["valid"]:
        return {"valid": True, "data": result["data"]}
    if DEBUG_DEV:
        debug_info = result.get("debug_exception")
        return JSONResponse(status_code=401, content={"valid": False, "error": result["error"], "debug": debug_info})
    raise HTTPException(status_code=401, detail=result["error"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment_check": {
            "supabase_url": "✓" if SUPABASE_URL else "✗",
            "supabase_key": "✓" if SUPABASE_KEY else "✗",
            "supabase_function_url": "✓" if CURRENT_SAORI_URL else "✗"
        }
    }

# Try to include server-side conversation save router if present.
# Import guarded to avoid circular import issues during module init.
try:
    from emotional_os.deploy.save_conv_api import router as save_conv_router

    app.include_router(save_conv_router)
    print("[fastapi_app] Included save_conv_api router")
except Exception as e:
    print(f"[fastapi_app] Could not include save_conv_api router: {e}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
