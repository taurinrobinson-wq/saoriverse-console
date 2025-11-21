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

    Some older callers/tests expect a 3-tuple while newer callers expect 4.
    To be maximally compatible, this wrapper will ensure a 4-tuple is
    always returned. If the core implementation returns only three items,
    the wrapper will append an empty list for `glyphs_selected`.
    """
    result = _core_select_best_glyph_and_response(
        glyphs, signals, input_text=input_text, conversation_context=conversation_context
    )
    # Normalize result into a 4-tuple for callers that expect the full shape.
    if isinstance(result, tuple):
        if len(result) == 4:
            return result
        if len(result) == 3:
            # Append an empty selected list when core returned only three items
            return result[0], result[1], result[2], []
    # Fallback: not a tuple (unexpected) — wrap into expected shape
    return result, (None, {}), 'fallback_compat', []


# Re-export underscored helpers at module level so legacy imports work.
__all__ = [
    *[n for n in dir() if not n.startswith("__")],
    '_looks_like_artifact',
    '_normalize_display_name',
    'select_best_glyph_and_response',
]
