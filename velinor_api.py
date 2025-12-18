"""
FastAPI backend for Velinor game engine.
Exposes Velinor orchestrator as REST API endpoints.
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from pathlib import Path
import sys
import traceback
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from velinor.engine import VelinorTwineOrchestrator, VelinorEngine
except ImportError as e:
    print(f"Error importing Velinor engine: {e}")
    traceback.print_exc()
    print("\nTrying alternative import...")
    try:
        from velinor.engine.orchestrator import VelinorTwineOrchestrator
        from velinor.engine.core import VelinorEngine
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        traceback.print_exc()
        raise

# Local auth/persistence
try:
    from velinor.auth import (
        create_user,
        authenticate_user,
        create_access_token,
        verify_token,
        save_profile,
        load_profile,
        get_user_by_id,
    )
except Exception:
    create_user = authenticate_user = create_access_token = verify_token = save_profile = load_profile = get_user_by_id = None

# ============================================================================
# SETUP
# ============================================================================

app = FastAPI(
    title="Velinor Game API",
    description="REST API for Velinor: Remnants of the Tone",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Next.js static files
NEXT_BUILD_PATH = Path(__file__).parent / "velinor-web" / ".next"
PUBLIC_PATH = Path(__file__).parent / "velinor-web" / "public"

# Conditional mounting: only mount Next static when the build exists or when explicitly enabled
NEXT_STATIC_DIR = NEXT_BUILD_PATH / "static"
MOUNT_STATIC_ENV = os.environ.get("MOUNT_STATIC", "true").lower() in ("1", "true", "yes")

if PUBLIC_PATH.exists():
    # Mount public assets (always mount if present)
    app.mount("/public", StaticFiles(directory=str(PUBLIC_PATH)), name="public")

if NEXT_STATIC_DIR.exists() and MOUNT_STATIC_ENV:
    app.mount("/_next/static", StaticFiles(directory=str(NEXT_STATIC_DIR)), name="next-static")
else:
    # Informational log to help debugging in dev when the Next build is not present
    print(f"Skipping mount of Next static files: exists={NEXT_STATIC_DIR.exists()} MOUNT_STATIC={MOUNT_STATIC_ENV}")

# Mount game asset directories (backgrounds and npcs) so frontend can load images.
# Prefer the frontend `velinor-web/public/assets/...` location, but fallback to
# the older `velinor/backgrounds` and `velinor/npcs` if needed.
ASSETS_BG_CANDIDATES = [
    Path(__file__).parent / 'velinor-web' / 'public' / 'assets' / 'backgrounds',
    Path(__file__).parent / 'velinor' / 'backgrounds'
]
ASSETS_NPC_CANDIDATES = [
    Path(__file__).parent / 'velinor-web' / 'public' / 'assets' / 'npcs',
    Path(__file__).parent / 'velinor' / 'npcs'
]

def _pick_existing_path(candidates):
    for p in candidates:
        if p.exists():
            return p
    return None

ASSETS_BG_DIR = _pick_existing_path(ASSETS_BG_CANDIDATES)
ASSETS_NPC_DIR = _pick_existing_path(ASSETS_NPC_CANDIDATES)

if ASSETS_BG_DIR:
    app.mount('/assets/backgrounds', StaticFiles(directory=str(ASSETS_BG_DIR)), name='assets-backgrounds')
else:
    print(f"Background assets folder not found in candidates: {ASSETS_BG_CANDIDATES}")

if ASSETS_NPC_DIR:
    app.mount('/assets/npcs', StaticFiles(directory=str(ASSETS_NPC_DIR)), name='assets-npcs')
else:
    print(f"NPC assets folder not found in candidates: {ASSETS_NPC_CANDIDATES}")

# In-memory session storage (use Redis/database in production)
SESSIONS: Dict[str, VelinorTwineOrchestrator] = {}

# ============================================================================
# MODELS
# ============================================================================

class StartGameRequest(BaseModel):
    player_name: str = "Traveler"
    story_path: Optional[str] = None


class PlayerActionRequest(BaseModel):
    choice_index: Optional[int] = None
    player_input: Optional[str] = None


class GameState(BaseModel):
    passage_id: str
    passage_name: str
    main_dialogue: str
    npc_name: Optional[str] = None
    npc_dialogue: Optional[str] = None
    background_image: Optional[str] = None
    choices: List[Dict[str, Any]]
    clarifying_question: Optional[str] = None
    has_clarifying_question: bool = False
    game_state: Optional[Dict[str, Any]] = None


class GameResponse(BaseModel):
    session_id: str
    state: Dict[str, Any]


class ActionResponse(BaseModel):
    session_id: str
    state: Dict[str, Any]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Velinor Game API",
        "version": "1.0.0"
    }


@app.post("/api/auth/register")
def api_register(payload: Dict[str, str]):
    """Register a new user. Expects JSON: {"username": "alice", "password": "..."} """
    if not create_user:
        raise HTTPException(status_code=501, detail="Auth not available")
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")
    try:
        user = create_user(username, password)
        token = create_access_token(user['id']) if create_access_token else None
        return {"user": {"id": user['id'], "username": user['username']}, "access_token": token}
    except ValueError as e:
        if str(e) == 'username_taken':
            raise HTTPException(status_code=409, detail="username taken")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/login")
def api_login(payload: Dict[str, str]):
    """Login and receive access token."""
    if not authenticate_user:
        raise HTTPException(status_code=501, detail="Auth not available")
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(user['id']) if create_access_token else None
    return {"user": {"id": user['id'], "username": user['username']}, "access_token": token}



@app.post("/api/game/start", response_model=GameResponse)
def start_game(request: StartGameRequest, authorization: Optional[str] = Header(None)):
    """
    Start a new game session.
    
    Returns:
        session_id: Unique session identifier
        state: Initial game state
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Create game engine (no parameters)
        engine = VelinorEngine()
        
        # Create session with player name
        engine.create_session(player_name=request.player_name)
        
        # Create orchestrator
        story_path = request.story_path or str(PROJECT_ROOT / "velinor" / "stories" / "sample_story.json")
        orchestrator = VelinorTwineOrchestrator(
            game_engine=engine,
            story_path=story_path
        )
        # If an Authorization token is present and valid, attempt to load user profile
        if authorization and verify_token:
            token = authorization.split('Bearer ')[-1].strip()
            user_id = verify_token(token)
            if user_id:
                profile = load_profile(user_id) if load_profile else None
                if profile:
                    # Populate player stats from stored profile
                    try:
                        p = engine.session.player
                        # allowed keys: courage, wisdom, empathy, resolve, resonance, glyphs_collected, choices_made
                        if 'courage' in profile:
                            p.courage = float(profile.get('courage', p.courage))
                        if 'wisdom' in profile:
                            p.wisdom = float(profile.get('wisdom', p.wisdom))
                        if 'empathy' in profile:
                            p.empathy = float(profile.get('empathy', p.empathy))
                        if 'resolve' in profile:
                            p.resolve = float(profile.get('resolve', p.resolve))
                        if 'resonance' in profile:
                            p.resonance = float(profile.get('resonance', p.resonance))
                        if 'glyphs_collected' in profile:
                            p.glyphs_collected = profile.get('glyphs_collected', p.glyphs_collected)
                        if 'choices_made' in profile:
                            p.choices_made = profile.get('choices_made', p.choices_made)
                        if 'story_progress' in profile:
                            engine.session.story_progress = profile.get('story_progress', engine.session.story_progress)
                    except Exception:
                        pass

        # Start game
        initial_state = orchestrator.start_game()
        
        # Store session
        SESSIONS[session_id] = orchestrator
        
        return GameResponse(
            session_id=session_id,
            state=initial_state
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/{session_id}/action", response_model=ActionResponse)
def take_action(session_id: str, request: PlayerActionRequest):
    """
    Process player action (choice or text input).
    
    Args:
        session_id: Session identifier from /start
        choice_index: Index of selected choice (0-based)
        player_input: Free-form text input from player
    
    Returns:
        Updated game state
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        orchestrator = SESSIONS[session_id]
        
        # Process action
        next_state = orchestrator.process_player_action(
            choice_index=request.choice_index,
            player_input=request.player_input,
            player_id="player_1"
        )
        
        return ActionResponse(
            session_id=session_id,
            state=next_state
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/game/{session_id}")
def get_game_state(session_id: str):
    """Get current game state for a session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        orchestrator = SESSIONS[session_id]
        # Get the current passage rendering if twine_session exists
        if orchestrator.twine_session:
            current_state = orchestrator.twine_session._render_passage(
                orchestrator.twine_session.context.current_passage_id
            )
            formatted_state = orchestrator._format_ui_state(current_state)
            
            # Include REMNANTS debug info
            if orchestrator.remnants_manager:
                formatted_state['_debug_remnants'] = {
                    'initialized': True,
                    'npc_count': len(orchestrator.remnants_manager.npcs),
                    'ravi_state': orchestrator.remnants_manager.get_npc_state('Ravi')
                }
            
            return {"session_id": session_id, "state": formatted_state}
        else:
            raise HTTPException(status_code=400, detail="Game session not initialized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/{session_id}/save")
def save_game(session_id: str, authorization: Optional[str] = Header(None)):
    """Save current game progress."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        orchestrator = SESSIONS[session_id]
        # Persist session snapshot to file
        save_path = f"saves/{session_id}.json"
        orchestrator.save_game(save_path)

        # If user token provided, also persist profile to auth DB
        if authorization and verify_token:
            token = authorization.split('Bearer ')[-1].strip()
            user_id = verify_token(token)
            if user_id and save_profile:
                # Build profile dict
                player = orchestrator.game_engine.session.player
                profile = {
                    'courage': player.courage,
                    'wisdom': player.wisdom,
                    'empathy': player.empathy,
                    'resolve': player.resolve,
                    'resonance': player.resonance,
                    'glyphs_collected': player.glyphs_collected,
                    'choices_made': player.choices_made,
                    'story_progress': orchestrator.game_engine.get_story_progress()
                }
                try:
                    save_profile(user_id, profile)
                except Exception:
                    pass

        return {
            "status": "saved",
            "session_id": session_id,
            "save_path": save_path
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/{session_id}/load")
def load_game(session_id: str):
    """Load saved game progress."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        orchestrator = SESSIONS[session_id]
        load_path = f"saves/{session_id}.json"
        state = orchestrator.load_game(load_path)
        
        return {
            "status": "loaded",
            "session_id": session_id,
            "state": state
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/game/{session_id}")
def end_session(session_id: str):
    """End a game session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del SESSIONS[session_id]
    return {
        "status": "session_ended",
        "session_id": session_id
    }


@app.get("/api/sessions")
def list_sessions():
    """List all active sessions (admin endpoint)."""
    return {
        "active_sessions": list(SESSIONS.keys()),
        "count": len(SESSIONS)
    }


@app.get("/api/debug/npc-remnants/{session_id}")
def debug_npc_remnants(session_id: str):
    """Debug endpoint: inspect REMNANTS manager state for a session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        orchestrator = SESSIONS[session_id]
        if orchestrator.remnants_manager:
            npc_states = orchestrator.remnants_manager.get_all_npc_states()
            return {
                "session_id": session_id,
                "remnants_initialized": True,
                "npc_count": len(npc_states),
                "npcs": npc_states
            }
        else:
            return {
                "session_id": session_id,
                "remnants_initialized": False,
                "error": "REMNANTS manager not initialized"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Catch-all for frontend GET routes (placed last to avoid method conflicts)
# NOTE: Does NOT match /api/* routes, allowing debug endpoints to work
@app.get("/{path:path}")
async def catch_all(path: str):
    """Catch-all for frontend GET routes that aren't handled by API.

    This is intentionally a GET-only route and placed at the end of the
    module to avoid creating a path that would respond to GET but block
    POST/PUT methods elsewhere (which can result in a 405 Method Not Allowed
    for valid API endpoints).
    
    Does NOT match paths starting with /api/ to preserve API endpoints.
    """
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    return {"error": "not found"}

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
