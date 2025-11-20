"""Compatibility shim for tests and legacy imports.

Some tests and modules import `GlyphGenerator` from the top-level
`glyph_generator` module. The canonical implementation lives in
`emotional_os.glyphs.glyph_generator`. Re-export the class here to
avoid NameError regressions and preserve backward compatibility.
"""

from emotional_os.glyphs.glyph_generator import GlyphGenerator  # noqa: F401

__all__ = ["GlyphGenerator"]
