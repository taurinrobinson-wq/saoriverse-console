#!/usr/bin/env python3
"""
Analyze glyph database for redundancy and consolidation opportunities
"""

import sqlite3


def analyze_database():
    conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    """Compatibility stub: import implementation from tools.analyze_glyphs
    and expose a runnable script for backwards compatibility.
    """

    from tools.analyze_glyphs import main

    if __name__ == "__main__":
        main()
