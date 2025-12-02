"""FirstPerson: Relational AI Core Modules

This package contains the modular components that enable FirstPerson to remember,
attune, reflect, scaffold, and relate across conversations.

Phases:
- Phase 1: Core Foundations (story-start, frequency, memory, variation)
- Phase 2: Emotional Attunement (affect, modulation, repair)
- Phase 3: Relational Depth (perspective, choices, temporal tracking)
- Phase 4: Integration & Continuity (resonance, regulation, weaving)
- Phase 5: Advanced Modeling (scaffolding, learning, rituals)

Module Exports:
- StoryStartDetector: Detects ambiguous pronouns and temporal markers
- FrequencyReflector: Detects repeated emotional themes
- SupabaseManager: Manages persistent theme and anchor storage
- MemoryManager: Rehydrates conversation memory on session initialization
- ResponseTemplates: Manages clarifier and reflection templates with variation
"""

from .story_start_detector import (
    StoryStartDetector,
    analyze_story_start,
    generate_clarifying_prompt,
)

from .frequency_reflector import (
    FrequencyReflector,
    detect_theme,
    analyze_frequency,
    get_frequency_reflection,
)

from .supabase_manager import (
    SupabaseManager,
    ThemeAnchor,
    ThemeHistory,
    TemporalPattern,
)

from .memory_manager import (
    MemoryManager,
    rehydrate_memory,
    format_memory_for_parser,
    get_memory_summary,
)

from .response_templates import (
    ResponseTemplates,
    get_clarifying_prompt,
    add_custom_clarifier,
    add_custom_reflection,
)

from .integration_orchestrator import (
    FirstPersonOrchestrator,
    ConversationTurn,
    IntegrationResponse,
    create_orchestrator,
)

from .affect_parser import (
    AffectParser,
    AffectAnalysis,
    create_affect_parser,
)

from .response_rotator import (
    ResponseRotator,
    GLYPH_RESPONSE_BANK,
    create_response_rotator,
)

__all__ = [
    # Story-Start Detection (Phase 1.1)
    "StoryStartDetector",
    "analyze_story_start",
    "generate_clarifying_prompt",
    # Frequency Reflection (Phase 1.2)
    "FrequencyReflector",
    "detect_theme",
    "analyze_frequency",
    "get_frequency_reflection",
    # Supabase Management (Phase 1.3)
    "SupabaseManager",
    "ThemeAnchor",
    "ThemeHistory",
    "TemporalPattern",
    # Memory Rehydration (Phase 1.4)
    "MemoryManager",
    "rehydrate_memory",
    "format_memory_for_parser",
    "get_memory_summary",
    # Response Templates (Phase 1.5)
    "ResponseTemplates",
    "get_clarifying_prompt",
    "add_custom_clarifier",
    "add_custom_reflection",
    # Integration Orchestrator (Phase 1.6)
    "FirstPersonOrchestrator",
    "ConversationTurn",
    "IntegrationResponse",
    "create_orchestrator",
    # Affect Parser (Phase 2.1)
    "AffectParser",
    "AffectAnalysis",
    "create_affect_parser",
    # Response Rotator (Phase 2.2)
    "ResponseRotator",
    "GLYPH_RESPONSE_BANK",
    "create_response_rotator",
]
