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

from src.glyph_response_helpers import scaffold_response


def translate_emotional_response(system_output: Dict) -> str:
    """Map raw emotional metadata into gentle, intuitive phrasing.

    Expected keys in `system_output` (all optional):
    - emotion: str (e.g. 'longing')
    - intensity: str (e.g. 'high', 'gentle')
    - context: str (short descriptor of where emotion arose)
    - resonance: str (a phrase summarizing what the emotion points to)
    """
    emotion = system_output.get("emotion") or "feeling"
    intensity = system_output.get("intensity") or "gentle"
    context = system_output.get("context") or "this moment"
    resonance = system_output.get("resonance") or "a quiet shift"

    # Normalize phrasing to avoid awkward adjective+noun concatenation
    i = (intensity or "").lower()
    if i in ("high", "strong", "intense"):
        opener = f"This {context} seems to have stirred a strong sense of {emotion}."
    else:
        opener = f"There’s a gentle sense of {emotion} here."

    # Keep the invitation concise and permission-oriented
    # Do not force-capitalize `resonance` so tests that look for
    # lowercase tokens such as 'presence' continue to match.
    return f"{opener} {resonance}. Would you like to reflect on that?"


def generate_response_from_glyphs(system_output: Dict) -> str:
    """Generate a user-facing response using glyph overlays if available.

    Expects `system_output` may contain `glyph_overlays_info` (list of {tag, confidence}).
    Falls back to `translate_emotional_response` when overlays are absent.
    """
    glyphs = system_output.get(
        "glyph_overlays_info") or system_output.get("glyph_overlays")
    if not glyphs:
        return translate_emotional_response(system_output)

    # If glyphs is a list of tags, normalize to info form with default confidence
    if glyphs and isinstance(glyphs[0], str):
        glyphs = [{"tag": t, "confidence": 0.5} for t in glyphs]

    scaff = scaffold_response(glyphs)
    resp = scaff.get("response")
    if resp:
        return resp + ""

    # fallback
    return translate_emotional_response(system_output)


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
    return f"Would you like to explore what this {emotion} might be pointing toward in your {context}?"
