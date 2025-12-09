"""
FastAPI backend for Velinor game engine.
Exposes Velinor orchestrator as REST API endpoints.
"""

from fastapi import FastAPI, HTTPException
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

# Mount Next.js static files if in production
NEXT_BUILD_PATH = Path(__file__).parent / "velinor-web" / ".next"
if NEXT_BUILD_PATH.exists():
    # Serve Next.js static assets
    public_path = Path(__file__).parent / "velinor-web" / "public"
    if public_path.exists():
        app.mount("/assets", StaticFiles(directory=str(public_path / "assets")), name="assets")

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

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Velinor Game API",
        "version": "1.0.0"
    }


@app.post("/api/game/start", response_model=GameResponse)
def start_game(request: StartGameRequest):
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
            return {"session_id": session_id, "state": formatted_state}
        else:
            raise HTTPException(status_code=400, detail="Game session not initialized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/{session_id}/save")
def save_game(session_id: str):
    """Save current game progress."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        orchestrator = SESSIONS[session_id]
        save_path = f"saves/{session_id}.json"
        orchestrator.save_game(save_path)
        
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


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
