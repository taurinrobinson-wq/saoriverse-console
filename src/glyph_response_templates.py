"""Response templates keyed by glyph tag.

Each tag maps to a list of template variants. Templates may include
simple placeholders like {name} or {context} in future iterations.
"""

from typing import Dict, List

TEMPLATES = {
    "anger": [
        "I hear a sharpness in that — it sounds like anger. When that fires up, do you want a moment to ground first?",
        "That sounds heated. I can stay with that intensity if you want — would you like to name what’s behind it?",
        "There’s a flash of anger here; if you want, we can name it together and look at what it’s pointing to.",
    ],
    "sadness": [
        "That sounds heavy and quiet — sadness is present. I can sit with you in that stillness if you'd like.",
        "It sounds like sadness is moving through you. If it helps, we can breathe together and hold that feeling for a moment.",
        "There’s a soft ache in what you said; I’m here to listen to it with you.",
    ],
    "feeling_unseen": [
        "I hear you — feeling unseen can be very lonely. Would you like to tell me more about when that happens?",
        "It feels like a veil was between you and the others. I’m here if you want to describe it more.",
        "That sense of being overlooked matters. If you want, we can name what you wished for in that moment.",
    ],
    # Generic cluster templates for mixed or uncertain overlays
    "mixed_emotion": [
        "I’m noticing several feelings at once — we can slow down and explore any one of them, or hold them together.",
        "There’s a mix of tones here; would you prefer to focus on the sharpest feeling, or share how they sit together?",
    ],
    "fallback": [
        "I’m here to listen. If you want, tell me more about what that was like for you.",
        "Thank you for sharing that — would you like to unpack it together?",
    ],
}


def pick_template(tag: str, confidence: float):
    """Return a template string for the given tag and confidence.

    - If the tag exists in TEMPLATES, pick a variant based on confidence.
    - For unknown tags, return a fallback template.
    """
    if tag in TEMPLATES:
        variants = TEMPLATES[tag]
    else:
        variants = TEMPLATES.get("fallback", ["I’m here to listen."])

    # Use confidence to pick a variant (higher confidence -> earlier variant)
    idx = 0
    if confidence >= 0.75 and len(variants) > 1:
        idx = 0
    elif confidence >= 0.5 and len(variants) > 2:
        idx = 1
    else:
        idx = min(len(variants) - 1, 2 if len(variants) > 2 else 0)

    return variants[idx]


# A small set of response templates per glyph tag.
# Each entry contains a list of templates; templates may include {resonance}
# and {short_phrase} placeholders for minor variation.
TEMPLATES: Dict[str, List[str]] = {
    "anger": [
        "I hear a sharp edge here — {short_phrase}. If you'd like, we can name what stung.",
        "That sounds like anger cutting through; it's loud and clear. {short_phrase}.",
        "There is heat in this moment — {short_phrase}. I'm here if you want to let it out aloud.",
    ],
    "sadness": [
        "I'm holding a soft space for that sadness — {short_phrase}. Would you like to stay with it a moment?",
        "This feels quiet and low, like dusk. {short_phrase}. If it helps, we can name what mattered.",
        "There's a tenderness here — {short_phrase}. I can listen at your pace.",
    ],
    "feeling_unseen": [
        "It sounds like you felt unseen — {short_phrase}. That matters; thank you for saying it.",
        "There was a shadow where you expected attention. {short_phrase}. Do you want to describe what you wished for?",
        "I hear the ache of being overlooked — {short_phrase}. You're not invisible here.",
    ],
    "default": [
        "I notice something stirring — {short_phrase}. Would you like to say more?",
        "There's a feeling here worth noticing — {short_phrase}. I'm here to follow it with you.",
    ],
}


def pick_template(tag: str, confidence: float) -> str:
    """Select a template for a tag. Use confidence to bias selection deterministically."""
    options = TEMPLATES.get(tag) or TEMPLATES["default"]
    # deterministic choice: pick index based on rounded confidence
    idx = int((confidence * 10)) % len(options)
    return options[idx]
