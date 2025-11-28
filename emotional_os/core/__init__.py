"""
Emotional OS Core - Canonical implementation of all core modules.

This is the single source of truth for:
- Signal parsing and glyph matching
- Lexicon learning and pattern extraction
- Path management and configuration
- Constants and defaults

All other modules should import from here.
"""

# Path management
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

# Constants
from emotional_os.core.constants import (
    SIGNALS,
    SIGNAL_LIST,
    ECM_GATES,
    SIGNAL_MAPPING,
    DEFAULT_LEXICON_BASE,
    DEFAULT_LEARNED_LEXICON,
    DEFAULT_PATTERN_HISTORY,
    DEFAULT_GLYPH_DB,
    NRC_EMOTIONS,
    FUZZY_MATCH_THRESHOLD,
    FUZZY_MATCH_TOKEN_THRESHOLD,
    MIN_EFFECTIVENESS_THRESHOLD,
    RESPONSE_EFFECTIVENESS_BASE_SCORE,
    EMOTIONAL_PATTERNS,
    THEME_KEYWORDS,
    STOP_WORDS,
    EMPATHY_WORDS,
    REFLECTION_WORDS,
)

# Signal parser - the canonical parser
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

# Lexicon learning - the canonical learner
from emotional_os.core.lexicon_learner import (
    LexiconLearner,
    learn_from_conversation_data,
    get_enhanced_lexicon,
    get_learning_insights,
)

# Poetic Emotional Engine
from emotional_os.core.poetic_engine import (
    PoeticEmotionalEngine,
    LivingPoem,
    MetaphorStanza,
    RhythmStanza,
    SyntaxStanza,
    AffectiveMemory,
    RelationalGravity,
    EthicalCompass,
    EmotionalValence,
    RhythmTempo,
    SyntaxClarity,
    RelationalVector,
    get_poetic_engine,
    reset_poetic_engine,
)

__version__ = "2.0.0"
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
    
    # Poetic Emotional Engine
    "PoeticEmotionalEngine",
    "LivingPoem",
    "MetaphorStanza",
    "RhythmStanza",
    "SyntaxStanza",
    "AffectiveMemory",
    "RelationalGravity",
    "EthicalCompass",
    "EmotionalValence",
    "RhythmTempo",
    "SyntaxClarity",
    "RelationalVector",
    "get_poetic_engine",
    "reset_poetic_engine",
]
