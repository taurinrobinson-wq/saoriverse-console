#!/usr/bin/env python3
import json
import csv
import os

JSON_PATH = os.path.join('emotional_os', 'parser', 'signal_lexicon.json')
CSV_PATH = os.path.join('tools', 'lexicon_summary.csv')


def safe_len_examples(examples):
    if not examples:
        return 0, 0
    try:
        count = len(examples)
        chars = sum(len(e) for e in examples if isinstance(e, str))
        return count, chars
    except Exception:
        # examples may be a big string
        try:
            s = '\n'.join(examples)
            return s.count('\n')+1, len(s)
        except Exception:
            return 0, 0


def main():
    with open(JSON_PATH, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    signals = data.get('signals', {})
    rows = []
    for name, info in signals.items():
        keywords = info.get('keywords') or []
        examples = info.get('examples') or []
        examples_count, examples_chars = safe_len_examples(examples)
        frequency = info.get('frequency')
        community = info.get('community_contributed', False)
        rows.append({
            'signal': name,
            'frequency': frequency if frequency is not None else '',
            'keywords_count': len(keywords),
            'examples_count': examples_count,
            'examples_chars': examples_chars,
            'community_contributed': bool(community)
        })

    # sort by frequency desc (None last) then signal name
    def freq_key(r):
        f = r['frequency']
        return (-(f if isinstance(f, (int, float)) else 0), r['signal'])
    rows.sort(key=freq_key)

    os.makedirs('tools', exist_ok=True)
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=[
                                'signal', 'frequency', 'keywords_count', 'examples_count', 'examples_chars', 'community_contributed'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    total = len(rows)
    print(f'Wrote {CSV_PATH} with {total} signals')


if __name__ == '__main__':
    main()
