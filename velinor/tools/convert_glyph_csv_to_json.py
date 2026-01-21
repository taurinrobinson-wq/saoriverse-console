#!/usr/bin/env python3
"""
Convert `velinor/markdowngameinstructions/Glyph_Organizer.csv` to
`velinor/markdowngameinstructions/Glyph_Organizer.json` with extended fields.

Usage: run from repository root (script handles paths relative to repo root).
"""
import csv
import json
import os
import re

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Organizer.csv'))
OUT_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Organizer.json'))

def slugify(s: str) -> str:
    s = s or ''
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", '_', s)
    s = re.sub(r"_+", '_', s).strip('_')
    return s

def parse_npc_field(npc_field: str):
    # common format: "Name - Role" or just "Name"
    if not npc_field:
        return {'name': '', 'role': ''}
    parts = [p.strip() for p in npc_field.split(' - ', 1)]
    if len(parts) == 2:
        return {'name': parts[0], 'role': parts[1]}
    # try comma separation for multiple names
    if ',' in npc_field and ' and ' not in npc_field:
        names = [p.strip() for p in npc_field.split(',')]
        return {'name': ', '.join(names), 'role': ''}
    return {'name': npc_field.strip(), 'role': ''}

def derive_tags(domain: str, theme: str, storyline: str):
    tags = set()
    if domain:
        tags.add(domain.lower())
    if theme:
        for token in re.split(r"[\s,;:\-\/]+", theme):
            token = token.strip().lower()
            if token and len(token) > 2:
                tags.add(token)
    # small heuristic: check for memory keywords
    if storyline and any(k in storyline.lower() for k in ('memory', 'remember', 'forgot', 'stolen', 'fracture', 'collapse', 'presence', 'stillness')):
        tags.add('memory-loss')
    return sorted(list(tags))

def main():
    glyphs = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.reader(fh)
        header = next(reader)
        # Expecting header: Category,Count,Theme,NPC Giver,Glyph,Location,Storyline
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            # pad row to expected length
            while len(row) < 7:
                row.append('')
            domain, count, theme, npc_giver, glyph_name, location, storyline = row[:7]
            try:
                gid = int(count)
            except Exception:
                gid = None

            npc = parse_npc_field(npc_giver)

            # build JSON object following the extended schema
            obj = {
                'domain': domain.strip() if domain else '',
                'id': gid,
                'theme': theme.strip() if theme else '',
                'npc': {
                    'name': npc.get('name',''),
                    'role': npc.get('role',''),
                    'npc_images': [],
                    'background_images': [],
                },
                'glyph_name': glyph_name.strip() if glyph_name else '',
                'location': location.strip() if location else '',
                'storyline_summary': (storyline.strip()[:300] + '...') if storyline and len(storyline) > 300 else (storyline.strip() if storyline else ''),
                'story_seed': '',
                'tone_integration': [],
                'remnants_integration': [],
                'player_choices': [],
                'narrative_triggers': [],
                'memory_fragments': [],
                'tags': derive_tags(domain, theme, storyline),
                'alignment_paths': None,
                'original_storyline_text': storyline.strip() if storyline else ''
            }

            # provide sensible defaults for images using slugified values
            if obj['npc']['name']:
                base = slugify(obj['npc']['name'])
                obj['npc']['npc_images'] = [f"npcs/{base}.png"]
            if obj['location']:
                locbase = slugify(obj['location'])
                obj['npc']['background_images'] = [f"backgrounds/{locbase}.png"]

            glyphs.append(obj)

    out = {'glyphs': glyphs, 'meta': {'source_csv': os.path.relpath(CSV_PATH, start=HERE), 'converted_by': 'convert_glyph_csv_to_json.py'}}
    with open(OUT_PATH, 'w', encoding='utf-8') as outf:
        json.dump(out, outf, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT_PATH} with {len(glyphs)} glyphs")

if __name__ == '__main__':
    main()
