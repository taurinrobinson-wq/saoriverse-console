"""Velinor Game Engine - Core

Main orchestration layer for the Velinor game.
Manages game state, world state, player actions, and NPC interactions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import uuid
from datetime import datetime


class GameState(Enum):
    """Global game states."""
    MENU = "menu"
    LOADING = "loading"
    IN_GAME = "in_game"
    DIALOGUE = "dialogue"
    CHOICE = "choice"
    TRANSITION = "transition"
    GAME_OVER = "game_over"


class Location(Enum):
    """Game locations/environments."""
    MARKET_DISTRICT = "market_district"
    ARCHIVE_CAVES = "archive_caves"
    MILITARY_BASE = "military_base"
    HOSPITAL = "hospital"
    BRIDGE = "bridge"
    UPPER_DISTRICT = "upper_district"


@dataclass
class PlayerStats:
    """Player character stats and attributes."""
    name: str
    courage: float = 0.5  # 0-1 scale
    wisdom: float = 0.5
    empathy: float = 0.5
    resolve: float = 0.5
    
    # Emotional resonance (how attuned player is to glyph system)
    resonance: float = 0.0
    
    # Inventory of collected glyphs/artifacts
    glyphs_collected: List[str] = field(default_factory=list)
    
    # Cumulative choices affecting story
    choices_made: Dict[str, str] = field(default_factory=dict)


@dataclass
class GameAction:
    """Represents a player action or NPC event."""
    action_id: str
    actor: str  # "player" or NPC name
    action_type: str  # "dialogue", "choice", "roll", "move"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    result: Optional[str] = None
    emotional_tone: Optional[str] = None  # glyph/affect info


@dataclass
class NPCState:
    """State of an individual NPC."""
    name: str
    personality: str  # "Archivist", "Guard", "Healer", "Merchant", etc.
    current_location: Location
    relationship: float = 0.5  # -1 to 1, affects dialogue
    dialogue_history: List[str] = field(default_factory=list)
    active: bool = True


@dataclass
class GameSession:
    """Represents a complete game session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    player: PlayerStats = field(default_factory=lambda: PlayerStats(name="Wanderer"))
    npcs: Dict[str, NPCState] = field(default_factory=dict)
    
    # Game flow
    current_state: GameState = GameState.MENU
    current_location: Location = Location.MARKET_DISTRICT
    
    # Action history
    action_history: List[GameAction] = field(default_factory=list)
    
    # Story progress
    story_progress: Dict[str, bool] = field(default_factory=dict)  # story beat -> completed
    
    # Multiplayer
    is_multiplayer: bool = False
    other_players: List[str] = field(default_factory=list)
    
    # Session metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_action_at: str = field(default_factory=lambda: datetime.now().isoformat())


class VelinorEngine:
    """Main game engine orchestrator."""
    
    def __init__(self):
        """Initialize the game engine."""
        self.session: Optional[GameSession] = None
        self.callbacks: Dict[str, List[Callable]] = {
            "on_state_change": [],
            "on_action": [],
            "on_location_change": [],
            "on_dialogue": [],
        }
    
    def create_session(self, player_name: str = "Wanderer", multiplayer: bool = False) -> GameSession:
        """Create a new game session."""
        self.session = GameSession(
            player=PlayerStats(name=player_name),
            is_multiplayer=multiplayer
        )
        self._emit("on_state_change", GameState.LOADING, GameState.IN_GAME)
        return self.session
    
    def get_session(self) -> Optional[GameSession]:
        """Get current session."""
        return self.session
    
    def set_game_state(self, new_state: GameState) -> None:
        """Change game state."""
        if self.session:
            old_state = self.session.current_state
            self.session.current_state = new_state
            self._emit("on_state_change", old_state, new_state)
    
    def move_to_location(self, location: Location) -> None:
        """Move player to a new location."""
        if self.session:
            old_location = self.session.current_location
            self.session.current_location = location
            self._emit("on_location_change", old_location, location)
    
    def perform_action(self, action_type: str, content: str, emotional_tone: Optional[str] = None) -> GameAction:
        """Record a player action."""
        if not self.session:
            raise RuntimeError("No active session")
        
        action = GameAction(
            action_id=str(uuid.uuid4()),
            actor="player",
            action_type=action_type,
            content=content,
            emotional_tone=emotional_tone
        )
        
        self.session.action_history.append(action)
        self.session.last_action_at = datetime.now().isoformat()
        self._emit("on_action", action)
        
        return action
    
    def record_npc_dialogue(self, npc_name: str, dialogue: str) -> GameAction:
        """Record NPC dialogue."""
        if not self.session:
            raise RuntimeError("No active session")
        
        action = GameAction(
            action_id=str(uuid.uuid4()),
            actor=npc_name,
            action_type="dialogue",
            content=dialogue
        )
        
        # Update NPC state
        if npc_name in self.session.npcs:
            self.session.npcs[npc_name].dialogue_history.append(dialogue)
        
        self.session.action_history.append(action)
        self._emit("on_dialogue", npc_name, dialogue)
        
        return action
    
    def add_listener(self, event: str, callback: Callable) -> None:
        """Register event listener."""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to all listeners."""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in callback for {event}: {e}")
    
    def get_action_history(self, limit: int = 10) -> List[GameAction]:
        """Get recent action history."""
        if not self.session:
            return []
        return self.session.action_history[-limit:]
    
    def get_player_stats(self) -> Optional[PlayerStats]:
        """Get current player stats."""
        if self.session:
            return self.session.player
        return None
    
    def update_stat(self, stat_name: str, delta: float) -> None:
        """Update a player stat (add/subtract)."""
        if not self.session:
            raise RuntimeError("No active session")
        
        player = self.session.player
        if hasattr(player, stat_name):
            current = getattr(player, stat_name)
            # Clamp to 0-1 range for normalized stats
            if isinstance(current, float) and 0 <= current <= 1:
                setattr(player, stat_name, max(0, min(1, current + delta)))
            else:
                setattr(player, stat_name, current + delta)
    
    def roll_dice(self, sides: int = 20, modifier: float = 0.0) -> int:
        """Roll dice with optional modifier based on player stats."""
        import random
        roll = random.randint(1, sides)
        
        # Apply modifier based on resolve stat
        if self.session:
            resolve_bonus = int(self.session.player.resolve * 5)
            roll += resolve_bonus
        
        return max(1, roll + int(modifier))
    
    def mark_story_beat(self, beat_name: str) -> None:
        """Mark a story beat as completed."""
        if self.session:
            self.session.story_progress[beat_name] = True
    
    def get_story_progress(self) -> Dict[str, bool]:
        """Get story progress status."""
        if self.session:
            return self.session.story_progress
        return {}
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """End the current session and return summary."""
        if not self.session:
            return None
        
        summary = {
            "session_id": self.session.session_id,
            "player_name": self.session.player.name,
            "final_location": self.session.current_location.value,
            "actions_taken": len(self.session.action_history),
            "story_progress": self.session.story_progress,
            "final_stats": {
                "courage": self.session.player.courage,
                "wisdom": self.session.player.wisdom,
                "empathy": self.session.player.empathy,
                "resolve": self.session.player.resolve,
                "resonance": self.session.player.resonance,
            }
        }
        
        self.session = None
        self.set_game_state(GameState.GAME_OVER)
        
        return summary
