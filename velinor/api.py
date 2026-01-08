"""
Velinor Game API Layer (Phase 6)
FastAPI REST backend for game state management and player actions

Provides endpoints for:
- Game session creation and management
- Player action processing
- Game state serialization
- Save/load functionality
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from datetime import datetime
from enum import Enum
import uuid

from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.game_state import GameStateSnapshot, GameStateBuilder, GameStateValidator
from velinor.engine.save_system import SaveManager
from velinor.engine.load_system import LoadManager

# ==================== Pydantic Models ====================


class GameActionRequest(BaseModel):
    """Request body for game actions"""
    choice_index: Optional[int] = None
    player_input: Optional[str] = None


class SaveGameRequest(BaseModel):
    """Request to save a game"""
    save_name: str
    auto_save: bool = False


class LoadGameRequest(BaseModel):
    """Request to load a game"""
    slot_id: str


class GameStateResponse(BaseModel):
    """Serialized game state for API response"""
    session_id: str
    player_name: str
    current_scene: str
    available_choices: List[Dict[str, Any]]
    current_phase: str
    current_day: int
    game_completed: bool
    last_action_timestamp: str


class SessionMetadata(BaseModel):
    """Session metadata"""
    session_id: str
    player_name: str
    created_at: str
    last_action_at: str
    phase: str


class SaveSlotInfo(BaseModel):
    """Information about a save slot"""
    slot_id: str
    player_name: str
    save_name: str
    timestamp: str
    day: int
    phase: str


class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ==================== FastAPI Setup ====================

app = FastAPI(
    title="Velinor Game API",
    description="REST API for Velinor game engine",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Session Management ====================

class GameSession:
    """Represents an active game session"""
    
    def __init__(self, session_id: str, player_name: str):
        self.session_id = session_id
        self.player_name = player_name
        try:
            # Try to initialize orchestrator with minimal requirements
            from velinor.engine.core import VelinorEngine, GameSession as EngineSession
            game_engine = VelinorEngine()
            self.orchestrator = VelinorTwineOrchestrator(
                game_engine=game_engine,
                story_path="",  # Empty path for now
                player_name=player_name
            )
        except Exception as e:
            # Fallback: create a mock orchestrator if full orchestrator fails
            self.orchestrator = self._create_mock_orchestrator(player_name)
        
        self.created_at = datetime.now().isoformat()
        self.last_action_at = datetime.now().isoformat()
        self.action_count = 0
    
    def _create_mock_orchestrator(self, player_name: str):
        """Create a mock orchestrator for testing"""
        from velinor.engine.trait_system import TraitProfiler
        from velinor.engine.coherence_calculator import CoherenceCalculator
        from velinor.engine.event_timeline import EventTimeline
        from velinor.engine.ending_system import EndingManager
        from velinor.engine.save_system import SaveManager
        from velinor.engine.load_system import LoadManager
        from velinor.engine.npc_response_engine import NPCResponseEngine
        
        class MockOrchestrator:
            def __init__(self, player_name):
                self.player_name = player_name
                self.trait_profiler = TraitProfiler(player_name)
                self.coherence_calculator = CoherenceCalculator(self.trait_profiler)
                self.npc_response_engine = NPCResponseEngine(self.trait_profiler)
                self.event_timeline = EventTimeline()
                self.ending_manager = EndingManager()
                self.save_manager = SaveManager()
                self.load_manager = LoadManager()
                self.current_scene_choices = ["Choice 1", "Choice 2"]
                self.game_state = {}
            
            def process_player_choice(self, choice_index):
                if not isinstance(choice_index, int) or choice_index < 0 or choice_index >= len(self.current_scene_choices):
                    raise ValueError(f"Invalid choice index: {choice_index}")
                return {"action": "processed", "choice": choice_index}
            
            def process_player_input(self, player_input):
                return {"action": "processed", "input": player_input}
            
            def process_player_action(self, choice_index=None, player_input=None):
                if choice_index is not None:
                    return self.process_player_choice(choice_index)
                elif player_input:
                    return self.process_player_input(player_input)
                else:
                    raise ValueError("No action provided")
            
            def get_status(self):
                return {
                    "player_name": self.player_name,
                    "phase": "intro",
                    "day": 0,
                    "completed": False,
                    "coherence_score": 50.0,
                    "coherence_level": "MIXED",
                    "primary_trait": "empathy",
                    "building_stability": 100,
                    "malrik_stress": 0,
                    "elenya_stress": 0,
                }
        
        return MockOrchestrator(player_name)
    
    def serialize_state(self) -> Dict[str, Any]:
        """Serialize current game state for API response"""
        try:
            # Get orchestrator status
            status = self.orchestrator.get_status()
            
            # Get available choices if in an interactive scene
            available_choices = []
            if hasattr(self.orchestrator, 'current_scene_choices'):
                available_choices = [
                    {"index": i, "text": choice}
                    for i, choice in enumerate(self.orchestrator.current_scene_choices)
                ]
            
            return {
                "session_id": self.session_id,
                "player_name": self.player_name,
                "current_phase": status.get("phase", "unknown"),
                "current_day": status.get("day", 0),
                "game_completed": status.get("completed", False),
                "available_choices": available_choices,
                "orchestrator_status": status,
            }
        except Exception as e:
            return {
                "session_id": self.session_id,
                "player_name": self.player_name,
                "error": str(e),
            }


class SessionStore:
    """In-memory session storage"""
    
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
    
    def create_session(self, player_name: str) -> str:
        """Create a new game session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = GameSession(session_id, player_name)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        """Get an active session"""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[str]:
        """List all active session IDs"""
        return list(self.sessions.keys())
    
    def get_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)


