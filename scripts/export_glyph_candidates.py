#!/usr/bin/env python3
"""Chunked dry-run export of glyph_lexicon heuristic candidates to CSV.

Produces CSV files under `archive/glyph_exports/` named
`candidates_<start>_<end>.csv` where start/end are 1-indexed row counts
in the candidate set. Default chunk size is 1000.

This script is intentionally read-only (dry-run) and will not modify the DB.
"""
import sqlite3
import os
import sys
import csv


DB_DEFAULT = 'archive/full_backups/restore_glyphs_20251120T014253Z.db'
OUT_DIR = 'archive/glyph_exports'
CHUNK_SIZE = 1000


def ensure_outdir(path):
    os.makedirs(path, exist_ok=True)


def table_exists(cur, name):
    cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def get_columns(cur):
    cur.execute("PRAGMA table_info('glyph_lexicon')")
    cols = [r[1] for r in cur.fetchall()]
    return cols


def build_criteria_and_params(markers):
    # We'll include: long descriptions (>800), many newlines (>8), duplicate glyph_name,
    # and marker matches in glyph_name or description (case-insensitive).
    marker_clauses = []
    params = []
    for m in markers:
        like = f"%{m}%"
        marker_clauses.append("LOWER(glyph_name) LIKE ?")
        params.append(like)
        marker_clauses.append("LOWER(description) LIKE ?")
        params.append(like)

    marker_sql = " OR ".join(marker_clauses) if marker_clauses else '0'

    # newline count via LENGTH(description) - LENGTH(REPLACE(description, char(10), ''))
    criteria = (
        "(LENGTH(description) > 800)"
        " OR (LENGTH(description) - LENGTH(REPLACE(description, char(10), '')) > 8)"
        " OR glyph_name IN (SELECT glyph_name FROM glyph_lexicon GROUP BY glyph_name HAVING COUNT(*)>1)"
        f" OR ({marker_sql})"
    )
    return criteria, params


def count_candidates(cur, criteria, params):
    sql = f"SELECT COUNT(*) FROM glyph_lexicon WHERE {criteria}"
    cur.execute(sql, params)
    return cur.fetchone()[0]


def export_chunks(conn, cur, cols, criteria, params, outdir, chunk_size):
    total = count_candidates(cur, criteria, params)
    print(f"Total candidate rows (heuristics): {total}")
    if total == 0:
        return []

    select_cols = ', '.join([f'"{c}"' for c in cols])
    # We'll fetch in ORDER BY rowid to make chunk boundaries stable.
    sql = f"SELECT rowid, {select_cols} FROM glyph_lexicon WHERE {criteria} ORDER BY rowid LIMIT ? OFFSET ?"

    written_files = []
    seen = 0
    offset = 0
    while offset < total:
        cur.execute(sql, params + [chunk_size, offset])
        rows = cur.fetchall()
        if not rows:
            break
        start = offset + 1
        end = offset + len(rows)
        fname = os.path.join(outdir, f"candidates_{start}_{end}.csv")
        with open(fname, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['rowid'] + cols)
            for r in rows:
                # r[0] is rowid, r[1:] correspond to cols order
                # Normalize None -> empty string for CSV readability
                outrow = [r[0]] + [('' if v is None else v) for v in r[1:]]
                writer.writerow(outrow)
        print(f'Wrote {fname} ({len(rows)} rows)')
        written_files.append(fname)
        offset += len(rows)
        seen += len(rows)

    print(f"Export complete: {seen} rows in {len(written_files)} file(s)")
    return written_files


def main(dbpath, outdir=OUT_DIR, chunk_size=CHUNK_SIZE):
    if not os.path.exists(dbpath):
        print('DB not found:', dbpath)
        return 2
    ensure_outdir(outdir)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    if not table_exists(cur, 'glyph_lexicon'):
        print('No table named glyph_lexicon found. Aborting.')
        conn.close()
        return 2

    cols = get_columns(cur)
    print('Found glyph_lexicon with columns:', cols)

    markers = ['markdown export', 'json export', 'archive', 'gutenberg', 'conversation archive',
               'markdown', 'json', 'export', 'file:', 'http://', 'https://', '<html', '```', 'title:']

    criteria, params = build_criteria_and_params(markers)
    print('Using heuristics to select candidates (dry-run). Chunk size:', chunk_size)

    files = export_chunks(conn, cur, cols, criteria,
                          params, outdir, chunk_size)

    conn.close()
    print('\nDry-run export finished. Files created:')
    for p in files:
        print(' -', p)
    return 0


if __name__ == '__main__':
    db = DB_DEFAULT
    chunk = CHUNK_SIZE
    out = OUT_DIR
    if len(sys.argv) > 1:
        db = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            chunk = int(sys.argv[2])
        except Exception:
            pass
    if len(sys.argv) > 3:
        out = sys.argv[3]

    sys.exit(main(db, out, chunk))
