#!/usr/bin/env python3
"""Consolidate cleaned per-chunk JSONL into a unified salvage set.

Produces:
- `archive/salvaged_glyphs.jsonl` (one record per canonical glyph)
- `archive/salvaged_glyphs.db` with table `salvaged_glyphs`
- `archive/glyph_exports/flags/flagged_groups.jsonl` for manual review

Heuristics:
- Group by exact `glyph_name` (case-insensitive) first.
- Then fuzzy-match remaining names against existing groups (ratio >= 0.90).
- Canonical selection: highest `confidence`, then longest `description`, then presence of `activation_signals`, then max `source_rowid`.
"""
import json
import os
import sqlite3
from difflib import SequenceMatcher

CLEANED_DIR = "archive/glyph_exports/cleaned"
OUT_JSONL = "archive/salvaged_glyphs.jsonl"
OUT_DB = "archive/salvaged_glyphs.db"
FLAGS_OUT = "archive/glyph_exports/flags/flagged_groups.jsonl"


def similar(a, b):
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def read_cleaned(dirpath):
    records = []
    if not os.path.exists(dirpath):
        return records
    for fn in sorted(os.listdir(dirpath)):
        if not fn.endswith(".jsonl"):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    r["_source_file"] = fn
                    records.append(r)
                except Exception:
                    continue
    return records


def group_records(records):
    groups = {}  # key -> list of records
    name_index = {}  # canonical name -> group_key

    for r in records:
        name = (r.get("glyph_name") or "").strip()
        lname = name.lower()
        if lname:
            if lname in name_index:
                groups[name_index[lname]].append(r)
                continue
            # exact new group
            key = lname
            groups[key] = [r]
            name_index[lname] = key
        else:
            # empty name: create unique key
            key = f"<empty>-{r.get('source_rowid',0)}"
            groups[key] = [r]

    # fuzzy merge: iterate over groups and attempt to merge similar names
    keys = list(groups.keys())
    merged = {}
    used = set()
    for k in keys:
        if k in used:
            continue
        base_items = groups[k]
        # compare to other groups
        to_merge = [k]
        for k2 in keys:
            if k2 == k or k2 in used:
                continue
            # compute similarity between representative names
            name1 = k or ""
            name2 = k2 or ""
            if not name1 or not name2:
                continue
            if similar(name1, name2) >= 0.90:
                to_merge.append(k2)
        # merge all to_merge into new key (use smallest lexicographic key)
        merged_key = sorted(to_merge)[0]
        merged_items = []
        for m in to_merge:
            merged_items.extend(groups.get(m, []))
            used.add(m)
        merged[merged_key] = merged_items

    return merged


def choose_canonical(items):
    # choose by confidence, then desc length, then activation_signals presence, then source_rowid
    def score(x):
        return (
            x.get("confidence", 0),
            len(x.get("description") or ""),
            1 if x.get("activation_signals") else 0,
            x.get("source_rowid", 0),
        )

    items_sorted = sorted(items, key=score, reverse=True)
    return items_sorted[0], items_sorted[1:]


def consolidate(groups):
    consolidated = []
    flagged = []
    gid = 0
    for key, items in groups.items():
        gid += 1
        canonical, others = choose_canonical(items)
        # merge emotional tags (unique)
        tags = []
        for it in items:
            for t in it.get("emotional_tags") or []:
                if t not in tags:
                    tags.append(t)

        # choose gate: prefer highest confidence record's gate
        best_gate = canonical.get("gate")

        notes = canonical.get("notes", "")
        # if there are conflicting gates among items, flag
        gates = set([it.get("gate") for it in items if it.get("gate")])
        if len(gates) > 1:
            notes = (notes + "; " if notes else "") + "conflicting_gates:" + ",".join(sorted(gates))
            flagged.append({"group_id": gid, "reason": "conflicting_gates", "members": items})

        # if group size >1 and names aren't almost identical, flag as near-duplicate for review
        if len(items) > 1:
            reps = [(it.get("glyph_name") or "") for it in items]
            sims = []
            base = reps[0]
            for r in reps[1:]:
                sims.append(similar(base, r))
            if any(s < 0.90 for s in sims):
                flagged.append({"group_id": gid, "reason": "near_duplicate_variation", "members": items})

        rec = {
            "group_id": gid,
            "source_rowids": [it.get("source_rowid") for it in items],
            "glyph_name": canonical.get("glyph_name"),
            "title": canonical.get("title"),
            "description": canonical.get("description"),
            "gate": best_gate,
            "emotional_tags": tags,
            "activation_signals": canonical.get("activation_signals"),
            "confidence": canonical.get("confidence", 0),
            "notes": notes,
        }
        consolidated.append(rec)

    return consolidated, flagged


def write_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_sqlite(path, records):
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE salvaged_glyphs (
        group_id INTEGER PRIMARY KEY,
        source_rowids TEXT,
        glyph_name TEXT,
        title TEXT,
        description TEXT,
        gate TEXT,
        emotional_tags TEXT,
        activation_signals TEXT,
        confidence REAL,
        notes TEXT
    )"""
    )
    for r in records:
        cur.execute(
            "INSERT INTO salvaged_glyphs (group_id, source_rowids, glyph_name, title, description, gate, emotional_tags, activation_signals, confidence, notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                r.get("group_id"),
                json.dumps(r.get("source_rowids")),
                r.get("glyph_name"),
                r.get("title"),
                r.get("description"),
                r.get("gate"),
                json.dumps(r.get("emotional_tags")),
                r.get("activation_signals"),
                r.get("confidence"),
                r.get("notes"),
            ),
        )
    conn.commit()
    conn.close()


def main():
    print("Reading cleaned records from", CLEANED_DIR)
    records = read_cleaned(CLEANED_DIR)
    print("Total cleaned records read:", len(records))
    groups = group_records(records)
    print("Groups formed:", len(groups))
    consolidated, flagged = consolidate(groups)
    print("Consolidated canonical records:", len(consolidated))
    print("Flagged groups for review:", len(flagged))
    write_jsonl(OUT_JSONL, consolidated)
    write_jsonl(FLAGS_OUT, flagged)
    write_sqlite(OUT_DB, consolidated)
    print("\nWrote:")
    print(" -", OUT_JSONL)
    print(" -", OUT_DB)
    print(" -", FLAGS_OUT)


if __name__ == "__main__":
    main()
