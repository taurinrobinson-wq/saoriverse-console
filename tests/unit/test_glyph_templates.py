import sqlite3

conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
cursor = conn.cursor()
cursor.execute('SELECT glyph_name, response_template FROM glyph_lexicon WHERE response_template IS NOT NULL LIMIT 10')
for row in cursor.fetchall():
    print(f'Glyph: {row[0]}')
    template_preview = row[1][:200] if row[1] else "None"
    print(f'Template: {template_preview}')
    print()
conn.close()
