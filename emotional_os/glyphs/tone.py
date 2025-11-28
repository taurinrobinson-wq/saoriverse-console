"""Minimal tone utilities for dynamic response composition.

This module provides a lightweight, deterministic implementation of the
functions used by `dynamic_response_composer` during tests: `update_tone_state`
and `get_clarifier`. The real project likely has a richer tone model; the
implementation here is intentionally small and safe — enough to unblock the
test/import pipeline while preserving expected interfaces.
"""
from typing import List, Dict


def update_tone_state(history: List[str], latest_text: str) -> Dict:
    """Return a compact tone state derived from recent history and latest text.

    Args:
        history: rolling list of past tone labels or raw user texts
        latest_text: the newest user message

    Returns:
        A dict representing the inferred tone state. Tests and callers only
        expect a dict-like opaque object that `get_clarifier` can inspect.
    """
    # Very small heuristic: look for obvious emotion words and shortness
    text = (latest_text or "").lower()
    state = {
        "recent": history[-5:] if history else [],
        "primary": None,
        "short": len(text.split()) <= 6,
    }

    for emo in ("grief", "sad", "angry", "frustrat", "anx", "happy", "joy"):
        if emo in text:
            state["primary"] = emo
            break

    if not state["primary"] and history:
        # try to reuse last known tone token if provided
        for h in reversed(history):
            if isinstance(h, str) and h:
                state["primary"] = h
                break

    return state


def get_clarifier(tone_state: Dict) -> str:
    """Return a short clarifying question adapted to the tone state.

    This is intentionally conservative and non-intrusive.
    """
    primary = (tone_state or {}).get("primary")
    short = (tone_state or {}).get("short")

    if primary and any(k in primary for k in ("grief", "sad", "angry", "frustrat")):
        return "I hear something heavy there — would you like to tell me more about that?"

    if primary and any(k in primary for k in ("anx",)):
        return "That sounds worrying — can you say a bit more about what's making you feel that way?"

    if short:
        return "Could you say a little more so I can help?"

    return "I hear you — would you like to tell me more about that?"
