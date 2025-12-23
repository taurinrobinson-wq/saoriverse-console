#!/usr/bin/env python3
"""
tools/clean_glyph_db.py

Utility to detect and optionally archive/remove noisy/artifact rows from the
`glyph_lexicon` table in the glyphs DB. Defaults to dry-run (no destructive
changes). Use --apply to move flagged rows into an archival table
`glyph_lexicon_archived` and delete them from `glyph_lexicon`.

Heuristics used to flag rows:
- glyph_name length > 60
- description length > 1000
- description contains many newlines (>6)
- glyph_name or description contains '[DEPRECATED]' or 'deprecated'
- glyph_name contains '[' or '\t' (likely table fragments)
- glyph_name or description with high ratio of non-alphanumeric characters

Run examples:
  python3 tools/clean_glyph_db.py --db emotional_os/glyphs/glyphs.db --dry-run
  python3 tools/clean_glyph_db.py --db emotional_os/glyphs/glyphs.db --apply

"""
import argparse
import json
import os
import re
import sqlite3
from datetime import datetime, timezone


def high_non_alnum_ratio(s: str, threshold: float = 0.25) -> bool:
    if not s:
        return False
    total = len(s)
    non_alnum = len(re.findall(r"[^A-Za-z0-9\s\-',:.()\\n]", s))
    return (non_alnum / max(1, total)) >= threshold


def flag_row(row: sqlite3.Row) -> bool:
    # row is a sequence: (rowid, glyph_name, description, gate)
    name = row[1] or ""
    desc = row[2] or ""

    if not isinstance(name, str):
        return True
    if (
        "[DEPRECATED]" in name.upper()
        or "DEPRECATED" in desc.upper()
        or "deprecated" in name.lower()
        or "deprecated" in desc.lower()
    ):
        return True
    if len(name) > 60:
        return True
    if len(desc) > 1000:
        return True
    if desc.count("\n") > 6:
        return True
    if "[" in name or "\t" in name:
        return True
    if high_non_alnum_ratio(name, 0.20) or high_non_alnum_ratio(desc, 0.20):
        return True
    # bracketed index patterns like [1], (1) in name
    if re.search(r"\[\d+\]", name) or re.search(r"\(\d+\)", name):
        return True
    # otherwise, don't flag
    return False


def discover_candidates(db_path: str, limit: int = None):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DB not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT rowid, glyph_name, description, gate FROM glyph_lexicon")
    rows = cursor.fetchall()

    candidates = []
    for r in rows:
        if flag_row(r):
            # r: (rowid, glyph_name, description, gate)
            candidates.append(
                {"rowid": r[0], "glyph_name": r[1], "gate": r[3], "description_snippet": (r[2] or "")[:200]}
            )
            if limit and len(candidates) >= limit:
                break

    conn.close()
    return candidates


def archive_and_remove(db_path: str, rowids: list):
    if not rowids:
        return {"archived": 0, "deleted": 0}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create archival table if not exists (simple schema)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS glyph_lexicon_archived (
            orig_rowid INTEGER,
            glyph_name TEXT,
            description TEXT,
            gate TEXT,
            archived_at TEXT
        )
        """
    )
    conn.commit()

    archived = 0
    deleted = 0
    for rid in rowids:
        try:
            cursor.execute("SELECT glyph_name, description, gate FROM glyph_lexicon WHERE rowid = ?", (rid,))
            row = cursor.fetchone()
            if not row:
                continue
            cursor.execute(
                "INSERT INTO glyph_lexicon_archived (orig_rowid, glyph_name, description, gate, archived_at) VALUES (?, ?, ?, ?, ?)",
                (rid, row[0], row[1], row[2], datetime.now(timezone.utc).isoformat()),
            )
            cursor.execute("DELETE FROM glyph_lexicon WHERE rowid = ?", (rid,))
            archived += 1
            deleted += 1
        except Exception as e:
            print(f"Error archiving row {rid}: {e}")
            conn.rollback()
    conn.commit()
    conn.close()
    return {"archived": archived, "deleted": deleted}


def main():
    parser = argparse.ArgumentParser(description="Clean noisy rows from glyph_lexicon")
    parser.add_argument("--db", "--db-path", dest="db_path", required=True, help="Path to glyphs DB")
    parser.add_argument(
        "--dry-run", dest="dry_run", action="store_true", default=True, help="Only list candidates (default)"
    )
    parser.add_argument("--apply", dest="apply", action="store_true", help="Apply archival + deletion (destructive)")
    parser.add_argument("--limit", dest="limit", type=int, default=200, help="Limit number of candidates to show/apply")

    args = parser.parse_args()

    if args.apply:
        print("Running in APPLY mode: flagged rows will be moved to archival table and deleted from glyph_lexicon.")
    else:
        print("Running in DRY-RUN mode: no changes will be made. Use --apply to remove flagged rows.")

    candidates = discover_candidates(args.db_path, limit=args.limit)
    total = len(candidates)
    print(f"Found {total} flagged rows (limit={args.limit}).")
    if total == 0:
        return

    # Print a compact sample
    sample = candidates[:20]
    print(json.dumps(sample, indent=2, ensure_ascii=False))

    if args.apply:
        rowids = [c["rowid"] for c in candidates]
        result = archive_and_remove(args.db_path, rowids)
        print(f"Archived {result['archived']} rows and deleted {result['deleted']} rows.")
    else:
        print(
            "Dry-run complete. To remove these rows, run with --apply. Recommended: run a small apply first (limit) to confirm results."
        )


if __name__ == "__main__":
    main()
