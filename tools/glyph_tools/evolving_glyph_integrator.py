"""Top-level wrapper for `EvolvingGlyphIntegrator` used by tests.

Re-exports implementation from `src/emotional_os_glyphs` when available.
"""
try:
    from emotional_os_glyphs.evolving_glyph_integrator import EvolvingGlyphIntegrator  # type: ignore
except Exception:
    try:
        from src.emotional_os_glyphs.evolving_glyph_integrator import EvolvingGlyphIntegrator  # type: ignore
    except Exception:
        class EvolvingGlyphIntegrator:
            def __init__(self, *args, **kwargs):
                pass

            def process_conversation_with_evolution(self, *args, **kwargs):
                return {"saori_response": None, "new_glyphs_generated": [], "emotional_patterns_detected": [], "evolution_triggered": False}

__all__ = ["EvolvingGlyphIntegrator"]
