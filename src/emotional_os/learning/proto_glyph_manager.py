#!/usr/bin/env python3
"""Bridge to `emotional_os_learning.proto_glyph_manager`."""
try:
    from emotional_os_learning.proto_glyph_manager import *  # noqa: F401,F403
except Exception as exc:
    raise ImportError(
        "Unable to load emotional_os_learning.proto_glyph_manager; ensure src/emotional_os_learning is present"
    ) from exc
