"""
Emotional OS Core - Canonical implementation of all core modules.

This is the single source of truth for:
- Signal parsing and glyph matching
- Lexicon learning and pattern extraction
- Path management and configuration
- Constants and defaults
- Presence Architecture (attunement, reciprocity, memory, embodiment, poetic)
- Generative Tension (surprise, challenge, subversion, creation)
- Saori Layer (mirror, edge, genome, mortality)

All other modules should import from here.
"""

# Constants
from emotional_os.core.constants import (
    DEFAULT_GLYPH_DB,
    DEFAULT_LEARNED_LEXICON,
    DEFAULT_LEXICON_BASE,
    DEFAULT_PATTERN_HISTORY,
    ECM_GATES,
    EMOTIONAL_PATTERNS,
    EMPATHY_WORDS,
    FUZZY_MATCH_THRESHOLD,
    FUZZY_MATCH_TOKEN_THRESHOLD,
    MIN_EFFECTIVENESS_THRESHOLD,
    NRC_EMOTIONS,
    REFLECTION_WORDS,
    RESPONSE_EFFECTIVENESS_BASE_SCORE,
    SIGNAL_LIST,
    SIGNAL_MAPPING,
    SIGNALS,
    STOP_WORDS,
    THEME_KEYWORDS,
)

# Lexicon learning - the canonical learner
from emotional_os.core.lexicon_learner import (
    LexiconLearner,
    get_enhanced_lexicon,
    get_learning_insights,
    learn_from_conversation_data,
)

# Path management
from emotional_os.core.paths import (
    PathManager,
    get_path_manager,
    glyph_db_path,
    learned_lexicon_path,
    pattern_history_path,
    poetry_data_dir_path,
    reset_path_manager,
    signal_lexicon_path,
)

# Signal parser - the canonical parser
from emotional_os.core.signal_parser import (
    evaluate_gates,
    fetch_glyphs,
    fuzzy_contains,
    fuzzy_match,
    generate_contextual_response,
    generate_simple_prompt,
    generate_voltage_response,
    load_signal_map,
    parse_input,
    parse_signals,
)

# Presence Architecture - emotional presence components
from emotional_os.core.presence import (
    AttunementLoop,
    EmotionalReciprocity,
    TemporalMemory,
    EmbodiedSimulation,
    PoeticConsciousness,
)

# Generative Tension - dynamic interaction components
from emotional_os.core.tension import (
    GenerativeTension,
    SurpriseEngine,
    ChallengeEngine,
    SubversionEngine,
    CreationEngine,
)

# Saori Layer - advanced emotional framework
from emotional_os.core.saori import (
    SaoriLayer,
    MirrorEngine,
    EdgeGenerator,
    EmotionalGenome,
    MortalityClock,
    Archetype,
)

# Unified Emotional Framework
from emotional_os.core.emotional_framework import EmotionalFramework

__version__ = "2.1.0"
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
    # Constants
    "SIGNALS",
    "SIGNAL_LIST",
    "ECM_GATES",
    "SIGNAL_MAPPING",
    "DEFAULT_LEXICON_BASE",
    "DEFAULT_LEARNED_LEXICON",
    "DEFAULT_PATTERN_HISTORY",
    "DEFAULT_GLYPH_DB",
    "NRC_EMOTIONS",
    "FUZZY_MATCH_THRESHOLD",
    "FUZZY_MATCH_TOKEN_THRESHOLD",
    "MIN_EFFECTIVENESS_THRESHOLD",
    "RESPONSE_EFFECTIVENESS_BASE_SCORE",
    "EMOTIONAL_PATTERNS",
    "THEME_KEYWORDS",
    "STOP_WORDS",
    "EMPATHY_WORDS",
    "REFLECTION_WORDS",
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
    # Lexicon learning
    "LexiconLearner",
    "learn_from_conversation_data",
    "get_enhanced_lexicon",
    "get_learning_insights",
    
    # Presence Architecture
    "AttunementLoop",
    "EmotionalReciprocity",
    "TemporalMemory",
    "EmbodiedSimulation",
    "PoeticConsciousness",
    
    # Generative Tension
    "GenerativeTension",
    "SurpriseEngine",
    "ChallengeEngine",
    "SubversionEngine",
    "CreationEngine",
    
    # Saori Layer
    "SaoriLayer",
    "MirrorEngine",
    "EdgeGenerator",
    "EmotionalGenome",
    "MortalityClock",
    "Archetype",
    
    # Unified Framework
    "EmotionalFramework",
]
