"""Lightweight tone helper for glyphs package.

This module provides a minimal compatibility layer expected by
`dynamic_response_composer`. It intentionally keeps logic small and
pure-Python so imports don't pull heavy NLP packages at module import
time.

Functions:
- update_tone_state(tone_history, new_text) -> dict
- get_clarifier(tone_state) -> str
"""

from typing import Any, Dict, List


def update_tone_state(tone_history: List[str], new_text: str) -> Dict[str, Any]:
    """Update a minimal tone state from rolling history + new input.

    This is intentionally simple: keep the last N utterances and a
    lightweight summary (length, last_words). Downstream systems can
    later replace this with a richer implementation.
    """
    history = list(tone_history or [])
    if new_text:
        history.append(new_text)
    # keep only last 8 entries
    history = history[-8:]
    summary = {
        "history": history,
        "last_excerpt": (new_text or "").strip()[:120],
        "count": len(history),
    }
    return summary


def get_clarifier(tone_state: Dict[str, Any]) -> str:
    """Return a short clarifying prompt adapted to tone_state.

    This provides a friendly fallback clarifier used by
    `dynamic_response_composer` when a more advanced tone module is not
    available.
    """
    last = "" if not tone_state else str(tone_state.get("last_excerpt", ""))
    if last:
        # If last excerpt contains an emotional keyword, prefer acknowledging it
        lower = last.lower()
        for kw in ("anxious", "afraid", "sad", "angry", "overwhelmed", "joy", "happy"):
            if kw in lower:
                return f"I hear you're feeling {kw}. Would you like to tell me more about that?"

        # short echo + invitation
        echo = last if len(last) <= 80 else last[:77].rsplit(" ", 1)[0] + "..."
        return f'I hear you: "{echo}". Can you tell me a bit more about that?'

    return "I hear you. Would you like to tell me more about what's happening for you?"
