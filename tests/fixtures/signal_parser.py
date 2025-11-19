from typing import Optional
from clarification_memory import lookup_correction


def parse_input(text: str, speaker: Optional[str] = None):
    """A tiny, deterministic parser used only for tests.

    - Checks clarification memory for forced intents (substring match).
    - Detects simple keywords for dominant emotion.
    - Applies a tone overlay for the forced intent `emotional_checkin`.
    """
    result = {
        "forced_intent": None,
        "dominant_emotion": None,
        "tone_overlay": None,
        "clarification_provenance": None,
    }

    # Apply clarification memory if present
    rec = lookup_correction(text)
    if rec:
        result["forced_intent"] = rec["suggested_intent"]
        result["clarification_provenance"] = rec
        if rec["suggested_intent"] == "emotional_checkin":
            result["tone_overlay"] = "reflective, validating"

    # Very small-rule-based emotion detection
    t = text.lower()
    if "anger" in t or "angry" in t:
        result["dominant_emotion"] = "anger"
    elif any(k in t for k in ("sad", "sadness", "invisible", "ignored", "frustrat")):
        result["dominant_emotion"] = "sadness"

    return result
