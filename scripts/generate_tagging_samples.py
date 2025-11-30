"""Generate a CSV of sample user messages and their tags/phases for review.

Writes `data/tagging_samples.csv` with columns: input, tags, phase

Run: python3 scripts/generate_tagging_samples.py
"""

import csv
import importlib.util
import json
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# Load local modules by path to avoid import path issues when executed
def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sym_mod = _load_module("symbolic_tagger", ROOT / "symbolic_tagger.py")
phase_mod = _load_module("phase_modulator", ROOT / "phase_modulator.py")

tag_input = sym_mod.tag_input
detect_phase = phase_mod.detect_phase
tag_input_with_diagnostics = getattr(sym_mod, "tag_input_with_diagnostics", None)


SAMPLES = [
    "I just met someone who really sees me.",
    "Everything just changed. I feel overwhelmed and excited!",
    "We've been talking for a while and it's been heavy.",
    "I can't breathe, there's too much going on.",
    "The sunset made me feel so alive and seen.",
    "I'm so proud of myself — I got promoted today!",
    "Can you help me hold this? I want to remember it.",
    "I feel lonely even when I'm with people.",
    "This relationship has been hard for months.",
    "There's a spark — something opened in me.",
    "They betrayed me and I can't trust them anymore.",
    "I'm terrified of failing the test tomorrow.",
    "I feel joy and gratitude all at once.",
    "It's a turning point; this feels important.",
    "I feel so seen by them, like they really understand me.",
    "My heart is racing and I'm so excited about this new person.",
    "I've been working through my feelings for a long time.",
    "I want to slow this down and savor it.",
    "Help me hold this with gentleness.",
    "I met someone new yesterday and it was unexpected.",
]

OUT_PATH = Path("data") / "tagging_samples.csv"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Auto-generate paraphrase/synonym variants to expand coverage
SYNONYM_REPLACEMENTS = {
    "overwhelmed": ["overwhelmed", "swamped", "drowning", "snowed under", "buried"],
    "excited": ["excited", "thrilled", "electrified", "elated", "on cloud nine"],
    "met someone": ["met someone", "met a new person", "met someone new", "met someone yesterday", "met a new friend"],
    "lonely": ["lonely", "alone", "isolated", "by myself", "so alone"],
    "betrayed": ["betrayed", "backstabbed", "let down", "they betrayed me"],
    "joy": ["joy", "delight", "bliss", "elation"],
    "gratitude": ["grateful", "thankful", "so grateful", "deep gratitude"],
    "spark": ["spark", "tingle", "flutter", "sparkle"],
    "opened": ["opened", "what's opening", "an opening", "a new opening in me"],
}


def _expand_samples(samples, max_variants=3):
    out = []
    for s in samples:
        out.append(s)
        lowered = s.lower()
        for key, reps in SYNONYM_REPLACEMENTS.items():
            if key in lowered:
                for i, r in enumerate(reps[:max_variants]):
                    variant = s.lower().replace(key, r)
                    out.append(variant)
    # dedupe while preserving order
    seen = set()
    dedup = []
    for t in out:
        if t not in seen:
            dedup.append(t)
            seen.add(t)
    return dedup


EXPANDED = _expand_samples(SAMPLES, max_variants=3)


def _top_fuzzy_candidates(text: str, top_n: int = 3, min_score: float = 0.5):
    """Return top-N fuzzy candidate matches from the synonym groups.

    Each candidate is a dict: {group, phrase, window, score}.
    """
    candidates = []
    text_tokens = text.split()
    for group_name, phrases in getattr(sym_mod, "_SYNONYM_GROUPS", []):
        for phrase in phrases:
            p_tokens = phrase.split()
            p_len = max(1, len(p_tokens))
            # sliding window over text tokens
            for i in range(max(1, len(text_tokens) - p_len + 1)):
                window = " ".join(text_tokens[i : i + p_len])
                score = SequenceMatcher(None, window, phrase).ratio()
                if score >= min_score:
                    candidates.append(
                        {
                            "group": group_name,
                            "phrase": phrase,
                            "window": window,
                            "score": round(float(score), 4),
                        }
                    )
    # sort by score desc
    candidates.sort(key=lambda x: x["score"], reverse=True)
    # dedupe by (group, phrase, window) keeping highest score
    seen = set()
    out = []
    for c in candidates:
        key = (c["group"], c["phrase"], c["window"])
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
        if len(out) >= top_n:
            break
    return out


with OUT_PATH.open("w", encoding="utf-8", newline="") as fh:
    writer = csv.writer(fh)
    writer.writerow(["input", "tags", "phase", "matches_json", "top_fuzzy_json"])
    for s in EXPANDED:
        diag = tag_input_with_diagnostics(s)
        tags = diag.get("tags", [])
        matches = diag.get("matches", [])
        phase = detect_phase(s, {"symbolic_tags": tags})
        top_fuzzy = _top_fuzzy_candidates(s, top_n=3, min_score=0.5)
        writer.writerow(
            [
                s,
                "|".join(tags),
                phase,
                json.dumps(matches, ensure_ascii=False),
                json.dumps(top_fuzzy, ensure_ascii=False),
            ]
        )

print(f"Wrote expanded tagging CSV to: {OUT_PATH} (rows: {len(EXPANDED)})")
