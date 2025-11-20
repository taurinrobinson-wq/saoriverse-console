"""Backward compatibility shim.

This module re-exports the canonical implementations from
`emotional_os.core.signal_parser` while also restoring a few
internal helpers and a backward-compatible wrapper for
`select_best_glyph_and_response` that older callers/tests expect.
"""

from emotional_os.core.signal_parser import *  # noqa: F401, F403

# Explicitly import some underscore-prefixed helpers which are intentionally
# private in the core implementation but were referenced by older callers
# via `emotional_os.glyphs.signal_parser`.
from emotional_os.core.signal_parser import (
    _looks_like_artifact,
    _normalize_display_name,
    select_best_glyph_and_response as _core_select_best_glyph_and_response,
)


def select_best_glyph_and_response(glyphs, signals, input_text="", conversation_context=None):
    """Compatibility wrapper around core.select_best_glyph_and_response.

    The canonical implementation returns a 4-tuple:
            (best_glyph, (response_text, feedback_data), response_source, glyphs_selected)

    Older tests and callers expect a 3-tuple and will unpack only
    (best_glyph, (response_text, feedback_data), response_source).

    This wrapper calls the core function and returns the first three
    elements for backward compatibility.
    """
    result = _core_select_best_glyph_and_response(
        glyphs, signals, input_text=input_text, conversation_context=conversation_context
    )
    # If core returns 4 items, drop the fourth for compatibility.
    if isinstance(result, tuple) and len(result) == 4:
        return result[0], result[1], result[2]
    return result


# Re-export underscored helpers at module level so legacy imports work.
__all__ = [
    *[n for n in dir() if not n.startswith("__")],
    '_looks_like_artifact',
    '_normalize_display_name',
    'select_best_glyph_and_response',
]
