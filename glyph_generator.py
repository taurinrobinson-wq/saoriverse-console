"""Top-level compatibility shim for the glyph generator.

Some tests and scripts import `glyph_generator` from the repository root. The
actual implementation lives under `scripts/utilities/`. Re-export the main
symbols here so legacy imports continue to work in CI/test environments.
"""
try:
    from scripts.utilities.glyph_generator import GlyphGenerator, NewGlyph  # type: ignore
except Exception:
    # Tests should handle GlyphGenerator being None if the environment
    # intentionally lacks full dependencies.
    GlyphGenerator = None
    NewGlyph = None

__all__ = ["GlyphGenerator", "NewGlyph"]
