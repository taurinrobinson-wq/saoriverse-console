#!/usr/bin/env python3
"""Generate a seed word list from `data/glyph_lexicon_rows.json`.

This script extracts `glyph_name` tokens and writes a normalized
`data/seeds.txt` file (one seed per line).
"""
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
GLYPH_FILE = DATA_DIR / 'glyph_lexicon_rows.json'
SEEDS_OUT = DATA_DIR / 'seeds.txt'


def normalize_token(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"[^\w\s'-]", '', t)
    t = re.sub(r"\s+", ' ', t)
    return t


def main():
    if not GLYPH_FILE.exists():
        print(f"Glyph lexicon not found at {GLYPH_FILE}")
        return

    j = json.loads(GLYPH_FILE.read_text(encoding='utf-8'))
    seeds = []
    for entry in j:
        name = entry.get('glyph_name') or ''
        norm = normalize_token(name)
        # Add the full glyph name as a seed and also its words
        if norm:
            seeds.append(norm)
            for w in norm.split():
                if len(w) > 1:
                    seeds.append(w)

    # Add a few canonical emotional seeds if not present
    for extra in ('joy', 'grief', 'longing', 'ache', 'yearning', 'mourning'):
        seeds.append(extra)

    # Deduplicate while preserving order
    seen = set()
    out = []
    for s in seeds:
        if s not in seen:
            seen.add(s)
            out.append(s)

    SEEDS_OUT.parent.mkdir(parents=True, exist_ok=True)
    SEEDS_OUT.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f"Wrote {len(out)} seeds to {SEEDS_OUT}")


if __name__ == '__main__':
    main()
