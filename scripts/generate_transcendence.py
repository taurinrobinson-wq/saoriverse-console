#!/usr/bin/env python3
"""
Generate candidate Transcendence/fusion glyphs from existing glyphs.
Produces velinor/markdowngameinstructions/Glyph_Transcendence_Auto.csv

Behavior:
- Reads velinor/markdowngameinstructions/Glyph_Organizer.csv (excludes existing Transcendence rows)
- Generates a set of triglyph (3-glyph) candidates sampling triples across distinct categories
- Generates a set of octoglyph (8-glyph) candidates by selecting one per category + one extra
- Writes a CSV with a short generated storyline template
"""
import csv
import random
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORG = ROOT / "velinor" / "markdowngameinstructions" / "Glyph_Organizer.csv"
OUT = ROOT / "velinor" / "markdowngameinstructions" / "Glyph_Transcendence_Auto.csv"

random.seed(42)

def read_glyphs(path):
    glyphs = []
    # Try common encodings in fallbacks to avoid decode errors from legacy files
    encodings = ['utf-8', 'utf-8-sig', 'latin-1']
    for enc in encodings:
        try:
            with open(path, newline='', encoding=enc) as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r['Category'].strip().lower() == 'transcendence':
                        continue
                    glyphs.append({
                        'category': r['Category'].strip(),
                        'count': r['Count'].strip(),
                        'theme': r['Theme'].strip(),
                        'npc': r['NPC Giver'].strip(),
                        'glyph': r['Glyph'].strip(),
                        'location': r['Location'].strip(),
                        'story': r['Storyline'].strip()
                    })
            return glyphs
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError('utf-8', b'', 0, 1, 'Failed to decode file with tried encodings')


def group_by_category(glyphs):
    d = {}
    for g in glyphs:
        d.setdefault(g['category'], []).append(g)
    return d


def short_name(g):
    # condense glyph name to a short token for generated titles
    return ''.join(word for word in g.split()[:3])


def make_triglyphs(cat_map, max_candidates=30):
    # Choose triples from distinct categories
    categories = list(cat_map.keys())
    triples = []
    # all unique triples of categories
    for cat_combo in combinations(categories, 3):
        # combinatorial: sample one glyph choice per category
        for _ in range(1):
            choice = [random.choice(cat_map[c]) for c in cat_combo]
            triples.append(choice)
    random.shuffle(triples)
    triples = triples[:max_candidates]
    out = []
    for i, triple in enumerate(triples, start=1):
        names = [t['glyph'] for t in triple]
        npcs = ', '.join([t['npc'] or 'Unknown' for t in triple])
        title = f"Triglyph of {' / '.join([n.split()[0] for n in names])}"
        location = f"Procedural Triglyph Chamber #{i}"
        story = f"Fusion of {names[0]}, {names[1]}, and {names[2]}. Boss encounter resolves overlapping grief by requiring the player to apply the three emotional acts: {triple[0]['theme']}; {triple[1]['theme']}; {triple[2]['theme']}. NPCs involved: {npcs}."
        out.append({
            'Category': 'Transcendence',
            'Count': str(i),
            'Theme': 'Unity, transformation, resolution',
            'NPC Giver': npcs,
            'Glyph': title,
            'Location': location,
            'Storyline': story
        })
    return out


def make_octoglyphs(cat_map, max_candidates=10):
    categories = list(cat_map.keys())
    # We'll generate candidates by selecting one glyph from each category and one extra random glyph
    out = []
    for i in range(1, max_candidates+1):
        pick = [random.choice(cat_map[c]) for c in categories]
        extra_cat = random.choice(categories)
        pick.append(random.choice(cat_map[extra_cat]))
        names = [p['glyph'] for p in pick]
        npcs = ', '.join([p['npc'] or 'Unknown' for p in pick])
        title = f"Octoglyph of Resonant Paths #{i}"
        location = f"Procedural Octoglyph Chamber #{i}"
        story = f"Fusion of: {', '.join(names)}. This sentinel tests the player's integrated mastery of {', '.join(categories)}. NPCs: {npcs}."
        out.append({
            'Category': 'Transcendence',
            'Count': str(100 + i),
            'Theme': 'Unity, transformation, resolution',
            'NPC Giver': npcs,
            'Glyph': title,
            'Location': location,
            'Storyline': story
        })
    return out


def write_out(rows, path):
    fieldnames = ['Category','Count','Theme','NPC Giver','Glyph','Location','Storyline']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    glyphs = read_glyphs(ORG)
    cat_map = group_by_category(glyphs)
    trig = make_triglyphs(cat_map, max_candidates=30)
    octs = make_octoglyphs(cat_map, max_candidates=8)
    all_rows = trig + octs
    write_out(all_rows, OUT)
    print(f"Wrote {len(all_rows)} candidate transcendence glyphs to {OUT}")

if __name__ == '__main__':
    main()
