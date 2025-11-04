#!/usr/bin/env python3
import sqlite3
import json
import os
import sys

DB_PATH = 'emotional_os/glyphs/glyphs.db'
OUT_JSON = 'tools/archived_samples.json'

if not os.path.exists(DB_PATH):
    print(json.dumps({'error': f"DB not found: {DB_PATH}"}))
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check if table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='glyph_lexicon_archived'")
if not cur.fetchone():
    out = {'found': 0, 'samples': []}
    print(json.dumps(out, indent=2))
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    sys.exit(0)

# Count archived rows
cur.execute('SELECT COUNT(*) AS c FROM glyph_lexicon_archived')
count = cur.fetchone()['c']

# Select top 40 by archived_at desc if present, else by rowid
try:
    cur.execute('''
        SELECT orig_rowid, glyph_name, gate, archived_at, substr(description,1,800) as description_snippet
        FROM glyph_lexicon_archived
        ORDER BY archived_at DESC
        LIMIT 40
    ''')
    rows = cur.fetchall()
except Exception:
    cur.execute('''
        SELECT orig_rowid, glyph_name, gate, archived_at, substr(description,1,800) as description_snippet
        FROM glyph_lexicon_archived
        LIMIT 40
    ''')
    rows = cur.fetchall()

samples = []
for r in rows:
    samples.append({
        'orig_rowid': r['orig_rowid'],
        'glyph_name': r['glyph_name'],
        'gate': r['gate'],
        'archived_at': r['archived_at'],
        'description_snippet': r['description_snippet']
    })

out = {'found': count, 'samples': samples}
print(json.dumps(out, indent=2, ensure_ascii=False))
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

conn.close()
print(f"Wrote {OUT_JSON}")
