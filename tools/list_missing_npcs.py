#!/usr/bin/env python3
"""
List missing NPCs by comparing names in Glyph_Organizer.json to existing NPC image files.
Writes CSV to `tools/missing_npcs.csv` with columns: npc_name,found,matched_files
"""
import json
from pathlib import Path
import csv
import re

GLYPH_ORG = Path('velinor/markdowngameinstructions/glyphs/Glyph_Organizer.json')
NPC_DIRS = [Path('velinor/npcs'), Path('velinor-web/assets/npcs'), Path('velinor-web/public/velinor/npcs')]
OUT_CSV = Path('tools/missing_npcs.csv')


def load_npc_names(js_path: Path):
    data = json.loads(js_path.read_text(encoding='utf-8'))
    names = []
    for item in data.get('glyphs', []):
        npc = item.get('npc')
        if not npc:
            continue
        name = npc.get('name')
        if name:
            names.append(name.strip())
    # unique preserving order
    seen = set()
    out = []
    for n in names:
        if n.lower() not in seen:
            out.append(n)
            seen.add(n.lower())
    return out


def gather_image_files(dirs):
    files = []
    for d in dirs:
        if not d.exists():
            continue
        for p in d.rglob('*.png'):
            files.append(p)
        for p in d.rglob('*.jpg'):
            files.append(p)
    return files


def tokens_of(name: str):
    # split name into tokens, remove short words and punctuation
    parts = re.split(r"[^A-Za-z0-9]+", name.lower())
    toks = [p for p in parts if len(p) > 2]
    return toks


def match_name_to_files(name: str, files):
    toks = tokens_of(name)
    matched = []
    if not toks:
        return matched
    # strategy: match files containing any token
    for f in files:
        fname = f.name.lower()
        for t in toks:
            if t in fname:
                matched.append(str(f))
                break
    return matched


def main():
    if not GLYPH_ORG.exists():
        print('Glyph organizer not found at', GLYPH_ORG)
        return
    names = load_npc_names(GLYPH_ORG)
    files = gather_image_files(NPC_DIRS)
    # also include top-level velinor/npcs original folder
    orig = Path('velinor/npcs/original')
    if orig.exists():
        for p in orig.rglob('*.png'):
            files.append(p)
    rows = []
    for n in names:
        matched = match_name_to_files(n, files)
        found = len(matched) > 0
        rows.append((n, 'yes' if found else 'no', ';'.join(matched)))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['npc_name','found','matched_files'])
        w.writerows(rows)

    print(f'Wrote {OUT_CSV} with {len(rows)} entries. Missing: {sum(1 for r in rows if r[1]=="no")}')


if __name__ == '__main__':
    main()
