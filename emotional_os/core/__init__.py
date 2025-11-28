"""Lightweight core package shim for tests.

This file intentionally keeps imports minimal and provides small stubs
for larger components that are not required by unit tests in this
environment. It exposes the commonly-used names so other modules can
`from emotional_os.core import ...` without failing during import.
"""

from emotional_os.core.paths import (
    PathManager,
    get_path_manager,
    reset_path_manager,
    signal_lexicon_path,
    learned_lexicon_path,
    pattern_history_path,
    glyph_db_path,
    poetry_data_dir_path,
)

from emotional_os.core.constants import *  # re-export constants

from emotional_os.core.signal_parser import (
    parse_input,
    load_signal_map,
    parse_signals,
    evaluate_gates,
    fetch_glyphs,
    fuzzy_match,
    fuzzy_contains,
    generate_voltage_response,
    generate_contextual_response,
    generate_simple_prompt,
)

from emotional_os.core.lexicon_learner import (
    LexiconLearner,
    learn_from_conversation_data,
    get_enhanced_lexicon,
    get_learning_insights,
)

# === Minimal presence architecture stubs ===


class AttunementLoop:
    def __init__(self, *args, **kwargs):
        pass


class EmotionalReciprocity:
    def __init__(self, *args, **kwargs):
        pass


class TemporalMemory:
    def __init__(self, *args, **kwargs):
        pass


class EmbodiedSimulation:
    def __init__(self, *args, **kwargs):
        pass


class PoeticConsciousness:
    def __init__(self, *args, **kwargs):
        pass


"""Lightweight core package shim for tests.

This file intentionally keeps imports minimal and provides small stubs
for larger components that are not required by unit tests in this
environment. It exposes the commonly-used names so other modules can
`from emotional_os.core import ...` without failing during import.
"""


# === Minimal presence architecture stubs ===

class AttunementLoop:
    def __init__(self, *args, **kwargs):
        pass


class EmotionalReciprocity:
    def __init__(self, *args, **kwargs):
        pass


class TemporalMemory:
    def __init__(self, *args, **kwargs):
        pass


class EmbodiedSimulation:
    def __init__(self, *args, **kwargs):
        pass


class PoeticConsciousness:
    def __init__(self, *args, **kwargs):
        pass

# === Minimal generative tension stubs ===


class GenerativeTension:
    pass


class SurpriseEngine:
    pass


class ChallengeEngine:
    pass


class SubversionEngine:
    pass


class CreationEngine:
    pass

# === Minimal Saori layer stubs ===


class SaoriLayer:
    pass


class MirrorEngine:
    pass


class EdgeGenerator:
    pass


class EmotionalGenome:
    pass


class MortalityClock:
    pass


class Archetype:
    pass


class EmotionalFramework:
    def __init__(self):
        pass


__version__ = "0.0.0-test-shim"

__all__ = [
    # Path management
    "PathManager",
    "get_path_manager",
    "reset_path_manager",
    "signal_lexicon_path",
    "learned_lexicon_path",
    "pattern_history_path",
    "glyph_db_path",
    "poetry_data_dir_path",
    # Signal parser
    "parse_input",
    "load_signal_map",
    "parse_signals",
    "evaluate_gates",
    "fetch_glyphs",
    "fuzzy_match",
    "fuzzy_contains",
    "generate_voltage_response",
    "generate_contextual_response",
    "generate_simple_prompt",
    # Lexicon
    "LexiconLearner",
    "learn_from_conversation_data",
    "get_enhanced_lexicon",
    "get_learning_insights",
    # Presence stubs
    "AttunementLoop",
    "EmotionalReciprocity",
    "TemporalMemory",
    "EmbodiedSimulation",
    "PoeticConsciousness",
    # Tension stubs
    "GenerativeTension",
    "SurpriseEngine",
    "ChallengeEngine",
    "SubversionEngine",
    "CreationEngine",
    # Saori layer stubs
    "SaoriLayer",
    "MirrorEngine",
    "EdgeGenerator",
    "EmotionalGenome",
    "MortalityClock",
    "Archetype",
    # Framework
    "EmotionalFramework",
]
