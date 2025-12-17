# Dialogue generation configuration
# Uses deterministic pipeline: NRC lexicon + spaCy + TextBlob
# Python 3.12+ recommended for best NLP library compatibility

PROVIDER = "nrc"  # 'nrc' = deterministic only (no external LLM services)
CACHE_PATH = "velinor/cache/dialogue/"
SAFE_WORDS = ["glyph", "resonance", "ritual"]

# Optional: spaCy and TextBlob are used when available for enhanced sentiment analysis
# If not installed, the system gracefully falls back to simple heuristics
