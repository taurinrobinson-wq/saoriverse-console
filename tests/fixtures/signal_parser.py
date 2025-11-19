from typing import Optional, List, Dict
from clarification_memory import lookup_correction


def _keyword_glyphs(text: str) -> List[str]:
    """Map simple keywords to glyph overlays (test-only heuristic)."""
    t = text.lower()
    overlays = []
    if any(k in t for k in ("ignore", "ignored", "invisible", "invisibl")):
        overlays.append("feeling_unseen")
    if any(k in t for k in ("anger", "angry")):
        overlays.append("anger")
    if any(k in t for k in ("sad", "sadness", "stung", "frustrat")):
        overlays.append("sadness")
    return overlays


_routing_table: Dict[str, str] = {
    "emotional_checkin": "reflective, validating",
}


def parse_input(text: str, speaker: Optional[str] = None) -> Dict:
    """A more expressive test parser used to mock routing, glyph overlays and provenance.

    Returns a dict with keys:
      - forced_intent
      - dominant_emotion
      - tone_overlay
      - clarification_provenance
      - glyph_overlays
    """
    result = {
        "forced_intent": None,
        "dominant_emotion": None,
        "tone_overlay": None,
        "clarification_provenance": None,
        "glyph_overlays": [],
    }

    # Check clarification memory
    rec = lookup_correction(text)
    if rec:
        result["forced_intent"] = rec["suggested_intent"]
        # enrich provenance with stable keys expected by tests
        result["clarification_provenance"] = {
            "record_id": rec.get("record_id"),
            "trigger_phrase": rec.get("trigger_phrase"),
            "suggested_intent": rec.get("suggested_intent"),
            "confidence": rec.get("confidence"),
            "timestamp": rec.get("timestamp"),
        }
        # Apply routing table to decide tone overlay
        tone = _routing_table.get(rec["suggested_intent"])
        if tone:
            result["tone_overlay"] = tone

    # Glyph overlay inference (returns list of overlay tags)
    overlays = _keyword_glyphs(text)
    result["glyph_overlays"] = overlays

    # Dominant emotion selection: if both anger and sadness appear, choose the one explicitly stated
    if "anger" in overlays:
        result["dominant_emotion"] = "anger"
    elif "sadness" in overlays or "feeling_unseen" in overlays:
        result["dominant_emotion"] = "sadness"

    return result
