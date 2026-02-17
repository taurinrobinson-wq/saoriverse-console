#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.glyph_synthesizer`."""
try:
    from emotional_os_learning.glyph_synthesizer import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.glyph_synthesizer; ensure src/emotional_os_learning is present"
    ) from exc
