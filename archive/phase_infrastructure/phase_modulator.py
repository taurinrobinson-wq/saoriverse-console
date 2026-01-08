"""Phase detection and cue sets.

Exports:
- detect_phase(user_input: str, context: dict = None) -> str

Cue sets are provided for clarity and potential extension.
"""

from typing import List, Optional

# Cue lists (kept intentionally readable so maintainers can edit)
initiatory_cues: List[str] = [
    "I just met someone",
    "There’s someone new",
    "Everything just changed",
    "new connection",
    "first conversation",
]

anchoring_cues: List[str] = [
    "I’ve been working through",
    "This relationship has been hard",
    "We’ve been talking for a while",
    "ongoing",
]

voltage_surge_indicators: List[str] = [
    "I feel overwhelmed",
    "I’m spinning",
    "too much",
    "on edge",
]

containment_requests: List[str] = [
    "Can you help me hold this",
    "Can you help me hold",
    "I want to preserve this moment",
    "hold this",
]


def detect_phase(user_input: str, context: Optional[dict] = None) -> str:
    """Return the relational phase: 'initiatory' or 'archetypal'.

    Uses a simple scoring heuristic considering explicit tags, cue
    phrase matches, and surface signals (punctuation/exclamation) to
    decide. This allows nuanced routing when inputs contain mixed cues.
    """
    text = (user_input or "").lower()
    ctx = context or {}

    initiatory_score = 0
    archetypal_score = 0

    # Tags from symbolic_tagger are high-signal
    tags = ctx.get("symbolic_tags") or []
    if any(t in ("initiatory_signal", "voltage_surge") for t in tags):
        initiatory_score += 3
    if any(t in ("anchoring_signal", "containment_request") for t in tags):
        archetypal_score += 3

    # Phrase matches add softer evidence
    for phrase in initiatory_cues + voltage_surge_indicators:
        if phrase.lower() in text:
            initiatory_score += 1

    for phrase in anchoring_cues + containment_requests:
        if phrase.lower() in text:
            archetypal_score += 1

    # Surface cues: exclamation marks, short excited sentences favor initiatory
    if "!" in user_input or text.count("!") >= 1:
        initiatory_score += 1

    # Long, reflective sentences nudge toward archetypal
    if len(user_input.split()) > 25:
        archetypal_score += 1

    # Final decision: initiatory when it has a clear lead; otherwise archetypal
    if initiatory_score > archetypal_score:
        return "initiatory"
    return "archetypal"
