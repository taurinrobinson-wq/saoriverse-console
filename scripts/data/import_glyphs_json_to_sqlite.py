#!/usr/bin/env python3
"""Import validated glyph lexicon JSON into a SQLite `glyph_lexicon` table.

Creates (or updates) `glyphs.db` in the repository root and populates the
`glyph_lexicon` table with columns compatible with `fetch_glyphs()` used by
the parser: `glyph_name, description, gate, display_name, response_template`.

Usage:
  python3 scripts/import_glyphs_json_to_sqlite.py
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "emotional_os" / "glyphs" / "glyph_lexicon_rows_validated.json"
DB_PATH = ROOT / "glyphs.db"


def create_table(conn):
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS glyph_lexicon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        glyph_name TEXT,
        description TEXT,
        gate TEXT,
        display_name TEXT,
        response_template TEXT
    )
    """
    )
    conn.commit()


def import_json(json_path: Path, db_path: Path):
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(str(db_path))
    try:
        create_table(conn)
        cur = conn.cursor()
        # Clear existing rows to avoid duplicates
        cur.execute("DELETE FROM glyph_lexicon")
        inserted = 0
        for row in data:
            glyph_name = row.get("glyph_name") or row.get("name") or ""
            description = row.get("description") or ""
            gate = row.get("gate") or row.get("gates") or ""
            display_name = glyph_name
            response_template = row.get("response_template") or None
            cur.execute(
                """INSERT INTO glyph_lexicon
                (glyph_name, description, gate, display_name, response_template)
                VALUES (?, ?, ?, ?, ?)""",
                (glyph_name, description, gate, display_name, response_template),
            )
            inserted += 1
        conn.commit()
        print(f"Imported {inserted} glyph rows into {db_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    import_json(JSON_PATH, DB_PATH)
