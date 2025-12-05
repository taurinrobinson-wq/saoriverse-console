#!/usr/bin/env python3
"""Check glyph response templates"""

import sqlite3

conn = sqlite3.connect('glyphs.db')
cur = conn.cursor()

# Check if response_template column has data
cur.execute("SELECT glyph_name, description, response_template FROM glyph_lexicon WHERE glyph_name='Still Insight' LIMIT 1")
row = cur.fetchone()

if row:
    print(f"Glyph: {row[0]}")
    print(f"\nDescription:\n{row[1][:300] if row[1] else 'NONE'}")
    print(f"\nResponse Template:\n{row[2][:300] if row[2] else 'NONE'}")
else:
    print("Glyph not found")

# Check how many glyphs have response templates
cur.execute("SELECT COUNT(*) FROM glyph_lexicon WHERE response_template IS NOT NULL AND response_template != ''")
count = cur.fetchone()[0]
print(f"\n\nGlyphs with response templates: {count} out of")

cur.execute("SELECT COUNT(*) FROM glyph_lexicon")
total = cur.fetchone()[0]
print(f"Total glyphs: {total}")

conn.close()
