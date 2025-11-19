"""Comfort gestures (ASCII art) mapping and helpers.

This module provides a small palette of ASCII comfort gestures keyed to
emotion cues. It also exposes a helper to prepend/append the gesture to
messages and a simple rotation strategy to avoid repeating the same
gesture each time (deterministic based on the message hash).
"""
from __future__ import annotations

from typing import Optional
import hashlib
import random
import os

# Primary mapping: single preferred gesture per emotion
ASCII_COMFORT_MAP = {
    "sadness": ["(っ◕‿◕)っ"],
    "loneliness": ["(づ｡◕‿‿◕｡)づ"],
    "joy": ["ヽ(•‿•)ノ"],
    "celebration": ["✧٩(•́⌄•́๑)و ✧"],
    "frustration": ["(ง •̀_•́)ง"],
    "struggle": ["٩(◕‿◕｡)۶"],
    "calm": ["(˘︶˘).｡*♡"],
    "reflection": ["(｡•́‿•̀｡)"],
    "hope": ["✿◕ ‿ ◕✿"],
    "motivation": ["٩(◕‿◕｡)۶"],
    "encouragement": ["✧٩(•́⌄•́๑)و ✧"],
}


def _choose_variant(variants: list[str], seed: Optional[str] = None) -> str:
    """Choose a deterministic variant from the list using a seed.

    If `seed` is None, choose a random variant.
    """
    if not variants:
        return ""
    if seed is None:
        return random.choice(variants)
    h = hashlib.sha256(seed.encode("utf8")).digest()
    idx = h[0] % len(variants)
    return variants[idx]


def add_comfort_gesture(emotion: str, message: str, position: str = "prepend") -> str:
    """Return `message` with an ASCII comfort gesture added.

    - `emotion` is matched case-insensitively to the mapping keys.
    - `position` may be `prepend` or `append` (defaults to `prepend`).
    - If the environment variable `COMFORT_GESTURES_ENABLED` is set to
      a falsey value ("0", "false", "no"), the original message is
      returned unchanged.
    """
    enabled = os.environ.get("COMFORT_GESTURES_ENABLED", "true").lower()
    if enabled in ("0", "false", "no"):
        return message

    key = (emotion or "").strip().lower() or "calm"
    variants = ASCII_COMFORT_MAP.get(key) or ASCII_COMFORT_MAP.get("calm")
    # Use the message as a seed so repeated calls with the same message
    # yield deterministic choices and avoid immediate repetition.
    gesture = _choose_variant(variants, seed=message)
    if not gesture:
        return message

    if position == "append":
        return f"{message} {gesture}"
    # default: prepend
    return f"{gesture} {message}"


__all__ = ["ASCII_COMFORT_MAP", "add_comfort_gesture"]
