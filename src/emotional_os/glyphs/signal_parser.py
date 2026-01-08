"""Shim exposing the glyph-aware signal parser under
`emotional_os.glyphs.signal_parser`.

Prefer the richer `emotional_os_glyphs.signal_parser` when available;
fall back to `emotional_os.core.signal_parser` if needed.
"""
try:
    from emotional_os_glyphs.signal_parser import *  # noqa: F401,F403
    from emotional_os_glyphs.signal_parser import parse_input  # explicit
except Exception:
    from emotional_os.core.signal_parser import *  # noqa: F401,F403
    from emotional_os.core.signal_parser import parse_input
