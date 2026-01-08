"""Tone adapter templates for each phase.

Exports:
- generate_initiatory_response(user_context: dict) -> str
- generate_archetypal_response(user_context: dict) -> str

These functions produce short, evocative prompts suitable for
post-processing by the response_adapter.
"""

from typing import Dict, Optional


def generate_initiatory_response(user_context: Optional[Dict] = None) -> str:
    """Expansive, evocative, voltage-forward phrasing.

    Behavior is intensity-aware and selects a slightly different template
    for high vs. gentle intensity so the voice matches the user's arousal.
    """
    ctx = user_context or {}
    intensity = (ctx.get("intensity") or "gentle").lower()
    preview = ctx.get("preview")

    # Favor short, inquisitive prompts that feel like a treasured friend.
    if intensity in ("high", "strong", "intense"):
        if preview:
            return f"Wow, what about {preview} feels most alive for you?"
        return "That sounds intense, can you tell me a bit more about how it feels?"

    # gentle / default
    if preview:
        return f"That sounds like a spark. What about {preview} stands out to you?"
    return "Can you tell me more about how that feels?"


def generate_archetypal_response(user_context: Optional[Dict] = None) -> str:
    """Grounded, reverent, legacy-aware phrasing.

    Selects a template that leans into containment for higher-intensity
    emotional material, and a more gently honoring tone otherwise.
    """
    ctx = user_context or {}
    intensity = (ctx.get("intensity") or "gentle").lower()
    anchor = ctx.get("anchor")

    # Keep archetypal responses short and honoring; prefer curiosity over statements.
    if intensity in ("high", "strong", "intense"):
        if anchor:
            return f"That matters, what's one small part of {anchor} you'd like to hold on to?"
        return "That sounds heavy, would you like to say a bit more about it?"

    if anchor:
        return f"That seems meaningful around {anchor}. What feels important to you about it?"
    return "What about that feels most important to you right now?"
