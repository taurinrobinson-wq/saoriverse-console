#!/usr/bin/env python3
"""CLI verifier for the glyph DB.

Usage:
  ./scripts/check_glyph_db.py --db path/to/glyphs.db --show-counts
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from emotional_os.core.glyph_db_health import check_glyph_db


def count_table_rows(db: str, table: str) -> int:
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(f"SELECT count(*) FROM {table}")
        c = cur.fetchone()[0]
        conn.close()
        return int(c)
    except Exception:
        return -1


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', help='Path to glyph DB (optional)')
    p.add_argument('--show-counts', action='store_true',
                   help='Show glyph counts per table')
    p.add_argument('--strict', action='store_true',
                   help='Exit non-zero on missing tables (default is warn-only)')
    args = p.parse_args()

    res = check_glyph_db(db_path=args.db, warn_only=not args.strict)
    all_ok = all(res.values())
    for k, v in res.items():
        print(f"{k}: {'OK' if v else 'MISSING'}")

    db_path = args.db if args.db else None
    if args.show_counts and all_ok:
        db_path = args.db if args.db else None
        # derive path used by check_glyph_db if not provided
        if not db_path:
            # attempt to import path resolver
            try:
                from emotional_os.core.paths import glyph_db_path
                db_path = str(glyph_db_path())
            except Exception:
                db_path = None
        if db_path and Path(db_path).exists():
            for t in res.keys():
                c = count_table_rows(db_path, t)
                print(f"{t} rows: {c if c>=0 else 'UNKNOWN'}")

    sys.exit(0 if all_ok else 2)


if __name__ == '__main__':
    main()
