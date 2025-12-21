"""Compatibility wrapper exposing `GlyphGenerator` at top-level for tests.

This module re-exports the implementation from `src/emotional_os_glyphs` so
legacy tests that import `glyph_generator` continue to work.
"""
try:
    from emotional_os_glyphs.glyph_generator import GlyphGenerator, NewGlyph, EmotionalPattern  # type: ignore
except Exception:
    try:
        from src.emotional_os_glyphs.glyph_generator import GlyphGenerator, NewGlyph, EmotionalPattern  # type: ignore
    except Exception:
        # Provide a minimal fallback so tests won't crash during import;
        # functional tests that require full generator will still fail.
        class GlyphGenerator:
            def __init__(self, *args, **kwargs):
                pass

            def detect_new_emotional_patterns(self, *args, **kwargs):
                return []

            def process_conversation_for_glyphs(self, *args, **kwargs):
                return []

        class EmotionalPattern:
            def __init__(self, *args, **kwargs):
                self.emotions = []
                self.intensity = 0.0
                self.context_words = []
                self.frequency = 0
                self.first_seen = None
                self.last_seen = None

        class NewGlyph:
            def __init__(self, *args, **kwargs):
                self.tag_name = ""
                self.glyph_symbol = ""

__all__ = ["GlyphGenerator", "NewGlyph", "EmotionalPattern"]
