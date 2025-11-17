#!/usr/bin/env python3
"""Apply human review corrections produced from `active_learning_review.py`.

This script accepts a JSON file with corrected items (same shape as the review file,
but where reviewers may update `dominant_emotion`, `note`, or `keywords`). Corrections
are appended to `learning/user_overrides/reviewed_corrections.json` and logged to
`learning/hybrid_learning_log.jsonl` for traceability.

Usage: python3 tools/apply_review_corrections.py --in learning/active_review/low_confidence_items.corrected.json
"""
from pathlib import Path
import json
import argparse
import datetime


DEFAULT_OUT = Path('learning/user_overrides/reviewed_corrections.json')
LOG_FILE = Path('learning/hybrid_learning_log.jsonl')


def load_input(path: Path):
    if not path.exists():
        raise SystemExit(f"Corrections file not found: {path}")
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def append_corrections(corrections, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if out_path.exists():
        try:
            with out_path.open('r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []
    # Merge by id (simple append for now)
    for item in corrections:
        existing.append(item)
    with out_path.open('w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


def append_log(corrections, log_path: Path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    for item in corrections:
        entry = {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'source': 'active_review',
            'id': item.get('id'),
            'correction': item,
        }
        with log_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--in', dest='infile', required=True,
                   help='Corrected review JSON file')
    p.add_argument('--out', dest='out', default=str(DEFAULT_OUT),
                   help='Where to write corrected overrides')
    p.add_argument('--log', dest='log', default=str(LOG_FILE),
                   help='Append corrections to this log file (jsonl)')
    args = p.parse_args()

    inp = Path(args.infile)
    out = Path(args.out)
    log = Path(args.log)

    payload = load_input(inp)
    # Payload may contain {items: [...]}
    items = payload.get('items') if isinstance(
        payload, dict) and 'items' in payload else payload
    if not isinstance(items, list):
        raise SystemExit(
            'Invalid corrections format: expected a list or {items: [...]}')

    append_corrections(items, out)
    append_log(items, log)

    print(f"Appended {len(items)} corrections to: {out}")
    print(f"Logged {len(items)} corrections to: {log}")


if __name__ == '__main__':
    main()
