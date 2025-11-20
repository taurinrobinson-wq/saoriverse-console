#!/usr/bin/env python3
"""
Basic analysis of `emotional_os/glyphs/glyphs.db` to surface tables, row
counts, and candidate duplicate glyph names for manual review.
"""
import sqlite3
import os
import sys

DB = os.path.join('emotional_os', 'glyphs', 'glyphs.db')


def main():
    if not os.path.exists(DB):
        print('glyphs.db not found at', DB)
        sys.exit(2)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # list tables
    cur.execute(
        "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")
    tables = cur.fetchall()
    print('Tables/views:')
    for t in tables:
        print(' -', t[0], t[1])

    # row counts
    print('\nRow counts:')
    for t in tables:
        name = t[0]
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{name}"')
            cnt = cur.fetchone()[0]
        except Exception as e:
            cnt = f'error: {e}'
        print(f' - {name}: {cnt}')

    # attempt to find a column named 'name' or 'label' in tables and list duplicates
    print('\nCandidate duplicate glyph names (by table):')
    for t in tables:
        name = t[0]
        try:
            cur.execute(f'PRAGMA table_info("{name}")')
            cols = [r[1] for r in cur.fetchall()]
            candidate_cols = [c for c in cols if c.lower() in (
                'name', 'label', 'tag', 'glyph')]
            if not candidate_cols:
                continue
            col = candidate_cols[0]
            cur.execute(
                f'SELECT {col}, COUNT(*) as c FROM "{name}" GROUP BY {col} HAVING c>1 ORDER BY c DESC LIMIT 20')
            dups = cur.fetchall()
            if dups:
                print(f' - Table {name}, column {col} has duplicates:')
                for dd in dups:
                    print('    ', dd[0], 'count=', dd[1])
        except Exception:
            pass

    conn.close()
    print('\nAnalysis complete')


if __name__ == '__main__':
    main()