# Global session store
session_store = SessionStore()

# ==================== Dependency ====================


def get_session(session_id: str) -> GameSession:
    """Dependency to get and validate session"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session


# ==================== Health Check ====================


@app.get("/health")
async def health_check() -> ApiResponse:
    """Health check endpoint"""
    return ApiResponse(
        success=True,
        message="Velinor API is healthy",
        data={
            "status": "operational",
            "active_sessions": session_store.get_session_count(),
            "timestamp": datetime.now().isoformat(),
        }
    )


# ==================== Game Session Endpoints ====================


@app.post("/api/game/start")
async def start_game(player_name: str = "Traveler") -> ApiResponse:
    """
    Start a new game session
    
    Query params:
    - player_name: Name of the player (default: "Traveler")
    
    Returns: session_id and initial game state
    """
    try:
        session_id = session_store.create_session(player_name)
        session = session_store.get_session(session_id)
        
        return ApiResponse(
            success=True,
            message=f"Game started for {player_name}",
            data={
                "session_id": session_id,
                "player_name": player_name,
                "game_state": session.serialize_state(),
                "created_at": session.created_at,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/game/{session_id}")
async def get_game_state(session: GameSession = Depends(get_session)) -> ApiResponse:
    """
    Get current game state for a session
    
    Returns: Current state, available choices, phase, day, etc.
    """
    try:
        session.last_action_at = datetime.now().isoformat()
        state = session.serialize_state()
        
        return ApiResponse(
            success=True,
            message="Game state retrieved",
            data=state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/game/{session_id}")
async def end_game(session: GameSession = Depends(get_session)) -> ApiResponse:
    """
    End a game session and clean up
    
    Returns: Confirmation and final state
    """
    try:
        final_state = session.serialize_state()
        session_id = session.session_id
        
        session_store.delete_session(session_id)
        
        return ApiResponse(
            success=True,
            message=f"Session {session_id} ended",
            data={
                "session_id": session_id,
                "final_state": final_state,
                "duration_seconds": (
                    datetime.fromisoformat(session.last_action_at) -
                    datetime.fromisoformat(session.created_at)
                ).total_seconds(),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Game Action Endpoints ====================


@app.post("/api/game/{session_id}/action")
async def take_action(
    request: GameActionRequest,
    session: GameSession = Depends(get_session)
) -> ApiResponse:
    """
    Process a player action (choice or input)
    
    Body:
    - choice_index: Index of choice selected (optional)
    - player_input: Free-form player input (optional)
    
    Returns: New game state after action
    """
    try:
        # Validate that at least one action is provided
        if request.choice_index is None and not request.player_input:
            raise ValueError("Either choice_index or player_input must be provided")
        
        session.last_action_at = datetime.now().isoformat()
        session.action_count += 1
        
        # Process action through orchestrator
        try:
            if request.choice_index is not None:
                # Process choice
                action_result = session.orchestrator.process_player_choice(
                    request.choice_index
                )
            else:
                # Process free-form input
                action_result = session.orchestrator.process_player_input(
                    request.player_input
                )
        except (ValueError, IndexError) as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        
        new_state = session.serialize_state()
        
        return ApiResponse(
            success=True,
            message="Action processed",
            data={
                "action_result": action_result,
                "new_state": new_state,
                "action_count": session.action_count,
            }
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Save/Load Endpoints ====================


@app.post("/api/game/{session_id}/save")
async def save_game(
    request: SaveGameRequest,
    session: GameSession = Depends(get_session)
) -> ApiResponse:
    """
    Save current game state
    
    Body:
    - save_name: Name for this save
    - auto_save: Whether this is an auto-save (default: false)
    
    Returns: Save slot info
    """
    try:
        session.last_action_at = datetime.now().isoformat()
        
        # Build game state snapshot
        state_snapshot = GameStateBuilder.build_from_orchestrator(session.orchestrator)
        
        # Save to file
        save_manager = SaveManager()
        success, message, slot_id = save_manager.save_game(
            state_snapshot,
            request.save_name,
            request.auto_save
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        return ApiResponse(
            success=True,
            message=message,
            data={
                "slot_id": slot_id,
                "save_name": request.save_name,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/{session_id}/load")
async def load_game(
    request: LoadGameRequest,
    session: GameSession = Depends(get_session)
) -> ApiResponse:
    """
    Load a saved game into current session
    
    Body:
    - slot_id: ID of save slot to load
    
    Returns: Loaded game state
    """
    try:
        session.last_action_at = datetime.now().isoformat()
        
        # Load save file
        load_manager = LoadManager()
        success, message, snapshot = load_manager.load_game(request.slot_id)
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        # Restore to orchestrator
        success, message = load_manager.restore_to_orchestrator(snapshot, session.orchestrator)
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        new_state = session.serialize_state()
        
        return ApiResponse(
            success=True,
            message="Game loaded successfully",
            data={
                "loaded_save": request.slot_id,
                "player_name": snapshot.player_name,
                "game_state": new_state,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/game/{session_id}/save-slots")
async def get_save_slots(
    session: GameSession = Depends(get_session)
) -> ApiResponse:
    """
    Get list of all save slots
    
    Returns: Array of save slot information
    """
    try:
        save_manager = SaveManager()
        slots = save_manager.get_save_slots()
        
        slot_data = []
        for slot in slots:
            try:
                slot_data.append({
                    "slot_id": getattr(slot, 'slot_id', str(slot)),
                    "save_name": getattr(slot, 'save_name', 'Unknown'),
                    "player_name": getattr(slot, 'player_name', 'Unknown'),
                    "timestamp": getattr(slot, 'timestamp', ''),
                    "day": getattr(slot, 'day', 0),
                    "phase": getattr(slot, 'phase', 'unknown'),
                })
            except Exception as slot_err:
                # Skip problematic slots
                continue
        
        return ApiResponse(
            success=True,
            message=f"{len(slot_data)} save slot(s) found",
            data={"save_slots": slot_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/game/save/{slot_id}")
async def delete_save(slot_id: str) -> ApiResponse:
    """
    Delete a save slot
    
    Returns: Confirmation
    """
    try:
        save_manager = SaveManager()
        success, message = save_manager.delete_save(slot_id)
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        return ApiResponse(
            success=True,
            message=message,
            data={"deleted_slot": slot_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Status Endpoints ====================


@app.get("/api/game/{session_id}/status")
async def get_game_status(
    session: GameSession = Depends(get_session)
) -> ApiResponse:
    """
    Get detailed status of a game session
    
    Returns: Session metadata and game progress
    """
    try:
        orchestrator_status = session.orchestrator.get_status()
        
        return ApiResponse(
            success=True,
            message="Status retrieved",
            data={
                "session": {
                    "session_id": session.session_id,
                    "player_name": session.player_name,
                    "created_at": session.created_at,
                    "last_action_at": session.last_action_at,
                    "action_count": session.action_count,
                },
                "game": orchestrator_status,
                "save_slots": len(SaveManager().get_save_slots()),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions() -> ApiResponse:
    """
    List all active sessions
    
    Returns: Array of session information
    """
    try:
        session_ids = session_store.list_sessions()
        sessions_info = []
        
        for sid in session_ids:
            sess = session_store.get_session(sid)
            if sess:
                sessions_info.append({
                    "session_id": sid,
                    "player_name": sess.player_name,
                    "created_at": sess.created_at,
                    "action_count": sess.action_count,
                })
        
        return ApiResponse(
            success=True,
            message=f"{len(sessions_info)} active session(s)",
            data={"sessions": sessions_info}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Root Endpoints ====================


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API documentation link"""
    return {
        "title": "Velinor Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
