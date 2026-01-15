#!/usr/bin/env python3
"""
Generate batch-friendly prompts for missing NPCs listed in `tools/missing_npcs.csv`.

Writes `output/generated/missing_npc_prompts.txt` containing lines `slug|prompt` suitable
for `tools/batch_generate_automatic1111.sh`.
"""
import csv
from pathlib import Path
import re

IN_CSV = Path('tools/missing_npcs.csv')
OUT_PROMPTS = Path('output/generated/missing_npc_prompts.txt')

# Known prompt templates for specific NPC names (lowercase key -> prompt)
TEMPLATES = {
    'archivist malrik': 'semi-realistic painterly portrait, older archivist man, tired scholarly face, layered robes and archival ornaments, thoughtful weary expression, soft lighting, chest-up, velinor aesthetic',
    'dakrin': 'semi-realistic painterly portrait, middle-aged woman, strong build, braided hair, ritual leathers, muted earth tones, iron armband, stoic expression, soft lighting, chest-up, velinor aesthetic',
    'elka': 'semi-realistic painterly portrait, contemplative woman, long loose hair, shrine robes pale blue and grey, subtle circuitry jewelry, serene expression, soft lighting, chest-up, gentle background, velinor aesthetic',
    'helia': 'semi-realistic painterly portrait, warm grounded woman, mid-forties, loose tied hair, healer wraps green and brown, herbs and cords, gentle compassionate expression, soft lighting, chest-up, velinor aesthetic',
    'high seer elenya': 'semi-realistic painterly portrait, austere priestess, middle-aged woman, ornate ritual robes, pale skin tones, eyes intense, serene yet commanding expression, soft dramatic lighting, chest-up, velinor aesthetic',
    'coren the mediator': 'semi-realistic painterly portrait, diplomatic middle-aged man, calm composed expression, travel-worn robes, gentle eyes, chest-up, soft lighting, velinor aesthetic',
    'kiv': 'semi-realistic painterly portrait, older wiry man, greying hair, clay-stained robes, pottery shard adornments, contemplative sorrowful expression, soft lighting, chest-up, velinor aesthetic',
    'lark': 'semi-realistic painterly portrait, strong mason mid-thirties, stone-dust wraps, tool belt, earnest protective expression, soft lighting, chest-up, velinor aesthetic',
    'lira': 'semi-realistic painterly portrait, young woman, lithe, thoughtful expression, simple woven garments, muted palette, chest-up, soft lighting, velinor aesthetic',
    'nordia the mourning singer': 'semi-realistic painterly portrait, grieving singer, late 30s, worn shawl, voice-worn face, sad compassionate eyes, chest-up, muted velinor palette, soft lighting',
    'orvak': 'semi-realistic painterly portrait, weathered man, merchant type, practical robe, cautious expression, chest-up, soft lighting, velinor aesthetic',
    'rasha': 'semi-realistic painterly portrait, harbor trader, mid-30s, sun-weathered skin, layered fabrics, alert expression, chest-up, muted palette, velinor aesthetic',
    'sealina': 'semi-realistic painterly portrait, gentle elder woman, quiet eyes, layered robes, chest-up, soft lighting, velinor aesthetic',
    'seyla': 'semi-realistic painterly portrait, sharp-featured woman early forties, archivist robes ochre and red, lineage markers, focused weary expression, soft lighting, chest-up, velinor aesthetic',
    'sybil': 'semi-realistic painterly portrait, enigmatic woman, mid-40s, layered shawls, watchful eyes, chest-up, muted palette, velinor aesthetic',
    'thalma': 'semi-realistic painterly portrait, stoic elder, desert robes, weathered hands, calm expression, chest-up, velinor aesthetic',
    'thoran': 'semi-realistic painterly portrait, sturdy man, mid-40s, labor-worn clothing, steady gaze, chest-up, muted palette, velinor aesthetic',
    'velka': 'semi-realistic painterly portrait, matriarchal figure, late 50s, dignified robes, steady compassionate expression, chest-up, velinor palette',
}


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def main():
    if not IN_CSV.exists():
        print('Missing CSV:', IN_CSV)
        return
    names = []
    with IN_CSV.open('r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if r['found'].strip().lower() == 'no':
                names.append(r['npc_name'].strip())

    # normalize and dedupe while preserving order
    seen = set()
    uniq = []
    for n in names:
        key = n.lower()
        if key not in seen:
            seen.add(key)
            uniq.append(n)

    OUT_PROMPTS.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PROMPTS.open('w', encoding='utf-8') as out:
        for n in uniq:
            # handle paired names like 'Juria & Korinth'
            if '&' in n or ' and ' in n.lower():
                parts = re.split(r'\s*&\s*|\s+and\s+', n)
                for p in parts:
                    key = p.strip().lower()
                    slug = slugify(p)
                    prompt = TEMPLATES.get(key, f'semi-realistic painterly portrait, {p.strip()}, chest-up, soft lighting, muted velinor palette')
                    out.write(f"{slug}|{prompt}\n")
                continue

            key = n.lower()
            slug = slugify(n)
            prompt = TEMPLATES.get(key)
            if not prompt:
                # fallback: generate simple prompt from name tokens
                tokens = [t for t in re.split(r'[^A-Za-z0-9]+', n) if t]
                descriptor = ' '.join(tokens[:3]).lower()
                prompt = f'semi-realistic painterly portrait, {descriptor}, chest-up, soft lighting, muted velinor palette'
            out.write(f"{slug}|{prompt}\n")

    print('Wrote prompts to', OUT_PROMPTS)


if __name__ == '__main__':
    main()
