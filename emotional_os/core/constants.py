"""
Constants and defaults for Emotional OS.

Centralized definitions for signals, gates, and configuration.
"""

# Emotional Signals (7 core dimensions)
SIGNALS = {
    'α': 'Devotion/Sacred',      # vow, sacred, devoted, honor
    'β': 'Boundary/Contain',      # protect, guard, boundary, shield
    'γ': 'Longing/Ache',          # yearn, ache, crave, long for
    'θ': 'Grief/Mourning',        # loss, grief, mourn, sorrow
    'λ': 'Joy/Delight',           # joy, delight, happy, bliss
    'ε': 'Insight/Clarity',       # clarity, understand, insight, knowing
    'Ω': 'Recognition/Witnessing' # seen, witnessed, recognized, heard
}

SIGNAL_LIST = list(SIGNALS.keys())

# ECM Gate Mappings
ECM_GATES = {
    "Gate 2": ["β"],                    # Boundary
    "Gate 4": ["γ", "θ"],              # Longing + Grief
    "Gate 5": ["λ", "ε", "δ"],         # Joy + Insight
    "Gate 6": ["α", "Ω", "ε"],         # Devotion + Recognition + Insight
    "Gate 9": ["α", "β", "γ", "δ", "ε", "Ω"],  # All (except grief)
    "Gate 10": ["θ"]                   # Grief
}

# Signal to emotion category mapping for learner
SIGNAL_MAPPING = {
    'negative_emotions': 'θ',  # grief, mourning
    'longing_words': 'γ',      # ache, yearning
    'joy_words': 'λ',          # joy, delight
    'protection_words': 'β',   # boundary, contain
    'recognition_words': 'Ω',  # seen, witnessed
    'devotion_words': 'α',     # vow, sacred
    'insight_words': 'ε'       # clarity, understanding
}

# Default paths (can be overridden)
DEFAULT_LEXICON_BASE = "parser/signal_lexicon.json"
DEFAULT_LEARNED_LEXICON = "parser/learned_lexicon.json"
DEFAULT_PATTERN_HISTORY = "learning/pattern_history.json"
DEFAULT_GLYPH_DB = "glyphs.db"

# NRC lexicon for advanced emotion detection
NRC_EMOTIONS = [
    'anger', 'anticipation', 'disgust', 'fear',
    'joy', 'negative', 'positive', 'sadness',
    'surprise', 'trust'
]

# Fuzzy matching defaults
FUZZY_MATCH_THRESHOLD = 0.6
FUZZY_MATCH_TOKEN_THRESHOLD = 0.8

# Learning configuration
MIN_EFFECTIVENESS_THRESHOLD = 0.7
RESPONSE_EFFECTIVENESS_BASE_SCORE = 0.5

# Pattern extraction regex templates
EMOTIONAL_PATTERNS = {
    'feeling_expressions': [
        r'i feel (\w+)',
        r'feeling (\w+)',
        r'i\'m (\w+)',
        r'makes me (\w+)',
        r'i\'m experiencing (\w+)'
    ],
    'intensity_modifiers': [
        r'very (\w+)',
        r'extremely (\w+)',
        r'deeply (\w+)',
        r'slightly (\w+)',
        r'intensely (\w+)'
    ],
    'emotional_metaphors': [
        r'like a (\w+)',
        r'feels like (\w+)',
        r'reminds me of (\w+)',
        r'similar to (\w+)'
    ]
}

# Theme keywords for theme identification
THEME_KEYWORDS = {
    'grief': ['loss', 'death', 'gone', 'miss', 'grief', 'mourn', 'funeral', 'died'],
    'anxiety': ['worry', 'anxious', 'nervous', 'panic', 'stress', 'overwhelm'],
    'joy': ['happy', 'joy', 'celebrate', 'excited', 'wonderful', 'amazing'],
    'love': ['love', 'adore', 'cherish', 'affection', 'care', 'devoted'],
    'longing': ['want', 'need', 'desire', 'wish', 'yearn', 'crave', 'ache'],
    'anger': ['angry', 'mad', 'furious', 'rage', 'irritated', 'frustrated'],
    'confusion': ['confused', 'unclear', 'lost', 'uncertain', 'puzzle', 'wonder']
}

# Common stop words to filter in word associations
STOP_WORDS = {
    'i', 'me', 'my', 'am', 'is', 'the', 'a', 'an', 'and', 'or', 'but',
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'that',
    'this', 'it', 'be', 'have', 'has', 'do', 'does', 'will', 'would',
    'could', 'should', 'can', 'may', 'might', 'must', 'shall'
}

# Empathy marker words
EMPATHY_WORDS = ['feel', 'understand', 'see', 'hear', 'witness', 'acknowledge']

# Reflection marker words
REFLECTION_WORDS = ['seems', 'sounds like', 'appears', 'suggests', 'indicates']
