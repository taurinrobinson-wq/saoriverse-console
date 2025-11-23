"""Compatibility shim for legacy imports in tests.

Some integration tests import `evolving_glyph_integrator` from the
top-level module. The canonical implementation lives in
`emotional_os.glyphs.evolving_glyph_integrator`. Re-export the
primary symbol here to avoid ImportError in tests.
"""

from emotional_os.glyphs.evolving_glyph_integrator import EvolvingGlyphIntegrator  # noqa: F401

__all__ = ["EvolvingGlyphIntegrator"]
