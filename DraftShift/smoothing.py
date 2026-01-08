import re
from typing import List


def smooth_text(text: str) -> str:
    """Run lightweight smoothing: remove duplicate empathy phrases, trim repeated sentences.

    This is intentionally conservative; leave heavy rewriting to the transformer.
    """
    # collapse repeated phrases like "I understand. I understand." -> "I understand."
    text = re.sub(r"(I understand\.)\s+(I understand\.)+", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"(Thanks for reaching out\.)\s+(Thanks for reaching out\.)+", r"\1", text, flags=re.IGNORECASE)

    # remove obvious duplicated sentences
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    seen = set()
    out: List[str] = []
    for p in parts:
        key = p.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(p.strip())
    res = ' '.join(out)
    # normalize spaces
    res = re.sub(r'\s+', ' ', res).strip()
    return res
