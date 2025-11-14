#!/usr/bin/env python3
"""Filter merged synonyms to remove multi-word, short, numeric or low-quality items.

Reads a merged synonym map produced by `scripts/merge_synonyms.py` with the
structure:
  { seed: { 'datamuse': [...], 'wordnet': [...], 'merged': [...] } }

Writes a filtered map with the same structure plus a `filtered` list and
produces a small JSON report with counts.

Usage:
  python3 scripts/filter_synonyms.py --in data/synonyms_merged.json --out data/synonyms_filtered.json

This script intentionally avoids any external API calls.
"""
import argparse
import json
import re
from pathlib import Path
from collections import Counter

GENERIC_FILTER = {
    'thing', 'things', 'stuff', 'something', 'anything', 'everything',
    'item', 'items', 'object', 'objects', 'etc', 'etcetera', 'one', 'ones'
}


def is_low_quality(token: str, min_len: int) -> bool:
    if not token:
        return True
    # Remove tokens with digits or weird punctuation
    if re.search(r"\d", token):
        return True
    # token should be alphabetic (allow hyphen and apostrophe)
    if not re.match(r"^[\w\-']+$", token):
        return True
    # too short
    if len(token.replace("-", "").replace("'", "")) < min_len:
        return True
    # generic
    if token in GENERIC_FILTER:
        return True
    return False


def filter_syn_list(syns, remove_multiword: bool, min_len: int):
    kept = []
    removed = []
    for s in syns:
        s_norm = s.strip().lower()
        if not s_norm:
            removed.append((s, 'empty'))
            continue
        if remove_multiword and ' ' in s_norm:
            removed.append((s, 'multiword'))
            continue
        if is_low_quality(s_norm, min_len):
            removed.append((s, 'low_quality'))
            continue
        kept.append(s_norm)
    # dedupe preserving order
    out = []
    seen = set()
    for t in kept:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out, removed


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--in', dest='infile', default='data/synonyms_merged.json')
    p.add_argument('--out', dest='outfile',
                   default='data/synonyms_filtered.json')
    p.add_argument('--report', dest='report',
                   default='data/synonyms_filtered.report.json')
    p.add_argument('--remove-multiword', action='store_true',
                   help='Drop multi-word synonyms')
    p.add_argument('--min-length', type=int, default=3,
                   help='Minimum alphabetic token length')
    args = p.parse_args()

    infile = Path(args.infile)
    outfile = Path(args.outfile)
    reportp = Path(args.report)

    if not infile.exists():
        print('Input file not found:', infile)
        return

    data = json.loads(infile.read_text(encoding='utf-8'))
    filtered = {}
    global_stats = Counter()
    sample_removed = {}

    for seed, block in data.items():
        dm = block.get('datamuse', [])
        wn = block.get('wordnet', [])
        merged = block.get('merged', [])

        dm_f, dm_removed = filter_syn_list(
            dm, args.remove_multiword, args.min_length)
        wn_f, wn_removed = filter_syn_list(
            wn, args.remove_multiword, args.min_length)
        mg_f, mg_removed = filter_syn_list(
            merged, args.remove_multiword, args.min_length)

        filtered[seed] = {
            'datamuse': dm_f,
            'wordnet': wn_f,
            'merged': mg_f,
            'filtered_out': {
                'datamuse': [r for r in dm_removed],
                'wordnet': [r for r in wn_removed],
                'merged': [r for r in mg_removed]
            }
        }

        global_stats['seeds'] += 1
        global_stats['datamuse_total'] += len(dm)
        global_stats['datamuse_kept'] += len(dm_f)
        global_stats['wordnet_total'] += len(wn)
        global_stats['wordnet_kept'] += len(wn_f)
        global_stats['merged_total'] += len(merged)
        global_stats['merged_kept'] += len(mg_f)

        # store a small sample of removed
        sample_removed[seed] = {
            'datamuse_removed_sample': [r for r in dm_removed[:6]],
            'wordnet_removed_sample': [r for r in wn_removed[:6]],
            'merged_removed_sample': [r for r in mg_removed[:6]]
        }

    outfile.write_text(json.dumps(
        filtered, ensure_ascii=False, indent=2), encoding='utf-8')
    report = {
        'global_stats': dict(global_stats),
        'remove_multiword': bool(args.remove_multiword),
        'min_length': args.min_length,
        'sample_removed_by_seed': {k: v for k, v in list(sample_removed.items())[:50]}
    }
    reportp.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Wrote filtered synonyms to {outfile} (report: {reportp})')


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Filter merged synonyms to remove multi-word, short, or low-quality suggestions.

