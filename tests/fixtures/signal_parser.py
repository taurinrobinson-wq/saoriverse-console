from typing import Optional, List, Dict
from clarification_memory import lookup_correction
from rule_engine_helper import analyze_text


# Small routing table used by tests to map forced intents to tone overlays.
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
      - glyph_overlays  (list of overlay tags, kept for test compatibility)
      - glyph_overlays_info (list of {tag, confidence})
    """
    result = {
        "forced_intent": None,
        "dominant_emotion": None,
        "tone_overlay": None,
        "clarification_provenance": None,
        "glyph_overlays": [],
        "glyph_overlays_info": [],
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

    # Use shared test helper for tokenization/overlay detection
    analysis = analyze_text(text)
    result["glyph_overlays_info"] = analysis.get("glyph_overlays_info", [])
    result["glyph_overlays"] = analysis.get("glyph_overlays", [])

    # Dominant emotion: derive confidences from glyph_overlays_info
    conf_map = {i["tag"]: float(i.get("confidence", 0.0))
                for i in result.get("glyph_overlays_info", [])}
    anger_conf = conf_map.get("anger", 0.0)
    sad_conf = conf_map.get("sadness", 0.0)
    unseen_conf = conf_map.get("feeling_unseen", 0.0)

    if anger_conf > max(sad_conf, unseen_conf):
        result["dominant_emotion"] = "anger"
    elif sad_conf >= anger_conf or unseen_conf > 0.0:
        result["dominant_emotion"] = "sadness"

    return result
