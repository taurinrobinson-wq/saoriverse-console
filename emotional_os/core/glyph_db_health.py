"""Glyph DB health checks.

Provides a lightweight runtime check to ensure key glyph tables exist
and are readable. Intended to be called on startup (warn-only by default)
so it doesn't break import-time behavior in tests or CI.
"""
from __future__ import annotations

import logging
import sqlite3
from typing import Dict, List, Optional

from .paths import glyph_db_path

logger = logging.getLogger(__name__)


def _connect(db_path: Optional[str]) -> sqlite3.Connection:
    p = db_path if db_path else str(glyph_db_path())
    return sqlite3.connect(p)


def check_glyph_db(db_path: Optional[str] = None, required_tables: Optional[List[str]] = None, warn_only: bool = True) -> Dict[str, bool]:
    """Check the glyph DB for the presence/readability of required tables.

    Args:
        db_path: optional path to sqlite DB. If None, uses `glyph_db_path()`.
        required_tables: list of table names to verify. Defaults to
            `['glyph_lexicon', 'glyph_lexicon_salvaged']`.
        warn_only: if True, only logs warnings and returns status dict. If
            False, raises RuntimeError when required tables are missing.

    Returns:
        dict mapping table name to bool (present).
    """
    if required_tables is None:
        required_tables = ['glyph_lexicon', 'glyph_lexicon_salvaged']

    statuses = {t: False for t in required_tables}
    try:
        conn = _connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        rows = cur.fetchall()
        existing = {r[0] for r in rows}
        for t in required_tables:
            statuses[t] = t in existing

        for t, ok in statuses.items():
            if not ok:
                msg = f"[WARN] {t} not found — response engine may fallback or fail silently."
                try:
                    logger.warning(msg)
                except Exception:
                    print(msg)
        conn.close()
    except Exception as e:
        msg = f"[WARN] could not open glyph DB at '{db_path or glyph_db_path()}' — {e}"
        try:
            logger.warning(msg)
        except Exception:
            print(msg)
        # Treat as all-missing when DB can't be opened
        statuses = {t: False for t in required_tables}

    # If strict mode, raise when any missing
    if not warn_only and not all(statuses.values()):
        missing = [t for t, ok in statuses.items() if not ok]
        raise RuntimeError(f"Missing glyph DB tables: {missing}")

    return statuses


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Check glyph DB health')
    parser.add_argument('--db', help='Path to glyph DB (optional)')
    parser.add_argument('--no-warn-only', dest='warn_only',
                        action='store_false', help='Raise on missing tables')
    args = parser.parse_args()
    res = check_glyph_db(db_path=args.db, warn_only=args.warn_only)
    ok = all(res.values())
    for k, v in res.items():
        print(f"{k}: {'OK' if v else 'MISSING'}")
    raise SystemExit(0 if ok else 2)
