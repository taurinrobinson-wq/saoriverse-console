#!/usr/bin/env python3
"""Filter and canonicalize seed tokens before synonym ingestion.

Usage examples:
  python3 scripts/filter_seeds.py --seed-file data/seeds.txt --out data/seeds.filtered.txt

This script normalizes tokens, lemmatizes (NLTK), removes stopwords and
generic tokens, and optionally removes multi-word seeds to reduce noise.
It produces a filtered seed file and a JSON report with basic stats.
"""
import argparse
import json
import re
from pathlib import Path
from collections import Counter

try:
    from nltk.stem import WordNetLemmatizer
    import nltk
    nltk.data.find('corpora/wordnet')
except Exception:
    # Defer download to runtime if needed
    WordNetLemmatizer = None

GENERIC_FILTER = {
    'thing', 'things', 'stuff', 'something', 'anything', 'everything',
    'item', 'items', 'object', 'objects', 'etc', 'etcetera'
}

STOPWORDS = {
    # small curated stopword set for seed filtering (not full English stopwords)
    'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'for', 'to', 'with',
    'by', 'from', 'at', 'into', 'over', 'under', 'about', 'as'
}


def normalize_token(t: str) -> str:
    t = (t or '').lower().strip()
    t = re.sub(r"[^\w\s'-]", '', t)
    t = re.sub(r"\s+", ' ', t)
    return t


def lemmatize_token(t: str, lemmatizer):
    if not lemmatizer:
        return t
    # If multiword, lemmatize each piece
    parts = t.split()
    parts = [lemmatizer.lemmatize(p) for p in parts]
    return ' '.join(parts)


def is_generic(t: str):
    return t in GENERIC_FILTER or t in STOPWORDS


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--seed-file', default='data/seeds.txt')
    p.add_argument('--out', default='data/seeds.filtered.txt')
    p.add_argument('--min-length', type=int, default=3,
                   help='Minimum token length (after normalization)')
    p.add_argument('--remove-multiword', action='store_true',
                   help='Drop multi-word seeds (recommended)')
    p.add_argument('--allow-nltk-download', action='store_true',
                   help='Download wordnet if missing')
    args = p.parse_args()

    lemmatizer = None
    if WordNetLemmatizer is not None:
        lemmatizer = WordNetLemmatizer()
    else:
        if args.allow_nltk_download:
            import nltk
            nltk.download('wordnet')
            from nltk.stem import WordNetLemmatizer as _L
            lemmatizer = _L()

    src = Path(args.seed_file)
    outp = Path(args.out)
    report_path = outp.with_suffix('.report.json')

    if not src.exists():
        print('Seed file not found:', src)
        return

    raw = [line.strip() for line in src.read_text(
        encoding='utf-8').splitlines() if line.strip()]
    normalized = [normalize_token(r) for r in raw]

    kept = []
    dropped_reasons = Counter()

    for token in normalized:
        if not token:
            dropped_reasons['empty'] += 1
            continue
        if is_generic(token):
            dropped_reasons['generic'] += 1
            continue
        if args.remove_multiword and len(token.split()) > 1:
            dropped_reasons['multiword'] += 1
            continue
        if len(token) < args.min_length:
            dropped_reasons['short'] += 1
            continue

        canon = lemmatize_token(token, lemmatizer)
        if is_generic(canon):
            dropped_reasons['generic_after_lemmatize'] += 1
            continue

        kept.append(canon)

    # dedupe preserving order
    seen = set()
    final = []
    for t in kept:
        if t not in seen:
            seen.add(t)
            final.append(t)

    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text('\n'.join(final) + '\n', encoding='utf-8')

    report = {
        'input_count': len(raw),
        'normalized_count': len(normalized),
        'kept_count': len(final),
        'dropped': dict(dropped_reasons),
        'example_kept_head': final[:50]
    }
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"Wrote {len(final)} filtered seeds to {outp}")
    print('Report:', report_path)


if __name__ == '__main__':
    main()
