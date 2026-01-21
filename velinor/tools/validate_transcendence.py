#!/usr/bin/env python3
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORG = ROOT / "velinor" / "markdowngameinstructions" / "Glyph_Organizer.csv"
TR = ROOT / "velinor" / "markdowngameinstructions" / "Glyph_Transcendence.csv"

encodings = ['utf-8', 'utf-8-sig', 'latin-1']

def read_rows(path):
    for e in encodings:
        try:
            with open(path, newline='', encoding=e) as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception:
            continue
    raise RuntimeError(f"Failed reading {path} with tried encodings")

org_rows = read_rows(ORG)
tr_rows = read_rows(TR)

organizer_glyphs = set(r['Glyph'].strip() for r in org_rows if r.get('Glyph'))
transcendence_glyphs = set(r['Glyph'].strip() for r in tr_rows if r.get('Glyph'))

pattern = re.compile(r"Glyph of [^,\.\)]+")

missing = {}
all_refs = set()
for r in tr_rows:
    s = (r.get('Storyline') or '') + ' ' + (r.get('Theme') or '')
    found = pattern.findall(s)
    # strip whitespace
    found = [f.strip() for f in found]
    for f in found:
        all_refs.add(f)
        # ignore references that refer to transcendence glyphs (self-references)
        if f in transcendence_glyphs:
            continue
        if f not in organizer_glyphs:
            missing.setdefault(f, []).append(r.get('Glyph') or 'TRANS_ROW')

print(f"Organizer glyph count: {len(organizer_glyphs)}")
print(f"Transcendence referenced glyph count: {len(all_refs)}")
print()
if not missing:
    print('OK: All referenced glyphs are present in Glyph_Organizer.csv')
else:
    print('Missing glyph references (referenced -> transcendence rows):')
    for k,v in missing.items():
        print(f"  {k} -> {', '.join(v)}")

# Exit code non-zero if missing
import sys
sys.exit(0 if not missing else 2)
