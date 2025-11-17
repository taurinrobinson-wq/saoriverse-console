#!/usr/bin/env python3
"""
Prune a lexicon JSON by removing pronouns, determiners and common stopwords.

Reads `learning/user_overrides/gutenberg_texts_lexicon.json` by default and
writes `learning/user_overrides/gutenberg_texts_lexicon_pruned.json`.

Heuristics:
- Remove phrases where every token is a pronoun/determiner/stopword.
- Remove phrases that are 1-2 character tokens (e.g., 'a', 'I').
"""
from __future__ import annotations

import json
import argparse
import re
from pathlib import Path


STOPWORDS = set([
    # pronouns
    'i', 'me', 'you', 'he', 'him', 'she', 'her', 'it', 'we', 'us', 'they', 'them',
    'my', 'your', 'his', 'hers', 'our', 'their', 'mine', 'yours', 'ours', 'theirs',
    # determiners / articles
    'the', 'a', 'an', 'this', 'that', 'these', 'those',
    # common function words
    'and', 'or', 'but', 'if', 'then', 'else', 'of', 'in', 'to', 'for', 'with', 'on', 'at', 'by', 'from', 'as',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'not', 'no', 'yes', 'so', 'such', 'very', 'more', 'most', 'some', 'any', 'all', 'other', 'that', 'which',
    # short stop tokens
    'the', 'a', 'an', 'this', 'those'
])


def normalize(phrase: str) -> list:
    # split on whitespace and strip punctuation
    toks = []
    for t in re.split(r"\s+", phrase.strip()):
        t2 = re.sub(r"[^a-zA-Z0-9'-]", '', t).lower()
        if t2:
            toks.append(t2)
    return toks


def is_pronoun_or_stop(phrase: str) -> bool:
    toks = normalize(phrase)
    if not toks:
        return True
    # if all tokens are in STOPWORDS or are 1-2 char tokens, consider it stop
    nonstop = [t for t in toks if (t not in STOPWORDS and len(t) > 2)]
    return len(nonstop) == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='in_json',
                        default='learning/user_overrides/gutenberg_texts_lexicon.json')
    parser.add_argument('--out', dest='out_json',
                        default='learning/user_overrides/gutenberg_texts_lexicon_pruned.json')
    args = parser.parse_args()

    in_path = Path(args.in_json)
    out_path = Path(args.out_json)

    if not in_path.exists():
        print('Input lexicon not found:', in_path)
        return 1

    data = json.loads(in_path.read_text(encoding='utf-8'))
    signals = data.get('signals', {})

    pruned = {}
    removed = 0
    for phrase, info in signals.items():
        if is_pronoun_or_stop(phrase):
            removed += 1
            continue
        # keep phrase
        pruned[phrase] = info

    out = {'signals': pruned}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(
        out, indent=2, ensure_ascii=False), encoding='utf-8')

    print(
        f'Pruned lexicon written: {out_path} (kept: {len(pruned)}, removed: {removed})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
