#!/usr/bin/env python3
"""
Less-Aggressive Glyph Consolidation Script

- Scans `emotional_os/glyphs/glyphs.db` glyph_lexicon records
- Computes text similarity (name + description) using difflib
- Auto-merges pairs with very-high similarity (>= 0.95)
  - Creates merged record combining activation_signals, choosing gate conservatively
  - Records lineage mapping in JSON and a SQL file
- Marks candidate merges with moderate similarity (>= 0.75 and < 0.95)
  - Writes candidates to JSON for manual review
- Does not delete originals. Marks deprecated entries if applying merges.

Usage:
  python consolidation_less_aggressive.py --preview    # produce JSON reports, no DB changes
  python consolidation_less_aggressive.py --apply-auto # apply only very-high-similarity automatic merges

Outputs:
  - emotional_os/deploy/consolidation_reports/auto_merges.json
  - emotional_os/deploy/consolidation_reports/candidates.json
  - emotional_os/deploy/consolidation_reports/apply_auto.sql  (if --apply-auto)

"""

import argparse
import json
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Tuple

DB_PATH = "emotional_os/glyphs/glyphs.db"
REPORT_DIR = Path("emotional_os/deploy/consolidation_reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

AUTO_MERGE_THRESHOLD = 0.95
CANDIDATE_THRESHOLD = 0.75


def similarity(a: str, b: str) -> float:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def load_glyphs(db_path: str) -> List[Dict]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Use rowid to safely identify records even if no explicit id column
    cursor.execute("SELECT rowid, voltage_pair, glyph_name, description, gate, activation_signals FROM glyph_lexicon")
    rows = cursor.fetchall()
    conn.close()

    glyphs = []
    for row in rows:
        rowid, voltage_pair, glyph_name, description, gate, activation_signals = row
        glyphs.append(
            {
                "rowid": rowid,
                "voltage_pair": voltage_pair or "",
                "name": glyph_name or "",
                "description": description or "",
                "gate": gate or "",
                "activation_signals": (activation_signals or "").split(",") if activation_signals else [],
            }
        )
    return glyphs


def find_similar_pairs(glyphs: List[Dict]) -> List[Tuple[Dict, Dict, float]]:
    pairs = []
    n = len(glyphs)
    for i in range(n):
        g1 = glyphs[i]
        text1 = (g1["name"] + "\n" + (g1["description"] or "")).strip()
        for j in range(i + 1, n):
            g2 = glyphs[j]
            text2 = (g2["name"] + "\n" + (g2["description"] or "")).strip()
            score = similarity(text1, text2)
            if score >= CANDIDATE_THRESHOLD:
                pairs.append((g1, g2, round(score, 4)))
    # Sort descending by score
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs


def choose_canonical_name(g1: Dict, g2: Dict) -> str:
    # Prefer shorter name that's not emoji-only, else the longer more descriptive
    def clean(n: str) -> str:
        return n.replace("\n", " ").strip()

    n1 = clean(g1["name"])
    n2 = clean(g2["name"])
    if not n1:
        return n2
    if not n2:
        return n1
    # If one contains punctuation and one is plain, prefer plain
    if len(n1) < len(n2) and len(n1) >= 5:
        return n1
    if len(n2) < len(n1) and len(n2) >= 5:
        return n2
    # fallback choose the more descriptive (longer)
    return n1 if len(n1) >= len(n2) else n2


def merge_activation_signals(a: List[str], b: List[str]) -> List[str]:
    s = set([x.strip() for x in (a or []) if x and x.strip()]) | set([x.strip() for x in (b or []) if x and x.strip()])
    return sorted([x for x in s if x])


def create_auto_merge_plan(pairs: List[Tuple[Dict, Dict, float]]) -> Tuple[List[Dict], List[Dict]]:
    auto_merges = []
    candidates = []

    used_rowids = set()

    for g1, g2, score in pairs:
        if g1["rowid"] in used_rowids or g2["rowid"] in used_rowids:
            continue  # avoid overlapping merges; conservative
        entry = {"left": g1, "right": g2, "score": score}
        if score >= AUTO_MERGE_THRESHOLD:
            # build merged glyph
            canonical_name = choose_canonical_name(g1, g2)
            merged_desc = None
            # prefer longer description if significantly longer
            d1 = (g1.get("description") or "").strip()
            d2 = (g2.get("description") or "").strip()
            if len(d1) > len(d2) * 1.1:
                merged_desc = d1
            elif len(d2) > len(d1) * 1.1:
                merged_desc = d2
            else:
                merged_desc = d1 if len(d1) >= len(d2) else d2

            merged_activation = merge_activation_signals(
                g1.get("activation_signals", []), g2.get("activation_signals", [])
            )
            # choose gate conservatively: prefer more specific gate (lower number mapping arbitrary); keep both if different
            gate = g1["gate"] if g1["gate"] == g2["gate"] else g1["gate"] + " | " + g2["gate"]

            merged = {
                "merged_name": canonical_name,
                "merged_description": merged_desc,
                "merged_activation_signals": merged_activation,
                "merged_gate": gate,
                "members": [g1["rowid"], g2["rowid"]],
                "member_details": [g1, g2],
                "score": score,
            }
            auto_merges.append(merged)
            used_rowids.add(g1["rowid"])
            used_rowids.add(g2["rowid"])
        else:
            # candidate for manual review
            candidates.append({"left": g1, "right": g2, "score": score})
    return auto_merges, candidates


def write_reports(auto_merges: List[Dict], candidates: List[Dict]):
    auto_path = REPORT_DIR / "auto_merges.json"
    cand_path = REPORT_DIR / "candidates.json"

    with open(auto_path, "w", encoding="utf-8") as f:
        json.dump(auto_merges, f, indent=2, ensure_ascii=False)

    with open(cand_path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)

    print(f"Wrote auto_merges: {auto_path}")
    print(f"Wrote candidates: {cand_path}")


def build_apply_sql(auto_merges: List[Dict]) -> str:
    """Generate SQL statements to add merged records and mark old ones deprecated.
    Strategy:
      - INSERT a new glyph_lexicon row with merged fields
      - INSERT into a mapping table (consolidation_map) that we will create if absent
      - UPDATE old rows to prefix their glyph_name with "[DEPRECATED] " and keep them

    NOTE: This SQL is conservative: does not delete originals.
    """
    statements = []
    statements.append("BEGIN TRANSACTION;")
    # Ensure consolidation_map table exists
    statements.append(
        "CREATE TABLE IF NOT EXISTS consolidation_map (merged_rowid INTEGER, original_rowid INTEGER, merged_name TEXT, created_at TEXT);"
    )

    for merged in auto_merges:
        name = merged["merged_name"].replace("'", "''")
        desc = (merged.get("merged_description") or "").replace("'", "''")
        gate = (merged.get("merged_gate") or "").replace("'", "''")
        activation = ",".join(merged.get("merged_activation_signals") or [])
        voltage_pair = ""
        # create conservative voltage_pair based on name hash
        vp = f"m-{abs(hash(name))%1000:03d}"
        sql_insert = f"INSERT INTO glyph_lexicon (voltage_pair, glyph_name, description, gate, activation_signals) VALUES ('{vp}', '{name}', '{desc}', '{gate}', '{activation}');"
        statements.append(sql_insert)
        # capture last_insert_rowid via a placeholder comment (user-run SQL should replace or run sequentially)
        statements.append(
            "-- After running the INSERT above, run the following for this merged entry with the real last_insert_rowid from the DB engine:"
        )
        # add mapping statements
        for orig in merged["members"]:
            statements.append(
                f"INSERT INTO consolidation_map (merged_rowid, original_rowid, merged_name, created_at) VALUES (last_insert_rowid(), {orig}, '{name}', datetime('now'));"
            )
            statements.append(
                f"UPDATE glyph_lexicon SET glyph_name = '[DEPRECATED] ' || glyph_name WHERE rowid = {orig};"
            )

    statements.append("COMMIT;")
    return "\n".join(statements)


def apply_auto_merges_to_db(db_path: str, auto_merges: List[Dict]):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure consolidation_map exists
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS consolidation_map (merged_rowid INTEGER, original_rowid INTEGER, merged_name TEXT, created_at TEXT)"
    )
    conn.commit()

    for merged in auto_merges:
        name = merged["merged_name"]
        desc = merged.get("merged_description") or ""
        gate = merged.get("merged_gate") or ""
        activation = ",".join(merged.get("merged_activation_signals") or [])
        vp = f"m-{abs(hash(name))%1000:03d}"

        cursor.execute(
            "INSERT INTO glyph_lexicon (voltage_pair, glyph_name, description, gate, activation_signals) VALUES (?, ?, ?, ?, ?)",
            (vp, name, desc, gate, activation),
        )
        merged_rowid = cursor.lastrowid
        for orig in merged["members"]:
            cursor.execute(
                "INSERT INTO consolidation_map (merged_rowid, original_rowid, merged_name, created_at) VALUES (?, ?, ?, datetime('now'))",
                (merged_rowid, orig, name),
            )
            cursor.execute(
                "UPDATE glyph_lexicon SET glyph_name = '[DEPRECATED] ' || glyph_name WHERE rowid = ?", (orig,)
            )

    conn.commit()
    conn.close()


