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
        # Prefer explicit affect metadata when available (strong signal)
        pipeline = context.get("pipeline_metadata") or context.get("micro_context") or {}
        affect = None
        # Common keys used by pipeline outputs
        if isinstance(pipeline, dict):
            affect = pipeline.get("affect_analysis") or pipeline.get("affect") or pipeline.get("emotion")

        uplift_tones = {"relief", "pride", "excited", "excitement", "amazed", "amazing", "joy", "delight", "satisfaction", "proud", "relieved"}

        # If affect metadata is present and explicit, gate on positive valence + recognized uplift tone
        if isinstance(affect, dict):
            tone = (affect.get("tone") or "").lower()
            valence = float(affect.get("valence") or 0.0)
            arousal = float(affect.get("arousal") or 0.0)
            if tone in uplift_tones and valence > 0.3:
                return True
            # Do NOT trigger solely on positive valence without an explicit uplift tone.
            # Require an explicit uplift tone (relief/pride/excitement/amazed/etc.)

        # Fallback: explicit explicit emotion string in context
        emotion = (context.get("user_emotion") or context.get("emotion") or "").lower()
        if emotion in uplift_tones:
            return True

        # Lexical cues indicating upward movement (conservative list)
        text = (context.get("user_words") or context.get("user_words_raw") or "").lower()
        cues = [
            "i'm relieved", "i am relieved", "i'm so proud", "i am so proud", "i'm proud", "i am proud",
            "i'm excited", "i am excited", "so excited", "amazing", "that was amazing", "wow", "finally",
            "i did it", "i made it", "i passed", "it worked", "i'm glad", "i am glad", "i feel lighter", "i feel better",
            "i'm thrilled", "i am thrilled", "overjoyed", "so happy", "i'm happy", "i am happy", "grateful", "thankful"
        ]

        for cue in cues:
            if cue in text:
                # require that the cue appears in a positive context (avoid matching sarcasm); simple heuristic:
                # if preceding words include negation, reject (e.g., "not happy")
                if any(neg in text for neg in ("not ", "n't ", "never ")):
                    continue
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
        # If there's no positive lift detected, do not append celebratory text.
        if not self._detect_positive_lift(context):
            return ""

        use_excl = self.should_use_exclamation(context)
        if use_excl:
            return random.choice(EXCL_TEMPLATES)
        return random.choice(PERIOD_TEMPLATES)
