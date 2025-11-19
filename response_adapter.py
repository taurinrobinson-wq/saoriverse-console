"""Convert backend outputs into emotionally fluent, user-facing language.

API (public):
- translate_emotional_response(system_output: dict) -> str
- reflect_relationship(name: str, prior_context: dict) -> str
- suggest_resonance_action(emotion: str, context: str) -> str

Design notes:
- Avoid exposing backend terms like 'glyph', 'signal', or 'voltage' in
  user-facing text. Use metaphorical, gentle phrasing.
"""
from typing import Dict, List, Optional


def translate_emotional_response(system_output: Dict) -> str:
    """Map raw emotional metadata into gentle, intuitive phrasing.

    Expected keys in `system_output` (all optional):
    - emotion: str (e.g. 'longing')
    - intensity: str (e.g. 'high', 'gentle')
    - context: str (short descriptor of where emotion arose)
    - resonance: str (a phrase summarizing what the emotion points to)
    """
    emotion = system_output.get("emotion") or "emotion"
    intensity = system_output.get("intensity") or "subtle"
    context = system_output.get("context") or "this moment"
    resonance = system_output.get("resonance") or "a quiet shift"

    # Build phrasing while avoiding technical vocabulary
    i = (intensity or "").lower()
    if i in ("high", "strong", "intense"):
        opener = f"This {context} seems to have stirred something deep — {emotion} with some force."
    else:
        # Normalize adverb/adjective forms to a simple adjective phrase.
        if i.endswith("ly"):
            adj = i[:-2]
        else:
            adj = i or "gentle"
        # Guard against duplicate words (e.g. "gentle gentle") by using a single adjective.
        opener = f"There's a {adj} {emotion} here."

    return f"{opener} It feels like {resonance}. Would you like to reflect on that?"


def reflect_relationship(name: str, prior_context: Optional[Dict] = None) -> str:
    """Generate a relational reflection without exposing backend terms.

    `prior_context` can include keys such as `emotional_tone` (list[str])
    and `recent_summary` (str).
    """
    prior_context = prior_context or {}
    tones = prior_context.get("emotional_tone") or []
    recent_summary = prior_context.get("recent_summary")

    tone_phrase = " and ".join(tones) if tones else "a quiet tenderness"
    base = f"{name} seems to hold {tone_phrase} for you."
    if recent_summary:
        base += f" When you say more, I notice: {recent_summary}."

    return base


def suggest_resonance_action(emotion: str, context: str) -> str:
    """Offer an exploratory prompt aligned with user context.

    Keep suggestions permission-oriented and optional.
    """
    return (
        f"Would you like to explore what this {emotion} might be pointing toward in your {context}?"
    )
