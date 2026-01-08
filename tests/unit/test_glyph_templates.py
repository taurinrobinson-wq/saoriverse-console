
import sqlite3
from pathlib import Path


def _db_path() -> str:
    # tests/unit is two levels under repo root; build path to the DB used by the project
    return str(Path(__file__).resolve().parents[2] / "emotional_os" / "glyphs" / "glyphs.db")


def test_glyph_table_has_rows():
    conn = sqlite3.connect(_db_path())
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM glyph_lexicon")
    count = cur.fetchone()[0]
    conn.close()
    assert isinstance(count, int)
    assert count > 0


def test_response_template_column_exists():
    conn = sqlite3.connect(_db_path())
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(glyph_lexicon)")
    cols = [r[1] for r in cur.fetchall()]
    conn.close()
    assert "response_template" in cols
