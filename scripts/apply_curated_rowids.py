#!/usr/bin/env python3
"""Apply curated display_name and response_template to specific rowids in glyph_lexicon.

This script reads `scripts/output/curated_top20_glyphs.csv` and updates the three rowids
confirmed by the user: 62, 259, 49.

Run: python3 scripts/apply_curated_rowids.py
"""
import os
import sqlite3
import csv

ROOT = os.path.dirname(__file__)
DB_PATH = os.path.normpath(os.path.join(
    ROOT, '..', 'emotional_os', 'glyphs', 'glyphs.db'))
CSV_PATH = os.path.join(ROOT, 'output', 'curated_top20_glyphs.csv')

# Confirmed rowid -> display_name mapping (from user's confirmation)
ROWID_TO_DISPLAY = {
    62: "Resonance fragments without system...",
    259: "It entangles it — so that the ache is...",
    49: "That’s the quiet scream of coherence in...",
}


def load_csv(path):
    mapping = {}
    if not os.path.exists(path):
        return mapping
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            dn = (r.get('display_name') or '').strip()
            rt = (r.get('response_template') or '').strip()
            if dn:
                mapping[dn] = rt
    return mapping


def ensure_columns(conn, cur):
    cur.execute("PRAGMA table_info(glyph_lexicon)")
    cols = [r[1] for r in cur.fetchall()]
    changed = False
    if 'display_name' not in cols:
        cur.execute("ALTER TABLE glyph_lexicon ADD COLUMN display_name TEXT")
        changed = True
    if 'response_template' not in cols:
        cur.execute(
            "ALTER TABLE glyph_lexicon ADD COLUMN response_template TEXT")
        changed = True
    if changed:
        conn.commit()


def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    csv_map = load_csv(CSV_PATH)
    if not csv_map:
        print(f"Curated CSV not found or empty at {CSV_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    ensure_columns(conn, cur)

    applied = []
    skipped = []
    missing_display = []

    for rid, display in ROWID_TO_DISPLAY.items():
        # find response template for display_name in csv
        rt = csv_map.get(display)
        if rt is None:
            missing_display.append(display)
            continue
        cur.execute(
            "SELECT glyph_name, display_name FROM glyph_lexicon WHERE rowid = ?", (rid,))
        row = cur.fetchone()
        if not row:
            print(f"Rowid {rid} not found in glyph_lexicon")
            continue
        glyph_name, existing_display = row
        if existing_display and existing_display.strip():
            skipped.append((rid, glyph_name, existing_display))
            continue
        # apply update
        cur.execute("UPDATE glyph_lexicon SET display_name = ?, response_template = ? WHERE rowid = ?",
                    (display, rt, rid))
        conn.commit()
        applied.append((rid, glyph_name, display))

    print("\nApply summary:")
    print(f" Applied: {len(applied)}")
    for a in applied:
        print(f"  - rowid={a[0]} glyph_name='{a[1]}' -> display_name='{a[2]}'")
    print(f" Skipped (already had display_name): {len(skipped)}")
    for s in skipped:
        print(
            f"  - rowid={s[0]} glyph_name='{s[1]}' existing_display='{s[2]}'")
    if missing_display:
        print(
            f" Missing display_name entries not found in CSV: {len(missing_display)}")
        for m in missing_display:
            print(f"  - {m}")

    # Show full updated rows
    if applied:
        print('\nUpdated rows preview (full response_template):')
        for rid, _, _ in applied:
            cur.execute(
                "SELECT rowid, glyph_name, display_name, response_template FROM glyph_lexicon WHERE rowid = ?", (rid,))
            r = cur.fetchone()
            print(
                f" - rowid={r[0]} glyph_name='{r[1]}' display_name='{r[2]}'\n   template: {r[3]}\n")

    conn.close()


if __name__ == '__main__':
    main()
