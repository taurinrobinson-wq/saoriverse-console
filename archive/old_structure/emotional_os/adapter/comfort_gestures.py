"""Comfort gestures (ASCII art) mapping and helpers.

This module provides a small palette of ASCII comfort gestures keyed to
emotion cues. It also exposes a helper to prepend/append the gesture to
messages and a simple rotation strategy to avoid repeating the same
gesture each time (deterministic based on the message hash).
"""

from __future__ import annotations

import hashlib
import os
import random
from typing import Optional

# Primary mapping: single preferred gesture per emotion
ASCII_COMFORT_MAP = {
    "sadness": ["(っ◕‿◕)っ", "(つ╯‿╰)つ", "(っ˘̩╭╮˘̩)っ"],
    "loneliness": ["(づ｡◕‿‿◕｡)づ", "(つ˵•́ ᴗ •̀˵)つ"],
    "joy": ["ヽ(•‿•)ノ", "(ﾉ^_^)ﾉ", "(＾▽＾)"],
    "celebration": ["✧٩(•́⌄•́๑)و ✧", "ヽ(＾Д＾)ﾉ", "\(^o^)/"],
    "frustration": ["(ง •̀_•́)ง", "(ง'̀-'́)ง", "(ง︡'-'︠)ง"],
    "struggle": ["٩(◕‿◕｡)۶", "(ง˘̀_˘́)ง"],
    "calm": ["(˘︶˘).｡*♡", "(¬‿¬)", "(˶ˆ꒳ˆ˶)"],
    "reflection": ["(｡•́‿•̀｡)", "(｡･ω･｡)", "( ͡ᵔ ͜ʖ ͡ᵔ )"],
    "hope": ["✿◕ ‿ ◕✿", "(✿◠‿◠)", "(◕‿◕✿)"],
    "motivation": ["٩(◕‿◕｡)۶", "(ง°ل͜°)ง", "( •̀ᴗ•́ )و"],
    "encouragement": ["✧٩(•́⌄•́๑)و ✧", "(＾ｰ^)ノ", "(ﾉ･∀･)ﾉ"],
}


def _choose_variant(variants: list[str], seed: Optional[str] = None) -> str:
    """Choose a deterministic variant from the list using a seed.

    If `seed` is None, choose a random variant.
    """
    if not variants:
        return ""
    if seed is None:
        # rotate based on a coarse time bucket to vary across sessions
        try:
            import datetime

            bucket = datetime.date.today().strftime("%Y%m")
            seed = bucket
        except Exception:
            return random.choice(variants)
    h = hashlib.sha256(seed.encode("utf8")).digest()
    idx = h[0] % len(variants)
    return variants[idx]


def add_comfort_gesture(
    emotion: str, message: str, position: str = "prepend", session_seed: Optional[str] = None
) -> str:
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
    # Choose a seed for deterministic rotation: prefer explicit session_seed,
    # otherwise use the message combined with a monthly bucket inside _choose_variant.
    seed = session_seed or message
    gesture = _choose_variant(variants, seed=seed)
    if not gesture:
        return message

    if position == "append":
        return f"{message} {gesture}"
    # default: prepend
    return f"{gesture} {message}"


__all__ = ["ASCII_COMFORT_MAP", "add_comfort_gesture"]
