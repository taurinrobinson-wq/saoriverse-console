from typing import List, Dict


def scaffold_response(glyph_overlays_info: List[Dict]) -> Dict:
    """Simple scaffolding: map glyph overlay confidences to tone and pacing suggestions.

    Returns a structure with:
      - primary_tag: highest-confidence overlay tag
      - tone: one of ('calm', 'firm', 'empathetic')
      - pacing: float (0.0 slow / 1.0 fast)
      - details: original overlays
    """
    if not glyph_overlays_info:
        return {"primary_tag": None, "tone": "neutral", "pacing": 0.5, "details": []}

    # Sort overlays by confidence
    sorted_overlays = sorted(
        glyph_overlays_info, key=lambda o: -o.get("confidence", 0.0))
    primary = sorted_overlays[0]
    tag = primary.get("tag")
    conf = float(primary.get("confidence", 0.0))

    # Map tags to a simple tone and pacing heuristic
    tone = "neutral"
    pacing = 0.5
    if tag == "anger":
        tone = "firm"
        pacing = 0.8 if conf >= 0.6 else 0.65
    elif tag == "sadness":
        tone = "empathetic"
        pacing = 0.4 if conf >= 0.5 else 0.45
    elif tag == "feeling_unseen":
        tone = "validating"
        pacing = 0.45 if conf >= 0.6 else 0.5

    return {"primary_tag": tag, "tone": tone, "pacing": pacing, "details": sorted_overlays}
