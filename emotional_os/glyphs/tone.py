"""Simple runtime tone detection and state utilities.

This module provides a lightweight tone detector (formal/casual/neutral), a
rolling-window tone state updater, and a clarifier pool selector that ensures
all clarifiers begin with "I hear".

It's intentionally small and dependency-free so it can be easily unit-tested
and extended.
"""
from __future__ import annotations

from typing import List
import random

FORMAL_MARKERS = ["sir", "please", "kindly",
                  "assist", "clarify", "could you", "would you"]
CASUAL_MARKERS = ["hey", "lol", "yo", "cool",
                  "thanks", "what's up", "sup", "dude"]

# Clarifier pools per tone state — every template starts with "I hear"
CLARIFIER_POOLS = {
    "formal": [
        "I hear you're feeling concerned. Could you elaborate further?",
        "I hear you're having a difficult time. Would you like to explain a bit more?",
        "I hear that. Could you say more about what's coming up for you?",
    ],
    "casual": [
        "I hear you're feeling off. What's up?",
        "I hear you're feeling weird — do you want to say more about it?",
        "I hear that. Want to tell me what's going on right now?",
    ],
    "neutral": [
        "I hear you're feeling anxious. What's coming up for you right now?",
        "I hear you. Do you want to tell me a bit more about that?",
        "I hear you're feeling that way. Would you like to say more?",
    ],
}


def detect_tone(user_input: str) -> str:
    """Detect an input's tone as 'formal', 'casual', or 'neutral'.

    Heuristics are intentionally simple and keyword-based so the module is
    transparent and testable. This function can be replaced by a more
    sophisticated detector later if desired.
    """
    if not user_input:
        return "neutral"
    text = user_input.lower()
    # formal markers first
    for m in FORMAL_MARKERS:
        if m in text:
            return "formal"
    for m in CASUAL_MARKERS:
        if m in text:
            return "casual"
    return "neutral"


def update_tone_state(history: List[str], new_input: str, window: int = 4) -> str:
    """Append the detected tone for `new_input` to `history` and return the
    majority tone across the most recent `window` entries.

    `history` is modified in-place.
    """
    tone = detect_tone(new_input)
    history.append(tone)
    if len(history) > window:
        # keep last `window` elements
        del history[0: len(history) - window]
    # majority vote
    # simplest tie behavior: max by count (if tie, deterministic by order in set)
    return max(set(history), key=history.count)


def get_clarifier(tone_state: str) -> str:
    """Return a clarifier template for the given `tone_state`.

    The function selects a random template from the corresponding pool. All
    templates are guaranteed to start with "I hear" to satisfy the
    repository's phrasing guard.
    """
    pool = CLARIFIER_POOLS.get(tone_state) or CLARIFIER_POOLS["neutral"]
    return random.choice(pool)
