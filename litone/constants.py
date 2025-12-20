"""
Constants for LiToneCheck Tone Analysis.

Emotional signals, tone mappings, and configuration for legal correspondence
tone analysis and transformation.
"""

# Legal Tone Signals (7 core dimensions for correspondence)
LEGAL_SIGNALS = {
    "α": "Formality/Professional",      # formal, professional, authoritative
    "β": "Boundary/Protective",         # protective, guarding interests, firm
    "γ": "Longing/Understanding",       # seeking understanding, empathetic
    "θ": "Concern/Cautionary",          # concern, caution, warning
    "λ": "Confidence/Assertiveness",    # confident, assertive, clear
    "ε": "Clarity/Reasoning",           # clear reasoning, logical, structured
    "Ω": "Recognition/Acknowledgment",  # recognizing perspective, acknowledging
}

SIGNAL_LIST = list(LEGAL_SIGNALS.keys())

# Tone names mapping
TONE_NAMES = {
    0: "Very Formal",
    1: "Formal",
    2: "Neutral",
    3: "Friendly",
    4: "Empathetic",
}

TONE_EMOJIS = {
    0: "📋",
    1: "📝",
    2: "➖",
    3: "😊",
    4: "🤝",
}

# NRC lexicon for advanced emotion detection
NRC_EMOTIONS = [
    "anger",
    "anticipation",
    "disgust",
    "fear",
    "joy",
    "negative",
    "positive",
    "sadness",
    "surprise",
    "trust",
]

# Signal to tone category mapping
SIGNAL_MAPPING = {
    "formal_markers": "α",           # Formality markers
    "boundary_words": "β",           # Boundary/protective language
    "empathy_words": "γ",            # Understanding/empathy
    "concern_words": "θ",            # Concern/cautionary
    "confidence_words": "λ",         # Assertiveness/confidence
    "reasoning_words": "ε",          # Clarity/logical reasoning
    "recognition_words": "Ω",        # Recognition/acknowledgment
}

# Fuzzy matching defaults
FUZZY_MATCH_THRESHOLD = 0.6
FUZZY_MATCH_TOKEN_THRESHOLD = 0.8

# Learning configuration
MIN_EFFECTIVENESS_THRESHOLD = 0.7
RESPONSE_EFFECTIVENESS_BASE_SCORE = 0.5

# Legal-specific pattern extraction
LEGAL_PATTERNS = {
    "formal_language": [
        r"hereby|hereinafter|furthermore|moreover|notwithstanding",
        r"pursuant to|in accordance with|subject to",
        r"shall|may|must|shall not",
    ],
    "boundary_language": [
        r"protect|guard|boundary|shield|preserve|defend",
        r"maintain|reserve|safeguard|ensure",
    ],
    "empathy_language": [
        r"understand|appreciate|recognize|acknowledge|see",
        r"compassion|consideration|concern|care",
    ],
    "concern_language": [
        r"concern|caution|warning|alert|beware",
        r"risk|danger|issue|problem|challenge",
    ],
    "confidence_language": [
        r"confident|certain|clear|decisive|assertive",
        r"will|must|should|definitely|absolutely",
    ],
    "reasoning_language": [
        r"therefore|thus|hence|consequently|as a result",
        r"because|since|reason|logic|evidence",
    ],
}

# Sentence structure markers
SENTENCE_STRUCTURE_MARKERS = {
    "Introduction": [
        r"^(regarding|concerning|re:|subject:|with respect to|in reference to)",
        r"^(i am writing|this letter|please find)",
    ],
    "Conclusion": [
        r"(in conclusion|in summary|to summarize|finally|as noted|in short)",
        r"(we look forward|we appreciate|thank you|sincerely|respectfully)",
    ],
    "Reasoning": [
        r"(therefore|thus|hence|consequently|as a result|for this reason)",
        r"(because|since|as|inasmuch as|in that)",
    ],
    "Supporting": [
        r"(for example|such as|including|specifically|in particular|notably)",
        r"(evidence|research|data|shows|indicates|demonstrates)",
    ],
}

# Message assessment markers
MESSAGE_ASSESSMENT_MARKERS = {
    "Persuasive": [
        r"(should|consider|recommend|suggest|would benefit)",
        r"(compelling|important|significant|critical|essential)",
    ],
    "Argumentative": [
        r"(however|contrary|on the other hand|conversely|despite)",
        r"(disagree|dispute|challenge|contest|object)",
    ],
    "Aggressive": [
        r"(must|demand|require|insist|will not)",
        r"(unacceptable|outrageous|violation|breach|failure)",
    ],
    "Professional": [
        r"(professional|respectfully|with regard|accordingly)",
        r"(hereby|therefore|shall|pursuant)",
    ],
    "Neutral": [
        r"(stated|noted|indicated|mentioned|observed)",
        r"(information|details|fact|accordingly)",
    ],
    "Friendly": [
        r"(appreciate|thank|look forward|glad|happy|pleased)",
        r"(warmly|sincerely|best regards|hope)",
    ],
    "Empathetic": [
        r"(understand|appreciate your|recognize|acknowledge)",
        r"(compassion|care|support|help|together)",
    ],
}

# Common stop words to filter in analysis
STOP_WORDS = {
    "i", "me", "my", "am", "is", "the", "a", "an", "and", "or", "but",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "that",
    "this", "it", "be", "have", "has", "do", "does", "will", "would",
    "could", "should", "can", "may", "might", "must", "shall",
}

# Empathy marker words
EMPATHY_WORDS = [
    "feel", "understand", "see", "hear", "witness", "acknowledge",
    "appreciate", "recognize", "care", "support", "compassion",
]

# Reflection marker words
REFLECTION_WORDS = [
    "seems", "sounds like", "appears", "suggests", "indicates",
    "reflects", "portrays", "demonstrates",
]
