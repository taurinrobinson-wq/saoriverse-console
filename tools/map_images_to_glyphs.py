import json
from pathlib import Path
import re

ROOT = Path('d:/saoriverse-console')
GO = ROOT / 'velinor' / 'markdowngameinstructions' / 'glyphs' / 'Glyph_Organizer.json'
IMAGE_DIRS = [
    ROOT / 'velinor' / 'glyph_images',
    ROOT / 'velinor' / 'npcs',
    ROOT / 'velinor' / 'backgrounds',
    ROOT / 'velinor' / 'overlays',
    ROOT / 'velinor-web' / 'public' / 'velinor' / 'backgrounds',
    ROOT / 'velinor-web' / 'public' / 'velinor' / 'overlays',
]

def gather_images():
    images = []
    for d in IMAGE_DIRS:
        if not d.exists():
            continue
        for p in d.rglob('*'):
            if p.is_file() and p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg'):
                # store relative path from workspace root
                rel = p.relative_to(ROOT)
                images.append(str(rel).replace('\\','/'))
    return images


def tokens(s):
    s = re.sub(r"[^0-9a-zA-Z]+", ' ', s or '').lower()
    return [t for t in s.split() if t]


def match_images_for_glyph(glyph_name, images):
    tks = tokens(glyph_name)
    matches = []
    for img in images:
        n = img.lower()
        score = sum(1 for t in tks if t in n)
        if score>0:
            matches.append((score, img))
    matches.sort(reverse=True)
    # return top 3 unique
    return [m[1] for m in matches[:3]]


def match_npc_images(npc_name, images):
    tks = tokens(npc_name)
    matches = []
    for img in images:
        if not img.startswith('npcs/'):
            continue
        n = img.lower()
        score = sum(1 for t in tks if t in n)
        if score>0:
            matches.append((score, img))
    matches.sort(reverse=True)
    return [m[1] for m in matches[:5]]


def main():
    images = gather_images()
    GO_text = GO.read_text(encoding='utf-8')
    data = json.loads(GO_text)
    updated = 0
    for g in data.get('glyphs', []):
        # ensure npc object exists
        npc = g.get('npc', {})
        name = npc.get('name') or g.get('npc', {}).get('name')
        if name:
            found = match_npc_images(name, images)
            if found:
                # set npc_images if missing or empty
                if not npc.get('npc_images'):
                    npc['npc_images'] = found
                    g['npc'] = npc
                    updated += 1
        # glyph image matches
        glyph_matches = match_images_for_glyph(g.get('glyph_name',''), images)
        if glyph_matches:
            if not g.get('glyph_images'):
                g['glyph_images'] = glyph_matches
                updated += 1
        # background_images already often present — ensure they are valid
        bgs = g.get('npc', {}).get('background_images', []) or g.get('background_images', [])
        valid_bgs = []
        for bg in bgs:
            if bg in images:
                valid_bgs.append(bg)
            else:
                # try find a close match in images containing tokens
                for img in images:
                    if any(t in img.lower() for t in tokens(bg)):
                        valid_bgs.append(img)
                        break
        if valid_bgs:
            # prefer npc.background_images
            if 'npc' in g:
                g['npc']['background_images'] = valid_bgs
            else:
                g['background_images'] = valid_bgs
    GO.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print('map_images_to_glyphs: updated entries:', updated)

if __name__ == '__main__':
    main()
