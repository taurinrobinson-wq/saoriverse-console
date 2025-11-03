#!/bin/bash
# Quick reference for working with the newly generated glyphs

echo "=== POETRY GLYPHS QUICK REFERENCE ==="
echo ""

# Show glyph statistics
echo "[GLYPH STATISTICS]"
cat "/Volumes/My Passport for Mac/saoriverse_data/generated_glyphs_from_poetry.json" | python3 << 'EOF'
import json
import sys

with open(sys.argv[1]) as f:
    glyphs = json.load(f)

print(f"Total glyphs: {len(glyphs)}")
print(f"Frequency range: {min(g['combined_frequency'] for g in glyphs)} - {max(g['combined_frequency'] for g in glyphs)}")
print(f"\nBy emotion combination:")

for glyph in glyphs[:10]:
    emotions = " + ".join(glyph['core_emotions'])
    print(f"  {glyph['symbol']} {glyph['name']}: {emotions} ({glyph['combined_frequency']})")

EOF

echo ""
echo "[FILE LOCATIONS]"
echo "Glyph JSON:     /Volumes/My Passport for Mac/saoriverse_data/generated_glyphs_from_poetry.json"
echo "Poetry corpus:  /Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry/"
echo "Processing log: /Volumes/My Passport for Mac/saoriverse_data/gutenberg_learning.log"
echo ""

echo "[INTEGRATION SUGGESTIONS]"
echo "1. Import glyphs into your glyph database:"
echo "   python -c \"import json; glyphs = json.load(open('/Volumes/My Passport for Mac/saoriverse_data/generated_glyphs_from_poetry.json')); print(f'Loaded {len(glyphs)} glyphs')\""
echo ""
echo "2. Add to system responses for better emotional understanding"
echo ""
echo "3. Create visual representations for the glyphs"
echo ""
echo "4. Map poetry collections to specific glyphs"
echo ""

echo "[KEY STATISTICS]"
echo "Poems processed: 18 collections"
echo "Total words: 1.1 million"
echo "Chunks processed: 2,185"
echo "Emotional signals: 1,368"
echo "Lexicon entries: 136,110"
echo "New glyphs created: 20"
echo ""

echo "✓ Generated glyphs are ready for integration!"