Usage:
  python3 scripts/filter_synonyms.py --in data/synonyms_merged.json --out data/synonyms_merged.filtered.json

Default behavior:
 - Remove multi-word suggestions (contains whitespace)
 - Remove tokens shorter than `min_length` (default 3)
 - Remove overly generic tokens (e.g., 'thing', 'stuff')
 - Remove tokens with excessive punctuation or that are mostly numeric

Output:
 - Writes filtered JSON preserving provenance keys (`datamuse`, `wordnet`, `merged`).
 - Writes a report JSON with counts at `data/synonyms_merged.filtered.report.json` by default.
"""

GENERIC_FILTER = {
    'thing', 'things', 'stuff', 'something', 'anything', 'everything',
    'item', 'items', 'object', 'objects', 'etc', 'etcetera'
}

PUNCT_RE = re.compile(r"[^\w\s'-]")


def normalize_candidate(s: str) -> str:
    if s is None:
        return ''
    t = s.lower().strip()
    # remove excessive punctuation but keep hyphens/apostrophes
    t = PUNCT_RE.sub('', t)
    t = re.sub(r"\s+", ' ', t)
    return t


def is_multiword(s: str) -> bool:
    return ' ' in s.strip()


def is_low_quality(s: str, min_length: int) -> bool:
    if not s:
        return True
    if len(s) < min_length:
        return True
    if s in GENERIC_FILTER:
        return True
    # tokens that are mostly numeric or punctuation
    alnum = re.sub(r"[^0-9a-zA-Z]", '', s)
    if len(alnum) == 0:
        return True
    if len(alnum) / max(1, len(s)) < 0.5:
        return True
    return False


def filter_list(cands, min_length, remove_multiword):
    kept = []
    removed_reasons = Counter()
    for c in cands:
        orig = c
        norm = normalize_candidate(c)
        if remove_multiword and is_multiword(norm):
            removed_reasons['multiword'] += 1
            continue
        if is_low_quality(norm, min_length):
            removed_reasons['low_quality'] += 1
            continue
        kept.append(norm)
    return kept, removed_reasons


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--in', dest='infile', default='data/synonyms_merged.json')
    p.add_argument('--out', dest='outfile',
                   default='data/synonyms_merged.filtered.json')
    p.add_argument('--report', dest='report',
                   default='data/synonyms_merged.filtered.report.json')
    p.add_argument('--min-length', type=int, default=3)
    p.add_argument('--remove-multiword', action='store_true', default=True)
    p.add_argument('--keep-top', type=int, default=0,
                   help='If >0, keep only top-N merged candidates per seed')
    args = p.parse_args()

    infile = Path(args.infile)
    outfile = Path(args.outfile)
    reportp = Path(args.report)

    if not infile.exists():
        print('Input not found:', infile)
        return

    data = json.loads(infile.read_text(encoding='utf-8'))
    out = {}
    global_removed = Counter()

    for seed, entry in data.items():
        dm = entry.get('datamuse', [])
        wn = entry.get('wordnet', [])
        merged = entry.get('merged', [])

        dm_f, r1 = filter_list(dm, args.min_length, args.remove_multiword)
        wn_f, r2 = filter_list(wn, args.min_length, args.remove_multiword)
        merged_f, r3 = filter_list(
            merged, args.min_length, args.remove_multiword)

        # optional: if keep_top>0, limit merged_f to first N
        if args.keep_top and args.keep_top > 0:
            merged_f = merged_f[:args.keep_top]

        out[seed] = {'datamuse': dm_f, 'wordnet': wn_f, 'merged': merged_f}
        for k, v in r1.items():
            global_removed[k] += v
        for k, v in r2.items():
            global_removed[k] += v
        for k, v in r3.items():
            global_removed[k] += v

    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(
        out, ensure_ascii=False, indent=2), encoding='utf-8')

    report = {
        'seeds_processed': len(data),
        'seeds_kept': sum(1 for v in out.values() if v.get('merged')),
        'total_removed_reasons': dict(global_removed)
    }
    reportp.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Wrote filtered synonyms to {outfile} (seeds:{len(data)})')
    print('Report:', reportp)


if __name__ == '__main__':
    main()
