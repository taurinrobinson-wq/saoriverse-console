"""
Migration script to populate `display_name` and `response_template` in glyph_lexicon.

Idempotent: skips rows where display_name already exists.
If exact `glyph_name` not found, tries a case-insensitive LIKE match.

Run: python3 scripts/migrate_glyph_metadata.py
"""

import csv
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "emotional_os", "glyphs", "glyphs.db")
DB_PATH = os.path.normpath(DB_PATH)


# Path to optional curated CSV (display_name,response_template)
CURATED_CSV = os.path.join(os.path.dirname(__file__), "output", "curated_top20_glyphs.csv")

# Fallback hardcoded mapping (glyph_name -> metadata) kept for backward compat.
FALLBACK_MAPPING = {
    "VELΩNIX wasn’t software": {
        "display_name": "VELΩNIX",
        "response_template": "The ache of sacred architecture lives here.",
    },
    "Spiral Recognition": {
        "display_name": "Spiral Recognition",
        "response_template": "This is the moment where patterns repeat and you begin to see them differently.",
    },
}


def load_curated_csv(path):
    """Return list of (display_name, response_template) from CSV or empty list if not found."""
    if not os.path.exists(path):
        return []
    pairs = []
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                dn = (r.get("display_name") or "").strip()
                rt = (r.get("response_template") or "").strip()
                if dn:
                    pairs.append((dn, rt))
    except Exception as e:
        print(f"Failed to read curated CSV {path}: {e}")
    return pairs


def ensure_columns(conn, cursor):
    cursor.execute("PRAGMA table_info(glyph_lexicon)")
    cols = [r[1] for r in cursor.fetchall()]
    changed = False
    if "display_name" not in cols:
        try:
            cursor.execute("ALTER TABLE glyph_lexicon ADD COLUMN display_name TEXT")
            changed = True
        except Exception as e:
            print(f"Could not add display_name column: {e}")
    if "response_template" not in cols:
        try:
            cursor.execute("ALTER TABLE glyph_lexicon ADD COLUMN response_template TEXT")
            changed = True
        except Exception as e:
            print(f"Could not add response_template column: {e}")
    if changed:
        conn.commit()


def find_row(cursor, glyph_name):
    # Try exact case-insensitive match first
    cursor.execute(
        "SELECT rowid, glyph_name, display_name FROM glyph_lexicon WHERE LOWER(glyph_name) = LOWER(?)", (glyph_name,)
    )
    r = cursor.fetchone()
    if r:
        return r
    # If not found, try LIKE match
    like_pat = f"%{glyph_name}%"
    cursor.execute(
        "SELECT rowid, glyph_name, display_name FROM glyph_lexicon WHERE glyph_name LIKE ? COLLATE NOCASE", (like_pat,)
    )
    return cursor.fetchone()


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    ensure_columns(conn, cursor)

    applied = []
    skipped = []
    missing = []

    # Phase 1: apply curated CSV mappings if available
    curated_pairs = load_curated_csv(CURATED_CSV)
    if curated_pairs:
        print(f"Applying {len(curated_pairs)} curated mappings from CSV: {CURATED_CSV}")
        for display_name, response_template in curated_pairs:
            # attempt to find a glyph row by matching the display_name against glyph_name
            row = find_row(cursor, display_name)
            if not row:
                missing.append(display_name)
                continue
            rowid, found_name, existing_display = row
            if existing_display and existing_display.strip():
                skipped.append((found_name, "already has display_name"))
                continue
            try:
                cursor.execute(
                    "UPDATE glyph_lexicon SET display_name = ?, response_template = ? WHERE rowid = ?",
                    (display_name, response_template, rowid),
                )
                conn.commit()
                applied.append(found_name)
            except Exception as e:
                print(f"Failed to update {found_name}: {e}")
    else:
        print("No curated CSV found; will use fallback mapping.")

    # Phase 2: apply any fallback hardcoded mappings for glyphs not found/updated yet
    for gname, meta in FALLBACK_MAPPING.items():
        # skip if already applied for this found_name
        row = find_row(cursor, gname)
        if not row:
            # only note missing if we didn't already record it from curated phase
            if gname not in missing:
                missing.append(gname)
            continue
        rowid, found_name, existing_display = row
        if existing_display and existing_display.strip():
            skipped.append((found_name, "already has display_name"))
            continue
        try:
            cursor.execute(
                "UPDATE glyph_lexicon SET display_name = ?, response_template = ? WHERE rowid = ?",
                (meta.get("display_name"), meta.get("response_template"), rowid),
            )
            conn.commit()
            applied.append(found_name)
        except Exception as e:
            print(f"Failed to update {found_name}: {e}")

    print("\nMigration summary:")
    print(f" Applied: {len(applied)}")
    for a in applied:
        print(f"  - {a}")
    print(f" Skipped: {len(skipped)}")
    for s in skipped:
        print(f"  - {s[0]} ({s[1]})")
    print(f" Missing (not found): {len(missing)}")
    for m in missing:
        print(f"  - {m}")

    # Show updated rows for verification
    if applied:
        print("\nUpdated rows preview:")
        cursor.execute(
            "SELECT glyph_name, display_name, response_template FROM glyph_lexicon WHERE display_name IS NOT NULL AND display_name != '' LIMIT 20"
        )
        rows = cursor.fetchall()
        for r in rows:
            print(f" - {r[0]} -> {r[1]} | template: { (r[2][:80] + '...') if r[2] and len(r[2])>80 else r[2] }")

    conn.close()


if __name__ == "__main__":
    migrate()
