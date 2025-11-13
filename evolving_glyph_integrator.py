"""Compatibility shim for evolving_glyph_integrator imports.

Re-exports the implementation from `scripts/utilities` so legacy imports in
tests and examples continue to work.
"""
try:
    from scripts.utilities.evolving_glyph_integrator import EvolvingGlyphIntegrator  # type: ignore
except Exception:
    EvolvingGlyphIntegrator = None

__all__ = ["EvolvingGlyphIntegrator"]
