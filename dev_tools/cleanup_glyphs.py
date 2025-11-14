#!/usr/bin/env python3
"""
dev_tools/cleanup_glyphs.py

Parse a downloaded SQL INSERT export of the `glyphs` table (e.g. `glyphs_rows.sql`),
normalize fields, deduplicate, and produce cleaned preview artifacts.

This script runs in --dry-run mode by default (no Supabase interaction).

Outputs (dry-run):
- dev_tools/cleaned_glyphs.json           : array of cleaned glyph objects
- dev_tools/cleaned_glyphs_upsert.csv    : CSV suitable for upsert (JSON triggers column)
- dev_tools/cleanup_report.md            : summary + sample rows

Usage examples:
  python3 dev_tools/cleanup_glyphs.py --source glyphs_rows.sql --dry-run --sample 20
  python3 dev_tools/cleanup_glyphs.py --source glyphs_rows.sql --out-json out.json --out-csv out.csv --no-dry-run

The parser is conservative: it handles single-quoted SQL strings which may contain
escaped single quotes (''), and splits top-level tuples and top-level commas.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import unicodedata


SQL_COLS = [
    "id",
    "name",
    "description",
    "triggers",
    "response_layer",
    "depth",
    "last_updated",
    "symbolic_pairing",
    "user_id",
    "created_from_chat",
    "source_message",
    "emotional_tone",
    "glyph_type",
    "tenant_id",
]


def find_values_section(sql: str) -> str:
    m = re.search(r"\bVALUES\b", sql, flags=re.IGNORECASE)
    if not m:
        raise ValueError("No VALUES keyword found in SQL file")
    return sql[m.end():]


def iter_tuples(values_section: str):
    """Yield raw tuple text (without outer parentheses) from the VALUES section.

    Handles single-quoted strings and escaped single quotes ('').
    """
    i = 0
    n = len(values_section)
    while i < n:
        # Find next '(' that starts a tuple
        while i < n and values_section[i] != "(":
            i += 1
        if i >= n:
            break
        depth = 0
        in_sq = False
        j = i
        while j < n:
            ch = values_section[j]
            if in_sq:
                if ch == "'":
                    # could be escaped '' -> stay in string
                    if j + 1 < n and values_section[j + 1] == "'":
                        j += 2
                        continue
                    else:
                        in_sq = False
                j += 1
                continue
            else:
                if ch == "'":
                    in_sq = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        # tuple ends at j
                        raw = values_section[i + 1: j]
                        yield raw.strip()
                        i = j + 1
                        break
                j += 1
        else:
            break


def split_fields(tuple_text: str) -> List[str]:
    """Split top-level comma-separated fields in the tuple text.

    Handles single-quoted SQL strings and escaped quotes.
    """
    fields: List[str] = []
    i = 0
    n = len(tuple_text)
    start = 0
    in_sq = False
    depth = 0
    while i < n:
        ch = tuple_text[i]
        if in_sq:
            if ch == "'":
                if i + 1 < n and tuple_text[i + 1] == "'":
                    i += 2
                    continue
                in_sq = False
            i += 1
            continue
        else:
            if ch == "'":
                in_sq = True
                i += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth > 0:
                    depth -= 1
            elif ch == "," and depth == 0:
                fields.append(tuple_text[start:i].strip())
                start = i + 1
            i += 1
    # last field
    last = tuple_text[start:].strip()
    if last:
        fields.append(last)
    return fields


def unquote_sql(val: str) -> Optional[str]:
    if val is None:
        return None
    sval = val.strip()
    if sval.upper() == "NULL" or sval == "":
        return None
    if sval.startswith("'") and sval.endswith("'"):
        # unescape '' -> '\''
        inner = sval[1:-1].replace("''", "'")
        return inner
    # sometimes values are provided without quotes (numbers, booleans)
    return sval


def to_snake(s: str) -> str:
    s = s or ""
    s = s.strip()
    # remove common trailing artifacts
    s = re.sub(r"(\.{2,}|\?|\"|\'|\,)$", "", s)
    # replace punctuation with space
    s = re.sub(r"[\-–—\\/\\\\\.:;\(\)\[\]{}\"]+", " ", s)
    # replace non-alnum with space
    s = re.sub(r"[^0-9a-zA-Z]+", " ", s)
    s = s.strip().lower()
    parts = [p for p in re.split(r"\s+", s) if p]
    slug = "_".join(parts)
    # collapse multiple underscores
    slug = re.sub(r"_+", "_", slug)
    # trim to sensible length
    return slug[:120]


STOPWORDS = set([
    "the",
    "and",
    "or",
    "of",
    "in",
    "on",
    "a",
    "an",
    "to",
    "with",
    "that",
    "this",
    "is",
    "it",
    "as",
    "for",
    "be",
    "are",
])


def generate_triggers(name: Optional[str], description: Optional[str], existing: List[str]) -> List[str]:
    """Heuristic triggers from name + description.

    Simple tokenization + frequency, excluding short words and a small stoplist.
    """
    tokens: List[str] = []
    if existing:
        tokens.extend(existing)
    text = " ".join([p for p in [name or "", description or ""] if p])
    # collapse punctuation
    text = re.sub(r"[^0-9A-Za-z ]+", " ", text).lower()
    for w in text.split():
        w = w.strip()
        if not w or len(w) < 3:
            continue
        if w in STOPWORDS:
            continue
        tokens.append(w)
    # frequency
    freq: Dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    # sort by frequency then length
    items = sorted(freq.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0]))
    picks = [k for k, _ in items]
    # prefer unique, up to 6 triggers
    seen = set()
    out: List[str] = []
    for p in picks:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
        if len(out) >= 6:
            break
    return out


def normalize_triggers(trig_raw: Optional[str]) -> List[str]:
    if not trig_raw:
        return []
    # Some triggers may be semi/colon delimited or comma separated. We'll split on common separators
    parts = re.split(r"[;|,\/\\]+", trig_raw)
    cleaned = []
    for p in parts:
        p = p.strip().lower()
        if not p:
            continue
        # remove punctuation
        p = re.sub(r"[^0-9a-z ]+", " ", p)
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            cleaned.append(p)
    return cleaned


def fix_mojibake(text: Optional[str]) -> Optional[str]:
    if not text:
        return text
    # Quick replacements for common mojibake sequences seen in exports
    replacements = {
        "â€”": "—",
        "â€“": "–",
        "â€œ": "“",
        "â€": "”",
        "â€": "",
        "Ã©": "é",
        "Ã¨": "è",
        "Ã¢": "â",
        "Ã¶": "ö",
        "Ã£": "ã",
        "Ã±": "ñ",
        "Ã¼": "ü",
        "ðŸ’¡": "💥",
    }
    s = text
    for k, v in replacements.items():
        s = s.replace(k, v)
    # Attempt a recover-by-decoding heuristic if still odd: try latin1->utf-8
    try:
        repaired = s.encode('latin1').decode('utf-8')
        # only replace if it looks better (contains more unicode categories)
        if any(ord(c) > 127 for c in repaired):
            s = repaired
    except Exception:
        pass
    # Normalize Unicode canonical composition
    s = unicodedata.normalize('NFC', s)
    # strip control characters
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]+", " ", s)
    return s.strip()


GENERIC_TRIGGERS = set(["you", "your", "new", "what", "when", "this", "that",
                       "they", "we", "is", "are", "will", "it", "here", "there", "not", "the"])

# Extend generic trigger set for fragment penalties
GENERIC_TRIGGERS.update({"being", "let", "wor", "ag"})


def refine_triggers(triggers: List[str]) -> List[str]:
    out = []
    for t in triggers:
        tt = t.strip().lower()
        if not tt:
            continue
        if tt in GENERIC_TRIGGERS:
            continue
        # drop fragments like 'wor' or 'proto' unless meaningful
        if len(tt) < 4:
            # allow some short emotional tokens
            if tt in {"ache", "ache", "grief", "rage", "awe", "joy", "love"}:
                pass
            else:
                continue
        out.append(tt)
    # unique preserving order
    seen = set()
    uniq = []
    for v in out:
        if v in seen:
            continue
        seen.add(v)
        uniq.append(v)
    return uniq


def infer_response_layer(description: Optional[str], emotional_tone: Optional[str]) -> Optional[str]:
    if description and re.search(r"\b(boundary|shield|surrender|defend|defense|protect|protects)\b", description, flags=re.I):
        return "grounding"
    if description and re.search(r"\b(repair|reconnection|reconnect|outreach|reach|invite)\b", description, flags=re.I):
        return "outreach"
    if description and re.search(r"\b(longing|ache|grief|mourning|insight|reflection|stillness|quiet)\b", description, flags=re.I):
        return "inner_reflection"
    # fallback: if emotional_tone mentions Gate, leave None (don't infer)
    if emotional_tone and re.search(r"gate", emotional_tone, flags=re.I):
        return None
    return None


def rehydrate_name_from_description(name: Optional[str], description: Optional[str]) -> Optional[str]:
    """If the name appears truncated or too short, try to build a sensible name from the description.

    This is conservative: only replaces when name is clearly missing/ellipsed or very short.
    """
    if description is None:
        return name
    nm = (name or "").strip()
    desc = description.strip()
    # heuristics: name endswith ellipsis or contains '...' or is very short
    if nm and not (nm.endswith("...") or nm.endswith("..") or nm.endswith(".") or len(nm) < 4):
        return nm
    # take first 3-6 words from description, capitalized
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’-]+", desc)
    if not words:
        return nm or None
    take = min(6, max(3, len(words)))
    head = words[:take]
    candidate = " ".join(head)
    # trim trailing partial word markers
    candidate = re.sub(r"\s+[a-zA-Z]$", "", candidate)
    # if candidate equals name or is empty, keep original
    if not candidate:
        return nm or None
    # Title case but preserve intentional lowercasing if present
    return candidate.strip()


GLYPH_TYPE_KEYWORDS = {
    "shield": "shielding",
    "shields": "shielding",
    "shielding": "shielding",
    "collapse": "collapse",
    "breakdown": "collapse",
    "break": "collapse",
    "recognition": "recognition",
    "recognise": "recognition",
    "insight": "recognition",
    "surrender": "surrender",
    "let go": "surrender",
    "repair": "repair",
    "reconnect": "repair",
}


EMOTIONAL_TONE_KEYWORDS = {
    "grief": "grief",
    "mourning": "grief",
    "ache": "longing",
    "longing": "longing",
    "rage": "rage",
    "awe": "awe",
    "wonder": "awe",
    "clarity": "clarity",
    "recognition": "recognition",
    "rupture": "rupture",
    "joy": "joy",
}


def infer_glyph_type(name: Optional[str], description: Optional[str], existing: Optional[str]) -> Optional[str]:
    if existing:
        return existing
    text = " ".join([p for p in [name or "", description or ""] if p]).lower()
    for k, v in GLYPH_TYPE_KEYWORDS.items():
        if re.search(r"\b" + re.escape(k) + r"\b", text):
            return v
    return None


def infer_emotional_tone(description: Optional[str], triggers: List[str], existing: Optional[str]) -> Optional[str]:
    if existing:
        # don't override a present value
        return existing
    text = " ".join([description or ""] + (triggers or [])).lower()
    for k, v in EMOTIONAL_TONE_KEYWORDS.items():
        if re.search(r"\b" + re.escape(k) + r"\b", text):
            return v
    return None


def compute_integrity_score(cleaned_obj: Dict[str, Any], triggers: List[str]) -> float:
    """Compute a heuristic integrity score in [0,1]. Lower values indicate likely fragments.

    Components:
      - name quality (0-1)
      - description quality (0-1)
      - triggers quality (0-1)
      - metadata completeness (0-1)
    Weighted sum returned.
    """
    name = (cleaned_obj.get("name") or "")
    desc = (cleaned_obj.get("description") or "")
    symbolic = cleaned_obj.get("symbolic_pairing")
    resp = cleaned_obj.get("response_layer")
    gtype = cleaned_obj.get("glyph_type")
    etone = cleaned_obj.get("emotional_tone")

    # name score
    if not name:
        name_score = 0.0
    else:
        # penalize ellipses/truncation
        if re.search(r"\.\.\.|\.\.\s*$", name) or len(name.strip()) < 4:
            name_score = 0.05
        else:
            name_score = min(len(name) / 40.0, 1.0)

    # description score (penalize extremely short or clearly truncated descriptions)
    dlen = len(desc.strip())
    if dlen == 0:
        desc_score = 0.0
    elif dlen < 20:
        desc_score = 0.1
    elif dlen < 80:
        desc_score = 0.6
    else:
        desc_score = 1.0

    # triggers score: count refined meaningful triggers and penalize generic-heavy sets
    refined = refine_triggers(triggers or [])
    meaningful = len(refined)
    # count generic tokens present
    generic_count = 0
    for t in (triggers or []) + refined:
        tt = (t or "").strip().lower()
        if tt in GENERIC_TRIGGERS:
            generic_count += 1
    # penalize when many generic tokens exist
    if generic_count > 2:
        trig_score = max(0.0, min(1.0, (meaningful / 4.0) - 0.5))
    else:
        trig_score = min(meaningful / 4.0, 1.0)

    # metadata completeness
    meta_count = 0
    meta_count += 1 if symbolic else 0
    meta_count += 1 if resp else 0
    meta_count += 1 if gtype else 0
    # emotional tone is considered invalid if it looks like 'Gate' or numeric
    if etone and re.search(r"gate|^\d+|gate\s*\d", str(etone), flags=re.I):
        etone_valid = 0
    else:
        etone_valid = 1 if etone else 0
    meta_count += etone_valid
    meta_score = meta_count / 4.0

    # weights
    score = (0.3 * name_score) + (0.3 * desc_score) + \
        (0.2 * trig_score) + (0.2 * meta_score)
    return float(max(0.0, min(1.0, score)))


def clamp_depth(value: Optional[str]) -> int:
    if value is None:
        return 3
    v = value.strip()
    try:
        di = int(v)
        if di < 1:
            return 1
        if di > 5:
            return 5
        return di
    except Exception:
        return 3


def parse_sql_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    values = find_values_section(sql)
    rows: List[Dict[str, Any]] = []
    for tup in iter_tuples(values):
        fields = split_fields(tup)
        if len(fields) != len(SQL_COLS):
            # attempt best-effort: pad or trim
            # print a debug warning
            print(
                f"Warning: tuple had {len(fields)} fields, expected {len(SQL_COLS)}. Skipping tuple prefix: {tup[:80]!r}")
            continue
        obj: Dict[str, Any] = {}
        for col, raw in zip(SQL_COLS, fields):
            obj[col] = unquote_sql(raw)
        rows.append(obj)
    return rows


def merge_and_normalize(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int], List[Dict[str, Any]]]:
    groups: Dict[Tuple[Optional[str], str], List[Dict[str, Any]]] = {}
    for r in rows:
        user = r.get("user_id") or "__global__"
        name_raw = r.get("name") or ""
        slug = to_snake(name_raw)
        key = (user, slug)
        groups.setdefault(key, []).append(r)

    cleaned: List[Dict[str, Any]] = []
    stats = {"total_input": len(rows), "groups": len(
        groups), "merged": 0, "null_name": 0, "null_description": 0}
    fragments: List[Dict[str, Any]] = []
    for (user, slug), items in groups.items():
        if len(items) > 1:
            stats["merged"] += len(items) - 1
        # pick the item with the longest non-empty description
        best = max(items, key=lambda it: len((it.get("description") or "")))
        # raw values
        name_raw = best.get("name")
        desc_raw = best.get("description")
        triggers = best.get("triggers")
        resp = best.get("response_layer")
        depth_raw = best.get("depth")
        emotional_tone = best.get("emotional_tone")

        # apply mojibake fixes
        name_norm = fix_mojibake(name_raw) if name_raw else (name_raw or "")
        desc = fix_mojibake(desc_raw) if desc_raw else desc_raw

        if not name_norm:
            stats["null_name"] += 1
        if not desc:
            stats["null_description"] += 1

        # rehydrate truncated names conservatively
        name_rehydrated = rehydrate_name_from_description(name_norm, desc)
        final_name = name_rehydrated or (
            name_norm.strip() if name_norm else None)
        # create slug from final name where possible
        slug = to_snake(final_name or slug)

        triggers_list = normalize_triggers(triggers)
        # prefer existing response_layer, otherwise infer
        response_layer = resp or infer_response_layer(desc, emotional_tone)
        depth = clamp_depth(depth_raw)

        # prefer existing triggers list (if parse returned a JSON-like list) or generate heuristics
        parsed_existing_triggers: List[str] = []
        try:
            if triggers:
                # if triggers look like a JSON array string, attempt parse
                if isinstance(triggers, str) and triggers.strip().startswith("["):
                    parsed_existing_triggers = json.loads(triggers)
                elif isinstance(triggers, list):
                    parsed_existing_triggers = triggers
                elif isinstance(triggers, str):
                    # fallback: split by common separators
                    parsed_existing_triggers = normalize_triggers(triggers)
        except Exception:
            parsed_existing_triggers = normalize_triggers(triggers)

        heur_triggers = generate_triggers(
            final_name, desc, parsed_existing_triggers)
        # refine triggers to drop generic/noisy tokens
        heur_triggers = refine_triggers(heur_triggers)

        # attempt to infer missing semantic fields conservatively
        inferred_glyph_type = infer_glyph_type(
            final_name, desc, best.get("glyph_type"))
        inferred_emotional_tone = infer_emotional_tone(
            desc, heur_triggers, best.get("emotional_tone"))

        cleaned_obj = {
            "id": best.get("id") or str(uuid.uuid4()),
            "name": final_name.strip() if final_name else None,
            "slug": slug or None,
            "description": desc.strip() if desc else None,
            "triggers": heur_triggers,
            "response_layer": response_layer,
            "depth": depth,
            # backfill last_updated if missing to current UTC for traceability
            "last_updated": best.get("last_updated") or datetime.utcnow().isoformat() + "Z",
            "symbolic_pairing": best.get("symbolic_pairing"),
            "user_id": best.get("user_id"),
            # default created_from_chat to False unless explicitly true
            "created_from_chat": True if (str(best.get("created_from_chat") or "").lower() == "true") else False,
            "source_message": best.get("source_message"),
            "emotional_tone": inferred_emotional_tone,
            "glyph_type": inferred_glyph_type,
            "tenant_id": best.get("tenant_id"),
        }

        # compute integrity score and flag fragments (threshold raised to 0.5 per rubric)
        score = compute_integrity_score(cleaned_obj, heur_triggers)
        cleaned_obj["integrity_score"] = score
        if score < 0.5:
            # tag as fragment candidate (score < 0.5 = candidate for review)
            cleaned_obj["fragment_flag"] = True
            # don't clobber an existing emotional tone if it looks meaningful, otherwise mark discard_candidate
            if not cleaned_obj.get("emotional_tone") or re.search(r"gate|^\d+", str(cleaned_obj.get("emotional_tone") or ""), flags=re.I):
                cleaned_obj["emotional_tone"] = cleaned_obj.get(
                    "emotional_tone") or "discard_candidate"
            cleaned_obj["glyph_type"] = cleaned_obj.get(
                "glyph_type") or "fragment"
            fragments.append(cleaned_obj.copy())
        else:
            cleaned_obj["fragment_flag"] = False

        cleaned.append(cleaned_obj)

    stats["total_cleaned"] = len(cleaned)
    return cleaned, stats, fragments


def write_outputs(cleaned: List[Dict[str, Any]], out_json: str, out_csv: str, report_md: str, sample_n: int = 20, fragments: Optional[List[Dict[str, Any]]] = None):
    os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    # write CSV
    fieldnames = [
        "id",
        "name",
        "slug",
        "description",
        "triggers",
        "response_layer",
        "depth",
        "symbolic_pairing",
        "user_id",
        "created_from_chat",
        "source_message",
        "emotional_tone",
        "glyph_type",
        "tenant_id",
        "last_updated",
    ]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in cleaned:
            row = {k: r.get(k) for k in fieldnames}
            # convert triggers list to JSON string
            row["triggers"] = json.dumps(row.get("triggers") or [])
            writer.writerow(row)

    # report
    with open(report_md, "w", encoding="utf-8") as f:
        f.write(f"# Glyphs Cleanup Report\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()} UTC\n\n")
        f.write(f"Total cleaned rows: {len(cleaned)}\n\n")
        if fragments:
            f.write(f"Total fragment candidates: {len(fragments)}\n\n")
        f.write("## Sample rows\n\n")
        for r in cleaned[:sample_n]:
            f.write("- ID: ``" + (r.get("id") or "") + "``\n")
            f.write("  - name: " + (r.get("name") or "<null>") + "\n")
            f.write("  - slug: " + (r.get("slug") or "<null>") + "\n")
            f.write("  - description: " + (r.get("description")
                    or "<null>")[:200].replace("\n", " ") + "\n")
            f.write("  - triggers: " +
                    json.dumps(r.get("triggers") or []) + "\n\n")
    # write fragments file if any
    if fragments is not None:
        frag_path = os.path.join(os.path.dirname(
            out_json) or ".", "fragments_to_review.json")
        with open(frag_path, "w", encoding="utf-8") as ff:
            json.dump(fragments, ff, indent=2, ensure_ascii=False)
        # Also produce a CSV summary for quick review (lowest integrity first)
        try:
            csv_path = os.path.join(os.path.dirname(
                out_json) or ".", "fragments_review.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as cf:
                fieldnames = ["id", "name", "slug",
                              "integrity_score", "description_short", "triggers"]
                writer = csv.DictWriter(cf, fieldnames=fieldnames)
                writer.writeheader()
                # sort fragments ascending by integrity_score
                frag_sorted = sorted(
                    fragments, key=lambda x: x.get("integrity_score", 0.0))
                for f in frag_sorted:
                    writer.writerow({
                        "id": f.get("id"),
                        "name": f.get("name"),
                        "slug": f.get("slug"),
                        "integrity_score": f.get("integrity_score"),
                        "description_short": (f.get("description") or "")[:200].replace("\n", " "),
                        "triggers": json.dumps(f.get("triggers") or [])
                    })
        except Exception:
            # best-effort: if CSV can't be written, continue
            pass
        # Produce a lowest-integrity sample CSV (bottom N), irrespective of fragment threshold
        try:
            sample_n = 50
            sample_path = os.path.join(os.path.dirname(
                out_json) or ".", "lowest_integrity_sample.csv")
            with open(sample_path, "w", encoding="utf-8", newline="") as sf:
                sfieldnames = ["id", "name", "slug",
                               "integrity_score", "description_short", "triggers"]
                sw = csv.DictWriter(sf, fieldnames=sfieldnames)
                sw.writeheader()
                # sort cleaned rows ascending by integrity score
                cleaned_sorted = sorted(
                    cleaned, key=lambda x: x.get("integrity_score", 1.0))
                for f in cleaned_sorted[:sample_n]:
                    sw.writerow({
                        "id": f.get("id"),
                        "name": f.get("name"),
                        "slug": f.get("slug"),
                        "integrity_score": f.get("integrity_score"),
                        "description_short": (f.get("description") or "")[:200].replace("\n", " "),
                        "triggers": json.dumps(f.get("triggers") or [])
                    })
        except Exception:
            pass


def main(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(
        description="Cleanup glyphs SQL export and produce normalized preview artifacts")
    p.add_argument("--source", default="glyphs_rows.sql",
                   help="Path to SQL file containing INSERT INTO glyphs ... VALUES (...)")
    p.add_argument("--out-json", default="dev_tools/cleaned_glyphs.json")
    p.add_argument("--out-csv", default="dev_tools/cleaned_glyphs_upsert.csv")
    p.add_argument("--report-md", default="dev_tools/cleanup_report.md")
    p.add_argument("--dry-run", dest="dry_run",
                   action="store_true", default=True)
    p.add_argument("--no-dry-run", dest="dry_run", action="store_false",
                   help="Allow writes to Supabase (not implemented in this script)")
    p.add_argument("--sample", type=int, default=20,
                   help="Number of sample cleaned rows to include in report")
    args = p.parse_args(argv)

    if not os.path.exists(args.source):
        print(f"Source file not found: {args.source}")
        sys.exit(1)

    print(f"Parsing SQL file: {args.source}")
    rows = parse_sql_file(args.source)
    print(f"Parsed {len(rows)} input rows")
    cleaned, stats, fragments = merge_and_normalize(rows)
    print(
        f"Produced {len(cleaned)} cleaned rows (merged groups: {stats.get('merged')})")

    write_outputs(cleaned, args.out_json, args.out_csv,
                  args.report_md, sample_n=args.sample, fragments=fragments)

    print("Wrote:")
    print(f" - JSON: {args.out_json}")
    print(f" - CSV:  {args.out_csv}")
    print(f" - Report: {args.report_md}")
    print("Dry-run mode: no Supabase writes were performed.")


if __name__ == '__main__':
    main()
