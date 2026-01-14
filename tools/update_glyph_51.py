from pathlib import Path
import json
# Update CSV
csvp = Path('velinor/markdowngameinstructions/glyphs/Glyph_Organizer.csv')
text = csvp.read_text(encoding='utf-8')
old_marker = 'High Seer Elenya,Glyph of Covenant Flame,'
if old_marker in text:
    # Replace the line start after the marker
    parts = text.split('\n')
    for i,l in enumerate(parts):
        if old_marker in l:
            # compose new CSV line (use concatenation to avoid quoting issues)
            new_line = (
                'Trust,51,"Community, restoration, interdependence",High Seer Elenya,'
                'Glyph of Covenant Flame,The Shared Archive Building (Central Chamber with Shrine Space),'
                '"Elenya gathers the community in the archive building\'s central chamber to light the Covenant Flame — '
                'a ritual that demonstrates the archive\'s role as a living, shared space rather than a sealed vault. '
                'After the collapse the flame becomes a focal point for rebuild decisions: does the community preserve '
                'records in exclusive custody, or does it tend memory together? The glyph manifests when the player joins '
                'the ritual and recognizes that activation can be a form of preservation, enabling reconciliation between '
                'preservation and ritual."'
            )
            parts[i] = new_line
            break
    csvp.write_text('\n'.join(parts), encoding='utf-8')
    print('csv-updated')
else:
    print('marker-not-found')
# Update JSON
jsonp = Path('velinor/markdowngameinstructions/glyphs/Glyph_Organizer.json')
data = json.loads(jsonp.read_text(encoding='utf-8'))
updated = False
for g in data.get('glyphs',[]):
    if g.get('id') == 51:
        g['location'] = 'The Shared Archive Building (Central Chamber with Shrine Space)'
        g['storyline_summary'] = "Elenya gathers the community in the archive building's central chamber to light the Covenant Flame — a ritual that demonstrates the archive's role as a living, shared space rather than a sealed vault. After the collapse the flame becomes a focal point for rebuild decisions: does the community preserve records in exclusive custody, or does it tend memory together? The glyph manifests when the player joins the ritual and recognizes that activation can be a form of preservation, enabling reconciliation between preservation and ritual."
        g.setdefault('narrative_triggers', [])
        for trig in ['archive_discovered','building_collapse','rebuild_event','ritual_activated']:
            if trig not in g['narrative_triggers']:
                g['narrative_triggers'].append(trig)
        g.setdefault('tags', [])
        for tag in ['archive','covenant','rebuild','shrine']:
            if tag not in g['tags']:
                g['tags'].append(tag)
        updated = True
        break
if updated:
    jsonp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print('json-updated')
else:
    print('json-not-found')
