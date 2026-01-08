#!/usr/bin/env python3
"""Export all glyph_lexicon rows that have display_name and response_template to a CSV.

Output: scripts/output/curated_glyphs_export.csv
"""
import csv
import os
import sqlite3

ROOT = os.path.dirname(__file__)
DB_PATH = os.path.normpath(os.path.join(ROOT, "..", "emotional_os", "glyphs", "glyphs.db"))
OUT_DIR = os.path.join(ROOT, "output")
OUT_PATH = os.path.join(OUT_DIR, "curated_glyphs_export.csv")

os.makedirs(OUT_DIR, exist_ok=True)

if not os.path.exists(DB_PATH):
    print(f"DB not found at {DB_PATH}")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute(
    "SELECT rowid, glyph_name, display_name, response_template, gate FROM glyph_lexicon WHERE display_name IS NOT NULL AND display_name != '' AND response_template IS NOT NULL AND response_template != '' ORDER BY display_name COLLATE NOCASE"
)
rows = cur.fetchall()

with open(OUT_PATH, "w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["rowid", "glyph_name", "display_name", "response_template", "gate"])
    for r in rows:
        writer.writerow([r[0], r[1], r[2], r[3], r[4]])

print(f"Wrote {len(rows)} rows to {OUT_PATH}")

# Print a short preview
preview_n = min(10, len(rows))
if preview_n:
    print("\nPreview:")
    for r in rows[:preview_n]:
        print(
            f" - rowid={r[0]} display_name='{r[2]}' gate={r[4]} template='{(r[3][:120] + '...') if r[3] and len(r[3])>120 else r[3]}'"
        )

conn.close()
