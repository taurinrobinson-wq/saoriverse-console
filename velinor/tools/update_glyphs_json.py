import json
from pathlib import Path
p = Path('velinor/markdowngameinstructions/glyphs/Glyph_Organizer.json')
data = json.loads(p.read_text(encoding='utf-8'))
updated = 0
for g in data.get('glyphs', []):
    if g.get('id') == 23:
        g['location'] = 'Archive Interior (Reclaimed Chambers)'
        g['storyline_summary'] = "Malrik navigates the archive building's interior with the player, each step deliberate and measured. The glyph now integrates archive collapse context: when the building fails this motif signals the tension between preservation and ritual—choices here influence Malrik/Elenya reconciliation and rebuild potential. The glyph manifests when the player moves through the chambers and recognizes discipline as both protection and a barrier to intimacy."
        g.setdefault('narrative_triggers', [])
        if 'building_collapse' not in g['narrative_triggers']:
            g['narrative_triggers'].append('building_collapse')
        if 'malrik_elenya_conflict' not in g['narrative_triggers']:
            g['narrative_triggers'].append('malrik_elenya_conflict')
        if 'rebuild_event' not in g['narrative_triggers']:
            g['narrative_triggers'].append('rebuild_event')
        g.setdefault('tags', [])
        for tag in ['archive','building','collapse-event']:
            if tag not in g['tags']:
                g['tags'].append(tag)
        updated += 1
    if g.get('id') == 24:
        g['location'] = 'The Shared Archive Building (Entrance)'
        g['storyline_summary'] = "Malrik stands at the archive building's entrance, inscribing preservation boundaries. He argues that records must be sealed and organized—that structure is the only way to honor memory. After collapse, this boundary becomes contentious: will the rebuilt archive be a sealed repository or a shared ritual space? The glyph manifests when the player helps mark preservation zones and recognizes the cost of rigid boundaries."
        g.setdefault('narrative_triggers', [])
        for trig in ['building_collapse','boundary_marked','rebuild_event']:
            if trig not in g['narrative_triggers']:
                g['narrative_triggers'].append(trig)
        g.setdefault('tags', [])
        for tag in ['archive','boundary','rebuild']:
            if tag not in g['tags']:
                g['tags'].append(tag)
        updated += 1
    if g.get('id') == 62:
        g['location'] = 'Archive Chamber (Ruins Where Inscriptions Blur)'
        g['storyline_summary'] = "Malrik shows the player chambers where the Corelink system stored emotional data — now corrupted, glitching, displaying fragments of millions of private moments. After the archive collapse the glyph becomes central to salvage options: choices to rescue, reconstruct, or abandon records influence rebuild potential and Malrik/Elenya's relationship. The glyph manifests when the player recognizes the human cost of institutional failure and the possibility of rebuilding meaning from fragments."
        g.setdefault('narrative_triggers', [])
        for trig in ['system_glitch_detected','player_enters_location','building_collapse','salvage_choice']:
            if trig not in g['narrative_triggers']:
                g['narrative_triggers'].append(trig)
        g.setdefault('tags', [])
        for tag in ['collapse','archive','salvage']:
            if tag not in g['tags']:
                g['tags'].append(tag)
        updated += 1
p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
print('updated', updated)