def main(preview: bool = True, apply_auto: bool = False):
    glyphs = load_glyphs(DB_PATH)
    print(f"Loaded {len(glyphs)} glyphs from DB")

    pairs = find_similar_pairs(glyphs)
    print(f"Found {len(pairs)} similar pairs (score >= {CANDIDATE_THRESHOLD})")

    auto_merges, candidates = create_auto_merge_plan(pairs)
    print(f"Auto-merge candidates (score >= {AUTO_MERGE_THRESHOLD}): {len(auto_merges)}")
    print(f"Manual candidate pairs (score >= {CANDIDATE_THRESHOLD} and < {AUTO_MERGE_THRESHOLD}): {len(candidates)}")

    write_reports(auto_merges, candidates)

    sql_path = REPORT_DIR / "apply_auto.sql"
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(build_apply_sql(auto_merges))
    print(f"Wrote SQL plan for auto merges: {sql_path}")

    if apply_auto and auto_merges:
        print("Applying auto merges to DB now...")
        apply_auto_merges_to_db(DB_PATH, auto_merges)
        print("Applied auto merges to DB. Consolidation map updated.")
    else:
        if apply_auto:
            print("No auto merges to apply.")
        else:
            print("Preview mode: no DB changes made. Inspect the JSON reports in the consolidation_reports folder.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Less-aggressive glyph consolidation")
    parser.add_argument("--preview", action="store_true", help="Only produce JSON reports (default)")
    parser.add_argument("--apply-auto", action="store_true", help="Apply only very-high similarity merges to DB")
    args = parser.parse_args()

    if not args.preview and not args.apply_auto:
        args.preview = True

    main(preview=args.preview, apply_auto=args.apply_auto)
