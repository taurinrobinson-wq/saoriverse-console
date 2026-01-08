#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

LEX_PATH = Path("emotional_os/glyphs/glyph_lexicon_rows_validated.json")
OUT_CSV = Path("dev_tools/extracted_to_lexicon_mapping.csv")

EXTRACTED = [
    {"name": "feeling_unmoored", "description": "A sense of instability and lack of direction."},
    {"name": "seeking_stability", "description": "The desire for something solid to hold onto."},
    {"name": "anger", "description": "Furious feelings about being dismissed at work."},
    {"name": "dismissal", "description": "Feeling disregarded and undervalued in a professional setting."},
    {"name": "longing", "description": "A deep sense of yearning for someone who is absent."},
    {"name": "heartache", "description": "Emotional pain stemming from missing someone dearly."},
    {"name": "quiet_joy", "description": "A serene happiness found in peaceful moments."},
    {"name": "overwhelm", "description": "Feeling burdened by excessive responsibilities and emotions."},
]

BASE_SYNS = {
    "unmoored": ["adrift", "ungrounded", "untethered"],
    "stability": ["stability", "anchor", "grounding", "something to hold onto"],
    "anger": ["furious", "angry", "irate", "enraged"],
    "dismissal": ["dismissed", "ignored", "overlooked", "undervalued"],
    "longing": ["miss", "yearn", "ache", "pining"],
    "heartache": ["ache", "sorrow", "heartache", "grief"],
    "quiet_joy": ["quiet joy", "serene joy", "contentment", "peaceful happiness"],
    "overwhelm": ["overwhelmed", "burdened", "swamped", "stressed"],
}


def normalize_text(s):
    s = s or ""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def to_snake(s):
    s = normalize_text(s)
    return s.replace(" ", "_")


def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    a_len = len(a)
    b_len = len(b)
    dp = list(range(b_len + 1))
    for i in range(1, a_len + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, b_len + 1):
            cur = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev
            else:
                dp[j] = min(prev, dp[j - 1], dp[j]) + 1
            prev = cur
    return dp[b_len]


def similarity(a, b):
    a = a or ""
    b = b or ""
    maxlen = max(len(a), len(b))
    if maxlen == 0:
        return 1.0
    dist = levenshtein(a, b)
    return 1 - dist / maxlen


# load lexicon
with LEX_PATH.open("r", encoding="utf-8") as f:
    lex = json.load(f)

entries = []
for row in lex:
    glyph_name = row.get("glyph_name") or row.get("name") or ""
    desc = row.get("description") or ""
    gid = row.get("id") or row.get("idx") or ""
    norm_name = normalize_text(glyph_name)
    snake = to_snake(glyph_name)
    entries.append(
        {"id": gid, "glyph_name": glyph_name, "norm_name": norm_name, "snake": snake, "description": desc, "row": row}
    )

rows_out = []
for ex in EXTRACTED:
    ex_name = ex["name"]
    ex_desc = ex.get("description", "")
    ex_norm = normalize_text(ex_name.replace("_", " "))
    best = None
    best_score = 0
    # exact by snake
    for e in entries:
        if ex_name == e["snake"]:
            best = e
            best_score = 1.0
            break
    # exact by normalized name
    if not best:
        for e in entries:
            if ex_norm == e["norm_name"]:
                best = e
                best_score = 0.98
                break
    # fuzzy by similarity
    if not best:
        for e in entries:
            s = similarity(ex_norm, e["norm_name"])
            if s > best_score:
                best_score = s
                best = e
    # description token overlap
    desc_tokens = set(normalize_text(ex_desc).split())
    desc_overlap = 0
    if best:
        lex_tokens = set(normalize_text(best["description"]).split())
        common = desc_tokens.intersection(lex_tokens)
        desc_overlap = len(common)
        if desc_overlap:
            best_score = min(1.0, best_score + 0.05)

    if best and best_score >= 0.9:
        match_type = "exact" if best_score >= 0.99 else "strong_fuzzy"
        matched_id = best.get("id")
        matched_name = best.get("glyph_name")
    elif best and best_score >= 0.75:
        match_type = "fuzzy"
        matched_id = best.get("id")
        matched_name = best.get("glyph_name")
    else:
        match_type = "none"
        matched_id = ""
        matched_name = ""

    # suggestions
    suggestions = []
    triggers = []
    key = ex_name
    key_token = key.split("_")[0]
    base_syns = BASE_SYNS.get(key_token, [])
    suggestions.extend(base_syns)
    for t in ex_name.split("_"):
        if t and t not in suggestions:
            suggestions.append(t)
    for t in normalize_text(ex_desc).split()[:6]:
        if t not in suggestions:
            suggestions.append(t)
    triggers.append(ex_name.replace("_", " "))
    triggers.append(ex_name)

    new_glyph = "no" if match_type != "none" else "yes"

    rows_out.append(
        {
            "extracted_name": ex_name,
            "extracted_description": ex_desc,
            "match_type": match_type,
            "match_score": round(best_score, 3),
            "matched_id": matched_id,
            "matched_glyph_name": matched_name,
            "suggested_synonyms": ";".join(suggestions[:8]),
            "suggested_triggers": ";".join(list(dict.fromkeys(triggers)))[:200],
            "new_glyph_needed": new_glyph,
        }
    )

# write CSV
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "extracted_name",
            "extracted_description",
            "match_type",
            "match_score",
            "matched_id",
            "matched_glyph_name",
            "suggested_synonyms",
            "suggested_triggers",
            "new_glyph_needed",
        ],
    )
    writer.writeheader()
    for r in rows_out:
        writer.writerow(r)

print("Wrote mapping to", OUT_CSV)
