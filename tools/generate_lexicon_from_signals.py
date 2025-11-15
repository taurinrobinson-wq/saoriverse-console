#!/usr/bin/env python3
"""
Create a lexicon JSON from a signals CSV for use with `poetry_glyph_generator.py`.

Input CSV columns expected: file,chunk_index,keyword,signal,confidence,source

Output structure (example):
{
  "signals": {
    "love": {"frequency": 123, "keywords": ["love", "affection"]},
    ...
  }
}
"""

import csv
import json
from pathlib import Path
from collections import defaultdict, Counter
import argparse


def build_lexicon(csv_path: Path, out_path: Path, min_freq: int = 1):
    counts = Counter()
    keywords = defaultdict(Counter)

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sig = (row.get('signal') or '').strip()
            kw = (row.get('keyword') or '').strip()
            if not sig:
                continue
            counts[sig] += 1
            if kw:
                keywords[sig][kw] += 1

    signals = {}
    for sig, freq in counts.items():
        if freq < min_freq:
            continue
        kw_list = [k for k, _ in keywords[sig].most_common(12)]
        signals[sig] = {
            'frequency': freq,
            'keywords': kw_list
        }

    lexicon = {'signals': signals}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        json.dump(lexicon, f, indent=2)

    print(f"Wrote lexicon with {len(signals)} signals to {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--csv', default='data/processed_poetry_signals/openstax_signals.csv')
    parser.add_argument(
        '--out', default='learning/user_overrides/openstax_bulk_lexicon.json')
    parser.add_argument('--min-freq', type=int, default=1)
    args = parser.parse_args()

    csv_path = Path(args.csv)
    out_path = Path(args.out)

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return 2

    build_lexicon(csv_path, out_path, args.min_freq)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
