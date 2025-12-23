"""Minimal Mutual Joy Handler for Saonyx Emotional OS.

Provides a lightweight implementation of the exclamation-rule logic and
template selection so the module can be integrated and tested.
"""
from typing import Dict, Optional
import random


EXCL_TEMPLATES = [
    "I’m really glad that happened for you!",
    "Feels like a real shift!",
    "That must have felt incredible!",
    "I’m so happy you got that moment!",
    "You’ve been working toward this. I’m thrilled for you!",
    "That’s such a meaningful win!",
]

PERIOD_TEMPLATES = [
    "I’m really glad that happened for you.",
    "Feels like a real shift.",
    "That must have felt incredible.",
    "I’m so happy you got that moment.",
    "You’ve been working toward this. I’m really glad you reached it.",
    "That’s a meaningful win.",
]


class MutualJoyHandler:
    """Handler that decides when to celebrate with the user.

    Methods expect a `context` dict containing:
    - `user_emotion`: str (e.g. 'lift', 'neutral')
    - `safety_tier`: int
    - `long_arc`: bool (True when this follows struggle)
    - `user_words`: str (recent user utterance)
    - `turns_since_exclaim`: int
    """

    def __init__(self, min_turns_between_exclaims: int = 6):
        self.min_turns_between_exclaims = min_turns_between_exclaims

    def _detect_positive_lift(self, context: Dict) -> bool:
        emotion = context.get("user_emotion", "neutral")
        if emotion in ("lift", "joy", "pride", "relief"):
            return True
        # simple lexical cue check
        text = (context.get("user_words") or "").lower()
        for cue in ("amazing", "wow", "finally", "i'm so happy", "i'm glad"):
            if cue in text:
                return True
        return False

    def should_use_exclamation(self, context: Dict) -> bool:
        """Apply the decision tree for allowing an exclamation mark.

        Returns True when an exclamation is permitted.
        """
        if context.get("safety_tier", 1) >= 3:
            return False

        if context.get("turns_since_exclaim", 999) < self.min_turns_between_exclaims:
            return False

        if not self._detect_positive_lift(context):
            return False

        if not context.get("long_arc", False) and not context.get("user_words"):
            # prefer clear context or explicit long-arc
            return False

        # Passed checks — allow exclamation
        return True

    def choose_template(self, context: Dict) -> str:
        """Choose a template line, deciding on exclamation or period.

        Always returns a single paragraph string.
        """
        use_excl = self.should_use_exclamation(context)
        if use_excl:
            return random.choice(EXCL_TEMPLATES)
        return random.choice(PERIOD_TEMPLATES)
