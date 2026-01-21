import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / 'cipher_seeds.json'
OBF = ROOT / 'cipher_obfuscations.txt'

with SEEDS.open('r', encoding='utf-8') as f:
    seeds = json.load(f)

# Build list of all phrases
phrases = []
for domain in seeds['domains']:
    for cat in domain.get('categories', []):
        for p in cat.get('phrases', []):
            phrases.append(p)

# Helper: convert '25-02' to letters 'Y','B'

def num_to_letter(num_str):
    try:
        n = int(num_str)
    except:
        return '?'
    if 1 <= n <= 26:
        return chr(ord('A') + n - 1)
    # fallback: map others to '?'
    return '?'

# Tokenize phrase into words (alphanumeric tokens)
import re
WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+")

def tokens(phrase):
    return WORD_RE.findall(phrase)

# Read obfuscations
with OBF.open('r', encoding='utf-8') as f:
    lines = [ln.strip() for ln in f if ln.strip()]

results = []
for ln in lines:
    nums = ln.split('-')
    letters = [num_to_letter(n) for n in nums]
    # Now find matching phrases: phrases whose token count == len(nums) and each token contains the letter (case-insensitive)
    matches = []
    for p in phrases:
        toks = tokens(p)
        if len(toks) != len(letters):
            continue
        ok = True
        for tok, L in zip(toks, letters):
            if L == '?':
                ok = False
                break
            if L.lower() not in tok.lower():
                ok = False
                break
        if ok:
            matches.append(p)
    results.append((ln, ''.join(letters), len(matches), matches if len(matches)<=10 else matches[:10]))

# print summary
for ln, letstr, cnt, m in results:
    print(f"{ln} -> {letstr} | matches: {cnt}")
    if cnt <= 10:
        for mm in m:
            print(f"  - {mm}")
    else:
        print(f"  - (showing first 10 of {cnt})")

# Also produce a simple vulnerability report
vuln = [r for r in results if r[2] == 1]
print('\nVULNERABLE (unique match) count:', len(vuln))
for ln, letstr, cnt, m in vuln:
    print(ln, '->', letstr, '=>', m[0])
