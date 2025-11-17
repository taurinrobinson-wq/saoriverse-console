#!/usr/bin/env python3
"""Create a review file of low-confidence glyphs for human annotation.

Usage: python3 tools/active_learning_review.py --source generated/gutenberg_texts_glyphs_with_dominant.json \
       --out learning/active_review/low_confidence_items.json --n 50
"""
from pathlib import Path
import json
import argparse
import datetime


def load_glyphs(path: Path):
    if not path.exists():
        raise SystemExit(f"Source glyph file not found: {path}")
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def select_low_confidence(glyphs, n=50, min_conf=None):
    # Compute confidence (default 0) and sort ascending
    for g in glyphs:
        g['_confidence'] = float(g.get('confidence') or 0.0)
    selected = sorted(glyphs, key=lambda x: x['_confidence'])
    if min_conf is not None:
        selected = [g for g in selected if g['_confidence'] <= float(min_conf)]
    return selected[:n]


def make_review_items(glyphs):
    items = []
    for g in glyphs:
        item = {
            'id': g.get('id'),
            'title': g.get('title') or g.get('name'),
            'dominant_emotion': g.get('dominant_emotion'),
            'dominant_score': g.get('dominant_score'),
            'confidence': g.get('confidence'),
            'keywords': g.get('keywords') or g.get('associated_keywords') or [],
            'frequency': g.get('frequency') or 0,
            'note': '',
        }
        items.append(item)
    return items


def ensure_out_dir(out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--source', default='generated/gutenberg_texts_glyphs_with_dominant.json')
    p.add_argument(
        '--out', default='learning/active_review/low_confidence_items.json')
    p.add_argument('--n', type=int, default=50)
    p.add_argument('--min-conf', type=float, default=None,
                   help='Only include items with confidence <= MIN_CONF')
    args = p.parse_args()

    src = Path(args.source)
    out = Path(args.out)

    glyphs = load_glyphs(src)
    selected = select_low_confidence(glyphs, n=args.n, min_conf=args.min_conf)
    review_items = make_review_items(selected)

    ensure_out_dir(out)
    payload = {
        'generated_from': str(src),
        'created_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'count': len(review_items),
        'items': review_items,
    }
    with out.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(review_items)} review items to: {out}")
    print("Next: open the file and annotate 'note' or correct 'dominant_emotion'.")


if __name__ == '__main__':
    main()
