"""Velinor Engine Package

Core game engine for Velinor: Remnants of the Tone
"""

from .core import (
    VelinorEngine,
    GameSession,
    GameState,
    Location,
    PlayerStats,
    GameAction,
    NPCState,
)

from .npc_system import (
    NPCDialogueSystem,
    NPCRegistry,
    NPC,
    NPCPersonality,
)

from .twine_adapter import (
    TwineGameSession,
    TwineStoryLoader,
    DialogueParser,
    StoryBuilder,
    StoryPassage,
    DialogueChoice,
)

from .orchestrator import VelinorTwineOrchestrator

__all__ = [
    # Core
    "VelinorEngine",
    "GameSession",
    "GameState",
    "Location",
    "PlayerStats",
    "GameAction",
    "NPCState",
    # NPC System
    "NPCDialogueSystem",
    "NPCRegistry",
    "NPC",
    "NPCPersonality",
    # Twine Integration
    "TwineGameSession",
    "TwineStoryLoader",
    "DialogueParser",
    "StoryBuilder",
    "StoryPassage",
    "DialogueChoice",
    # Orchestrator
    "VelinorTwineOrchestrator",
]
