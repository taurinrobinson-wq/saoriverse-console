"""Import salvaged glyph entries (JSONL or JSON array) into a staging table.

This script is non-destructive: it writes to `glyph_lexicon_salvaged` and
logs a short summary. It deliberately does not merge into the primary
`glyph_lexicon` table — reconciliation should be a human-reviewed step.

Usage: `python scripts/import_salvaged_glyphs.py path/to/salvaged.jsonl`
"""
import json
import os
import sqlite3
import sys
import logging
from typing import List

logging.basicConfig(level=logging.INFO)

DB_PATH = os.getenv('GLYPH_DB_PATH', 'emotional_os/glyphs/glyphs.db')


def load_entries_from_file(path: str) -> List[dict]:
    entries = []
    with open(path, 'r', encoding='utf-8') as fh:
        first = fh.readline().strip()
        # Heuristic: JSONL vs JSON array
        try:
            if first.startswith('{') and '\n' in fh.read(1):
                # JSONL - process line-by-line
                fh.seek(0)
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        logging.warning('Skipping malformed line in JSONL')
            else:
                # Try JSON array
                fh.seek(0)
                data = json.load(fh)
                if isinstance(data, list):
                    entries.extend(data)
                elif isinstance(data, dict):
                    entries.append(data)
        except json.JSONDecodeError:
            logging.error('Failed to parse input file as JSON/JSONL')
    return entries


def import_to_staging(entries: List[dict], db_path: str = DB_PATH):
    if not entries:
        logging.info('No entries to import')
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure staging table exists
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'sql', 'create_glyph_lexicon_salvaged.sql'), 'r', encoding='utf-8') as fh:
            ddl = fh.read()
            cursor.executescript(ddl)
    except Exception:
        # If the DDL file is missing, attempt to create minimal table
        cursor.execute('''CREATE TABLE IF NOT EXISTS glyph_lexicon_salvaged (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            glyph_name TEXT NOT NULL,
            description TEXT,
            gate TEXT,
            source_file TEXT,
            imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            raw_payload TEXT
        );''')

    inserted = 0
    for e in entries:
        try:
            name = e.get('glyph_name') or e.get(
                'name') or e.get('glyph') or 'unnamed'
            description = e.get('description') or e.get('desc') or None
            gate = e.get('gate') or e.get('gates') or None
            raw = json.dumps(e, ensure_ascii=False)
            cursor.execute('''INSERT INTO glyph_lexicon_salvaged (glyph_name, description, gate, source_file, raw_payload) VALUES (?, ?, ?, ?, ?)''', (
                name, description, gate if isinstance(gate, str) else (','.join(gate) if isinstance(gate, list) else None), os.path.basename(path), raw))
            inserted += 1
        except Exception as ex:
            logging.warning(f"Failed to insert entry: {ex}")

    conn.commit()
    conn.close()
    logging.info(f"Imported {inserted} entries into glyph_lexicon_salvaged")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/import_salvaged_glyphs.py PATH_TO_FILE')
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print('File not found:', path)
        sys.exit(1)
    ents = load_entries_from_file(path)
    import_to_staging(ents)
