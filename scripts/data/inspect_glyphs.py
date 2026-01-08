#!/usr/bin/env python3
import os
import sqlite3
import sys


def inspect_db(path):
    print("\nInspecting DB:", path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','index') ORDER BY type, name")
    items = cur.fetchall()
    print("Tables/Indexes:")
    for name, typ in items:
        print(" -", typ, name)

    names = [r[0] for r in items]
    if "glyph_lexicon" not in names:
        print("\nNo table named glyph_lexicon found in this DB. Listing top tables and counts:")
        for name, typ in items:
            if typ == "table":
                try:
                    cur.execute(f'SELECT COUNT(*) FROM "{name}"')
                    cnt = cur.fetchone()[0]
                    print(f"  - {name}: {cnt} rows")
                except Exception as e:
                    print("  -", name, "COUNT failed:", e)
        conn.close()
        return

    try:
        cur.execute("SELECT COUNT(*) FROM glyph_lexicon")
        total = cur.fetchone()[0]
        print("\nglyph_lexicon total rows:", total)
    except Exception as e:
        print("Failed to count glyph_lexicon:", e)
        conn.close()
        return

    # Heuristic scans
    long_desc = 0
    many_newlines = 0
    artifact_markers = 0
    dup_map = {}
    long_samples = []
    newline_samples = []
    artifact_samples = []

    markers = [
        "markdown export",
        "json export",
        "archive",
        "gutenberg",
        "conversation archive",
        "markdown",
        "json",
        "export",
        "file:",
        "http://",
        "https://",
        "<html",
        "```",
        "title:",
    ]

    cur.execute("SELECT rowid, glyph_name, description FROM glyph_lexicon")
    for i, row in enumerate(cur):
        rowid, name, desc = row[0], row[1] or "", row[2] or ""
        lname = (name or "").lower()
        ldesc = (desc or "").lower()
        if len(ldesc) > 800:
            long_desc += 1
            if len(long_samples) < 10:
                long_samples.append((rowid, name, len(ldesc)))
        nl_count = desc.count("\n")
        if nl_count > 8:
            many_newlines += 1
            if len(newline_samples) < 10:
                newline_samples.append((rowid, name, nl_count))
        if any(m in lname or m in ldesc for m in markers):
            artifact_markers += 1
            if len(artifact_samples) < 10:
                artifact_samples.append((rowid, name, [m for m in markers if m in lname or m in ldesc]))
        key = (name or "").strip()
        if key:
            dup_map[key] = dup_map.get(key, 0) + 1

    dups = [(k, v) for k, v in dup_map.items() if v > 1]
    print("\nHeuristic counts:")
    print(" - long descriptions (>800 chars):", long_desc)
    print(" - many newlines (>8):", many_newlines)
    print(" - artifact marker matches:", artifact_markers)
    print(" - duplicate glyph_name count:", len(dups))

    print("\nSample long descriptions (rowid, name, length):")
    for s in long_samples:
        print(" -", s)
    print("\nSample many-newlines (rowid, name, newline_count):")
    for s in newline_samples:
        print(" -", s)
    print("\nSample artifact matches (rowid, name, markers):")
    for s in artifact_samples:
        print(" -", s)

    if dups:
        dups_sorted = sorted(dups, key=lambda x: x[1], reverse=True)[:10]
        print("\nTop duplicate glyph_name examples:")
        for k, v in dups_sorted:
            print(" -", v, "x", (k[:80] if k else "<empty>"))

    conn.close()


if __name__ == "__main__":
    dbpath = "archive/full_backups/restore_glyphs_20251120T014253Z.db"
    if len(sys.argv) > 1:
        dbpath = sys.argv[1]
    if not os.path.exists(dbpath):
        print("DB not found:", dbpath)
        sys.exit(2)
    inspect_db(dbpath)
