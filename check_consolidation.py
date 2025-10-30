#!/usr/bin/env python3
"""Check consolidation results"""

import sqlite3

conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
cursor = conn.cursor()

# Total glyphs
cursor.execute('SELECT COUNT(*) FROM glyph_lexicon')
total = cursor.fetchone()[0]
print(f'Total glyphs: {total}')

# Deprecated glyphs
cursor.execute("SELECT COUNT(*) FROM glyph_lexicon WHERE glyph_name LIKE '[DEPRECATED]%'")
deprecated = cursor.fetchone()[0]
print(f'Deprecated glyphs: {deprecated}')

# Active glyphs (not deprecated)
active = total - deprecated
print(f'Active glyphs: {active}')

# Consolidation mappings
cursor.execute('SELECT COUNT(*) FROM consolidation_map')
mapped = cursor.fetchone()[0]
print(f'Consolidation mappings: {mapped}')

# Show a few deprecated examples
cursor.execute("SELECT glyph_name FROM glyph_lexicon WHERE glyph_name LIKE '[DEPRECATED]%' LIMIT 3")
examples = cursor.fetchall()
if examples:
    print(f'Deprecated examples:')
    for ex in examples:
        print(f'  - {ex[0][:80]}...' if len(ex[0]) > 80 else f'  - {ex[0]}')

# Show merged entries
cursor.execute('SELECT merged_name, COUNT(*) FROM consolidation_map GROUP BY merged_name')
merges = cursor.fetchall()
if merges:
    print(f'Merged entries:')
    for name, count in merges:
        print(f'  - "{name}" (consolidated {count} duplicates)')

conn.close()