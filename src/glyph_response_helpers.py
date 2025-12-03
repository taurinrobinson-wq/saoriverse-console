import datetime
import os
import re
from typing import Dict, List

from src.glyph_response_templates import pick_template


def scaffold_response(glyph_overlays_info: List[Dict]) -> Dict:
    """Simple scaffolding: map glyph overlay confidences to tone, pacing and a response string.

    Returns a structure with:
      - primary_tag: highest-confidence overlay tag
      - tone: one of ('calm', 'firm', 'empathetic')
      - pacing: float (0.0 slow / 1.0 fast)
      - details: original overlays
      - response: a short response string selected from templates
    """
    if not glyph_overlays_info:
        return {"primary_tag": None, "tone": "neutral", "pacing": 0.5, "details": [], "response": None}

    # Sort overlays by confidence
    sorted_overlays = sorted(
        glyph_overlays_info, key=lambda o: -o.get("confidence", 0.0))
    primary = sorted_overlays[0]
    tag = primary.get("tag")
    conf = float(primary.get("confidence", 0.0))

    # If multiple overlays have similar confidence, treat as a mixed emotion cluster
    if len(sorted_overlays) > 1:
        top_conf = float(sorted_overlays[0].get("confidence", 0.0))
        second_conf = float(sorted_overlays[1].get("confidence", 0.0))
        if abs(top_conf - second_conf) < 0.2:
            # classify as a mixed emotion cluster
            tag = "mixed_emotion"
            # use average confidence for template selection
            conf = round((top_conf + second_conf) / 2.0, 4)

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
    elif tag == "mixed_emotion":
        tone = "attentive"
        pacing = 0.5

    # Choose a template and render a short phrase. Use the primary confidence and tag.
    # Sanitize tag and short_phrase to avoid leaking internal glyph labels (e.g., VELΩNIX)
    valid_tag = tag and re.match(r"^[a-z_]+$", tag)
    safe_tag = tag if valid_tag else "default"
    short_phrase = tag.replace("_", " ") if valid_tag else "something"

    # If the tag is unsafe, log it for later curation (do not surface to user)
    if not valid_tag and tag:
        try:
            logdir = os.path.join(os.getcwd(), "logs")
            os.makedirs(logdir, exist_ok=True)
            path = os.path.join(logdir, "unsafe_tags.log")
            ts = datetime.datetime.utcnow().isoformat()
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(f"{ts}\t{tag}\t{conf}\t{sorted_overlays}\n")
        except Exception:
            # never fail user flows because logging couldn't write
            pass

    template = pick_template(safe_tag or "default", conf)
    response = template.format(short_phrase=short_phrase)

    return {"primary_tag": tag, "tone": tone, "pacing": pacing, "details": sorted_overlays, "response": response}
