import json
import csv
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / 'cipher_seeds.json'
OUT_CSV = ROOT / 'cipher_seeds.csv'
GLYPH_ORG = ROOT / 'Glyph_Organizer.json'
BACKUP = ROOT / 'Glyph_Organizer.json.cipher_backup'

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+")

def obfuscate_phrase_numeric(phrase, rng):
    # pick one random letter from each word token, convert to numeric A=01..Z=26,
    # fallback to ascii code % 100 for non-letters. Return both dash-separated numeric
    # string and a colon-separated display to evoke a digital-clock aesthetic.
    tokens = WORD_RE.findall(phrase)
    nums = []
    for t in tokens:
        if len(t) == 0:
            continue
        i = rng.randrange(len(t))
        ch = t[i]
        if ch.isalpha():
            val = ord(ch.upper()) - ord('A') + 1
        else:
            val = ord(ch) % 100
        nums.append(f"{val:02d}")
    dash = '-'.join(nums) if nums else ''
    colon = ':'.join(nums) if nums else ''
    return dash, colon


def generate(seed=None, apply_to_glyph_organizer=False):
    with SEEDS.open('r', encoding='utf-8') as f:
        data = json.load(f)

    rng = random.Random(seed)

    rows = []
    for domain in data['domains']:
        dname = domain['name']
        for cat in domain.get('categories', []):
            cname = cat['name']
            for phrase in cat.get('phrases', []):
                ob_dash, ob_colon = obfuscate_phrase_numeric(phrase, rng)
                rows.append({
                    'domain': dname,
                    'category': cname,
                    'phrase': phrase,
                    'first_view_obfuscation_numeric': ob_dash,
                    'first_view_display': ob_colon,
                })

    # write CSV
    with OUT_CSV.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['domain','category','phrase','first_view_obfuscation_numeric','first_view_display'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f'Wrote CSV to {OUT_CSV}')

    if apply_to_glyph_organizer:
        # backup
        if GLYPH_ORG.exists():
            GLYPH_ORG.rename(BACKUP)
            print(f'Backed up Glyph_Organizer.json -> {BACKUP}')
            # read backup to modify
            with BACKUP.open('r', encoding='utf-8') as f:
                org = json.load(f)
        else:
            org = {}
        # add a top-level key
        org['cipher_seeds'] = data
        with GLYPH_ORG.open('w', encoding='utf-8') as f:
            json.dump(org, f, ensure_ascii=False, indent=2)
        print(f'Applied cipher_seeds to {GLYPH_ORG}')

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, default=None, help='Random seed for obfuscation (optional)')
    p.add_argument('--apply', action='store_true', help='Apply seeds into Glyph_Organizer.json (makes a backup)')
    args = p.parse_args()
    generate(seed=args.seed, apply_to_glyph_organizer=args.apply)
