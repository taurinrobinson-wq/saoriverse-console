import json

with open('emotional_os/glyphs/glyph_lexicon_rows.json', 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)
    
if data:
    print("Total glyphs in JSON:", len(data))
    if isinstance(data, list) and len(data) > 0:
        print("\nFirst glyph keys:", list(data[0].keys()))
        glyph = [x for x in data if x.get('glyph_name') == 'Still Insight']
        if glyph:
            print("\nStill Insight entry:")
            print(json.dumps(glyph[0], indent=2)[:1500])
        else:
            # Show first glyph to see structure
            print("\nFirst glyph entry:")
            print(json.dumps(data[0], indent=2)[:1500])
