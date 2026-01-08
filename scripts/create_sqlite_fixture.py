#!/usr/bin/env python3
"""
Create a minimal SQLite fixture used by the integration CI job.

This creates `emotional_os/glyphs/glyphs_integration_fixture.db` with a
very small `glyphs` table that the smoke test can read.
"""
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(ROOT, "emotional_os", "glyphs")
DB_PATH = os.path.join(DB_DIR, "glyphs_integration_fixture.db")


def create_fixture(path: str = DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    # Minimal glyphs table with common columns used by the system
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS glyphs (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            display_name TEXT,
            response_template TEXT
        )
        """
    )
    # Insert one sample glyph
    cur.execute(
        "INSERT INTO glyphs (name, display_name, response_template) VALUES (?, ?, ?)",
        ("sample_glyph", "Sample Glyph", "This is a sample response template."),
    )
    conn.commit()
    conn.close()
    print(f"Created SQLite fixture at: {path}")


if __name__ == "__main__":
    create_fixture()
