#!/usr/bin/env python3
"""Check glyph database status after processing"""

import sqlite3


def check_database_status():
    conn = sqlite3.connect("emotional_os/glyphs/glyphs.db")
    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM glyph_lexicon")
    total = cursor.fetchone()[0]
    print(f"📊 Total glyphs in database: {total}")

    # Count by gate
    cursor.execute("SELECT gate, COUNT(*) FROM glyph_lexicon GROUP BY gate ORDER BY gate")
    print("\n🚪 Glyphs by gate:")
    for gate, count in cursor.fetchall():
        print(f"  {gate}: {count} glyphs")

    # Sample some newly added glyphs
    cursor.execute(
        "SELECT glyph_name, gate FROM glyph_lexicon WHERE voltage_pair LIKE 'extracted_%' ORDER BY rowid DESC LIMIT 10"
    )
    print("\n🆕 Sample newly extracted glyphs:")
    for name, gate in cursor.fetchall():
        print(f"  • {name} ({gate})")

    conn.close()


if __name__ == "__main__":
    check_database_status()
