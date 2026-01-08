"""Minimal Pun Interjector stub for Saonyx Emotional OS.

This module provides a small, testable scaffold that follows the design
in `docs/new_additions_20251222.md`.

It is intentionally lightweight: policies (safety, frequency) are expressed
as simple checks so the real signal bus can plug in without friction.
"""
from dataclasses import dataclass
from typing import Dict, Optional
import random


@dataclass
class Pun:
    setup: str
    twist: str
    callback: Optional[str]
    tone: str
    intensity: float


class PunInterjector:
    """Simple Pun Interjector.

    Methods accept a `context` dict so integration is straightforward. Expected
    context keys (not exhaustive):
    - `user_emotion`: str (e.g. 'frustration', 'warm', 'neutral')
    - `contains_wordplay`: bool
    - `safety_tier`: int (1..3)
    - `recent_pun_turns`: int (turns since last pun)
    """

    GLYPH_TEMPLATES = {
        "LEVITY": [
            ("Sounds like your day is stacking up", "but at least it’s not slacking off"),
            ("That’s annoying", "but at least it didn’t unpack itself")
        ],
        "WORDPLAY": [
            ("You need long johns", "or long janes — equal opportunity insulation"),
        ],
        "DEFUSION": [
            ("That sounds rough", "but at least it didn’t unravel completely"),
        ],
        "WARM_MIRROR": [
            ("You’re on a roll", "should I butter you up or let you keep going?"),
        ],
    }

    def __init__(self, min_turns_between_puns: int = 8):
        self.min_turns_between_puns = min_turns_between_puns

    def should_trigger(self, context: Dict) -> bool:
        """Return True when a pun is allowed given the context.

        Basic safety and frequency checks are applied here. Real integration
        should consult the central safety layer instead of local heuristics.
        """
        safety_tier = context.get("safety_tier", 1)
        if safety_tier >= 3:
            return False

        recent = context.get("recent_pun_turns", 999)
        if recent < self.min_turns_between_puns:
            return False

        user_emotion = context.get("user_emotion", "neutral")
        contains_wordplay = context.get("contains_wordplay", False)

        if contains_wordplay:
            return True

        if user_emotion in ("warm", "playful"):
            return True

        if user_emotion == "frustration":
            return True

        # default: do not trigger
        return False

    def compose_pun(self, context: Dict) -> Optional[Pun]:
        """Compose a pun for the given context. Returns a Pun or None.

        This is a minimal composer — real implementation should consult
        lexical resources and a template repository.
        """
        if not self.should_trigger(context):
            return None

        # Choose glyph
        if context.get("contains_wordplay"):
            glyph = "WORDPLAY"
        else:
            glyph = random.choice(["LEVITY", "DEFUSION", "WARM_MIRROR"])

        templates = self.GLYPH_TEMPLATES.get(glyph, [])
        if not templates:
            return None

        setup, twist = random.choice(templates)
        callback = None
        tone = "playful" if glyph in ("WORDPLAY", "LEVITY") else "soft"
        intensity = 0.4 if tone == "soft" else 0.6

        return Pun(setup=setup, twist=twist, callback=callback, tone=tone, intensity=intensity)

    def render(self, pun: Pun) -> str:
        """Render a Pun object into a single-line response (one paragraph).

        The renderer follows the Saonyx style rules: one paragraph, no em dashes.
        """
        if not pun:
            return ""

        if pun.callback:
            return f"{pun.setup}. {pun.twist}. {pun.callback}"
        return f"{pun.setup}. {pun.twist}."
