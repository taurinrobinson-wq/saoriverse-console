#!/usr/bin/env python3
import sqlite3
import os
import json

DB = os.path.join('emotional_os', 'glyphs', 'glyphs.db')
if not os.path.exists(DB):
    print('DB not found at', DB)
    raise SystemExit(2)

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('Schema for glyph_lexicon:')
cur.execute("PRAGMA table_info('glyph_lexicon')")
cols = cur.fetchall()
for c in cols:
    print(c)

print('\nRow count:')
cur.execute('SELECT COUNT(*) FROM glyph_lexicon')
print(cur.fetchone()[0])

print('\nSample rows (id, name, label, created_at, updated_at) if present:')
# try common columns
sample_cols = ['id', 'name', 'label', 'token', 'value',
               'created_at', 'updated_at', 'last_used', 'raw']
# build select with intersection of actual columns
actual_cols = [c[1] for c in cols]
sel = []
for c in sample_cols:
    if c in actual_cols:
        sel.append(c)
if not sel:
    sel = actual_cols[:6]

q = 'SELECT ' + ','.join(sel) + ' FROM glyph_lexicon LIMIT 20'
cur.execute(q)
rows = cur.fetchall()
print('Columns selected:', sel)
for r in rows:
    print(r)

conn.close()
