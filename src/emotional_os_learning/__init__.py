#!/usr/bin/env python3
"""
Dynamic Conversation Learning Module

Enables the system to learn and evolve from lived conversations.

Three-layer architecture:
1. Archetype Library: Stores learned conversation patterns
2. Response Generator: Applies archetypes to generate fresh responses
3. Learner: Extracts patterns from successful conversations

Workflow:
- Playwright (user) writes dialogue scenes
- Organizer (AI) extracts rules into archetype patterns
- System uses archetypes to respond dynamically
- Each conversation refines the archetype library
- Over time, system evolves to handle increasingly complex emotional arcs
"""

from .conversation_archetype import (
    ConversationArchetype,
    ArchetypeLibrary,
    get_archetype_library,
)
from .archetype_response_generator import (
    ArchetypeResponseGenerator,
    get_archetype_response_generator,
)
from .conversation_learner import (
    ConversationLearner,
    get_conversation_learner,
)

__all__ = [
    "ConversationArchetype",
    "ArchetypeLibrary",
    "get_archetype_library",
    "ArchetypeResponseGenerator",
    "get_archetype_response_generator",
    "ConversationLearner",
    "get_conversation_learner",
]
