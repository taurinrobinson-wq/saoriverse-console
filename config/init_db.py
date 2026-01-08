#!/usr/bin/env python3
"""Initialize the glyphs database from SQL"""

import sqlite3
import sys

db_path = "/workspaces/saoriverse-console/glyphs.db"
sql_file = "/workspaces/saoriverse-console/emotional_os/glyphs/glyph_lexicon_rows.sql"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(sql_file, "r") as f:
        sql_content = f.read()

    # Execute the SQL file content
    cursor.executescript(sql_content)
    conn.commit()

    # Verify table was created
    cursor.execute("SELECT COUNT(*) FROM glyph_lexicon;")
    count = cursor.fetchone()[0]
    print("✓ Database initialized successfully")
    print(f"✓ glyph_lexicon table has {count} rows")

    conn.close()
except Exception as e:
    print(f"✗ Error initializing database: {e}")
    sys.exit(1)
