"""Shim for `emotional_os.glyphs.antonym_glyphs`.

Prefer the implementation under `src/emotional_os_glyphs/antonym_glyphs.py`.
Provide minimal fallbacks if the full module cannot be imported.
"""
try:
    from emotional_os_glyphs.antonym_glyphs import *  # noqa: F401,F403
except Exception:
    # Minimal stubs to avoid import errors during test collection.
    def get_all_antonym_glyphs():
        return []

    def find_antonym_glyph(name):
        return None

    __all__ = ["get_all_antonym_glyphs", "find_antonym_glyph"]
