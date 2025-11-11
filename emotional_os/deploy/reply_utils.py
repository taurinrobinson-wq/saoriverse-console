import hashlib
from typing import List


def polish_ai_reply(text: str) -> str:
    """Return a user-facing polished reply.

    - Collapse duplicated short lines.
    - Replace short generic fallbacks with a deterministic rotated alternative.
    """
    t = (text or '').strip()
    # Collapse repeated identical sentences (e.g., "I'm here to listen.")
    parts = [p.strip() for p in t.split('\n') if p.strip()]
    if len(parts) > 1 and all(p == parts[0] for p in parts):
        t = parts[0]

    generic_fallbacks = {"I'm here to listen.", "I'm here to listen and help.", "I'm here to listen and support you."}
    if t in generic_fallbacks or t.lower().startswith("i'm here to listen"):
        alternatives: List[str] = [
            "I hear you — tell me more when you're ready.",
            "I'm listening. What's coming up for you right now?",
            "Thank you for sharing. I'm here to listen and support you."
        ]
        if len(t) > 40:
            return t
        try:
            h = int(hashlib.sha1(t.encode('utf-8')).hexdigest()[:8], 16)
            return alternatives[h % len(alternatives)]
        except Exception:
            return alternatives[0]

    return t
