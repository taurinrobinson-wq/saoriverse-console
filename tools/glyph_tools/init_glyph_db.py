#!/usr/bin/env python3
"""Initialize glyph database from JSON data files"""

import json
import sqlite3
from pathlib import Path
import sys

def init_glyph_db():
    """Create glyphs.db from available glyph JSON files"""
    
    root = Path(__file__).parent  # repo root (same dir as script)
    db_path = root / "glyphs.db"
    
    # Try different JSON sources
    json_paths = [
        root / "emotional_os" / "glyphs" / "glyph_lexicon_rows.json",
        root / "emotional_os" / "glyphs" / "glyph_lexicon_rows_validated.json",
        root / "data" / "glyph_lexicon_rows.json",
        root / "data" / "glyph_lexicon_rows_validated.json",
    ]
    
    json_path = None
    for path in json_paths:
        if path.exists():
            json_path = path
            print(f"✓ Found glyph data: {path}")
            break
    
    if not json_path:
        print(f"✗ No glyph JSON found in: {json_paths}")
        return False
    
    try:
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded {len(data)} glyphs from JSON")
        
        # Create database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS glyph_lexicon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                glyph_name TEXT UNIQUE,
                description TEXT,
                gate TEXT,
                display_name TEXT,
                response_template TEXT
            )
        """)
        
        # Clear existing data
        cursor.execute("DELETE FROM glyph_lexicon")
        
        # Insert glyph data
        inserted = 0
        for row in data:
            try:
                glyph_name = row.get("glyph_name") or row.get("name") or ""
                description = row.get("description") or ""
                gate = row.get("gate") or row.get("gates") or ""
                display_name = row.get("display_name") or glyph_name
                response_template = row.get("response_template")
                
                if glyph_name:
                    cursor.execute(
                        """INSERT OR REPLACE INTO glyph_lexicon
                        (glyph_name, description, gate, display_name, response_template)
                        VALUES (?, ?, ?, ?, ?)""",
                        (glyph_name, description, gate, display_name, response_template)
                    )
                    inserted += 1
            except Exception as e:
                print(f"  ⚠ Failed to insert glyph: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✓ Created {db_path} with {inserted} glyphs")
        return True
        
    except Exception as e:
        print(f"✗ Failed to initialize glyph database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_glyph_db()
    sys.exit(0 if success else 1)
