"""Compatibility helpers for return-shape normalization and small shims.

These functions centralize cross-version compatibility logic so callers
can rely on a stable shape regardless of upstream changes.
"""
from typing import Tuple, Any


def ensure_tuple_shape(result: Any) -> Tuple:
    """Normalize a variety of return shapes into a stable 4-tuple:

    (best_glyph, (response_text, feedback_data), response_source, glyphs_selected)

    If the incoming value is a 3-tuple, an empty list will be appended
    for `glyphs_selected`. If it's None or unexpected, a safe fallback
    tuple is returned.
    """
    # If result is already a 4-tuple, return as-is
    try:
        if isinstance(result, tuple):
            if len(result) == 4:
                return result
            if len(result) == 3:
                return result[0], result[1], result[2], []
    except Exception:
        pass

    # If it's a mapping-like object (older edge case), try to extract keys
    try:
        best = result.get('best_glyph') if hasattr(result, 'get') else None
        resp = (result.get('voltage_response') if hasattr(
            result, 'get') else None) or None
        feedback = result.get('feedback') if hasattr(result, 'get') else {}
        source = result.get('response_source') if hasattr(
            result, 'get') else 'fallback'
        glyphs = result.get('glyphs') if hasattr(result, 'get') else []
        return best, (resp, feedback), source, glyphs or []
    except Exception:
        pass

    # Last-resort fallback
    return None, (None, {}), 'fallback', []
