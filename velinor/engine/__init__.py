"""Velinor engine package."""

__all__ = ["resonance"]
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

from velinor.story.story_builder import StoryBuilder
from velinor.story.story_loader import StoryLoader, StoryPassage
from velinor.story.story_session import StorySession, DialogueChoice

from .scene_manager import (
    SceneModule,
    SceneRenderer,
    SceneBuilder,
    SceneState,
    SceneAssets,
    DialogueOption,
    get_scene_renderer,
    get_current_scene,
    set_current_scene,
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
    # Story System
    "StoryBuilder",
    "StoryLoader",
    "StorySession",
    "StoryPassage",
    "DialogueChoice",
    # Orchestrator
    "VelinorTwineOrchestrator",
]
