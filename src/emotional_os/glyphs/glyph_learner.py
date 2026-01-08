"""Bridge module for glyph learner.

Prefer the implementation in `emotional_os_glyphs.glyph_learner` when
available; fall back to a lightweight stub to allow tests to import.
"""
try:
    from emotional_os_glyphs.glyph_learner import *  # noqa: F401,F403
except Exception:
    # Minimal stub implementation
    class GlyphLearner:
        @staticmethod
        def _hash_user(user_id: str) -> str:
            return f"stub-{user_id}"

        def analyze_input_for_glyph_generation(self, input_text: str, signals: list, user_hash: str):
            return {
                "glyph_name": "stub_glyph",
                "confidence_score": 0.5,
                "description": "A stub glyph",
                "emotional_signal": "λ",
                "gates": [],
            }

        def log_glyph_candidate(self, candidate: dict) -> bool:
            return True

        def __init__(self, *a, **kw):
            pass

__all__ = ["GlyphLearner"]
