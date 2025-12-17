"""
Deterministic dialogue generator for REMNANTS-driven NPC lines.
- Provides `generate_line(npc_name, remnants, tone=None)` API
- Uses NRC lexicon, spaCy, and TextBlob for deterministic emotion/sentiment/syntax shaping
- No external LLM services; fully local, fast, and reproducible

Python 3.12+ recommended (better NLP library compatibility).
"""
from typing import Dict, Optional, List
import json
import os

# Load NRC lexicon from data/lexicons/nrc_lexicon_cleaned.json
NRC_LEXICON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "lexicons", "nrc_lexicon_cleaned.json"
)

def _load_nrc_lexicon() -> Dict:
    """Load the NRC emotion lexicon."""
    try:
        with open(NRC_LEXICON_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        print(f"[Warning] Could not load NRC lexicon from {NRC_LEXICON_PATH}: {e}")
        return {"words_by_emotion": {}}

NRC_LEXICON = _load_nrc_lexicon()

# Try optional NLP libs; fall back gracefully if missing
try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except Exception:
    HAS_TEXTBLOB = False

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except Exception:
    nlp = None
    HAS_SPACY = False
# Map REMNANTS traits to NRC emotion categories for word selection
TRAIT_TO_NRC_EMOTION = {
    "trust": "joy",
    "empathy": "joy",
    "resolve": "joy",
    "memory": "joy",
    "nuance": "joy",
    "authority": "anger",
    "need": "sadness",
    "skepticism": "fear"
}


def _dominant_trait(remnants: Dict[str, float]) -> str:
    """Return the trait with highest value in the REMNANTS dict."""
    return max(remnants.items(), key=lambda kv: kv[1])[0]


def _get_nrc_words(emotion: str, limit: int = 3) -> List[str]:
    """Get words from NRC lexicon for a given emotion category."""
    words_by_emotion = NRC_LEXICON.get("words_by_emotion", {})
    return words_by_emotion.get(emotion, [emotion])[:limit]


def _get_sentiment_polarity(trait: str) -> float:
    """
    Compute sentiment polarity for a trait using TextBlob if available.
    Returns float in [-1.0, 1.0].
    """
    if not HAS_TEXTBLOB:
        # Fallback heuristic
        if trait in ("empathy", "trust", "resolve", "memory", "nuance"):
            return 0.5
        elif trait in ("skepticism", "authority"):
            return -0.3
        else:
            return 0.0
    
    try:
        polarity = TextBlob(trait).sentiment.polarity
        return polarity
    except Exception:
        return 0.0


def _build_sentence(npc_name: str, dominant: str, nrc_words: List[str], persona_first_line: Optional[str] = None) -> str:
    """
    Build an in-character sentence using the dominant trait and NRC emotion words.
    """
    word = nrc_words[0] if nrc_words else dominant
    
    # Syntactic templates per trait
    templates = {
        "skepticism": "I question what I hear, {npc}—there is {word} in your words.",
        "empathy": "I feel your {word}, and I want to understand, {npc}.",
        "trust": "I believe in you, {npc}. Your presence brings {word}.",
        "resolve": "I stand firm, {npc}. {word} guides my path.",
        "memory": "The past recalls {word}, {npc}. I remember.",
        "nuance": "There is both {word} and shadow here, {npc}—balance matters.",
        "authority": "Hear me, {npc}: I command with {word}.",
        "need": "I need your help, {npc}. {word} moves me.",
    }
    
    template = templates.get(dominant, "I am moved by {word}, {npc}.")
    sentence = template.format(npc=npc_name, word=word)
    
    # Optionally append persona context
    if persona_first_line:
        sentence = sentence + " " + persona_first_line
    
    return sentence


def _read_persona(npc_name: str) -> Optional[str]:
    """Read persona file for an NPC; return first line or None."""
    path = os.path.join(
        "velinor", "markdowngameinstructions", "llm_templates",
        f"{npc_name.lower().replace(' ', '_')}_persona.md"
    )
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().strip().split('\n')
            # Return first non-empty line
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    return line.strip()
            return None
    except Exception:
        return None


def generate_line(npc_name: str, remnants: Dict[str, float], tone: Optional[str] = None) -> str:
    """
    Generate a deterministic dialogue line for an NPC using REMNANTS traits and NRC lexicon.
    
    Args:
        npc_name: NPC name string (used for persona file lookup)
        remnants: REMNANTS trait dict (keys: trait names, values: floats in [0.0, 1.0])
        tone: Optional explicit tone override (if None, uses dominant trait)
    
    Returns:
        In-character dialogue line string.
    """
    # Determine dominant trait
    dominant = tone if tone else _dominant_trait(remnants)
    
    # Map REMNANTS trait to NRC emotion for word selection
    nrc_emotion = TRAIT_TO_NRC_EMOTION.get(dominant, "joy")
    nrc_words = _get_nrc_words(nrc_emotion, limit=3)
    
    # Read persona context if available
    persona_first_line = _read_persona(npc_name)
    
    # Build and return sentence
    sentence = _build_sentence(npc_name, dominant, nrc_words, persona_first_line)
    
    return sentence
