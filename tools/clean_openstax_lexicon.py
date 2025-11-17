#!/usr/bin/env python3
"""Clean OpenStax lexicon by removing metadata or low-value head signals.

Writes a cleaned lexicon JSON; does not overwrite original by default.

Usage:
  python3 tools/clean_openstax_lexicon.py --in learning/user_overrides/openstax_psych_import.json \
      --out learning/user_overrides/openstax_psych_import_clean.json
"""
import argparse
import json
import os
import sys
from typing import Set


DEFAULT_REMOVE = [
    "book",
    "openstax",
    "attribution",
    "author",
    "publication",
    "publisher",
    "format",
    "license",
    "creative",
    "commons",
    "page",
    "section",
    "website",
    "url",
    "citation",
    "book_title",
]


def load_lexicon(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_lexicon(payload, out_path: str):
    d = os.path.dirname(out_path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def normalize_head(s: str) -> str:
    return s.replace("_", " ").lower()


def should_remove(head: str, remove_set: Set[str]) -> bool:
    # Remove if exact match or contains any remove token
    nh = normalize_head(head)
    if nh in remove_set:
        return True
    for token in remove_set:
        if token in nh:
            return True
    # also remove very short heads or those with digits/punctuation only
    if len(nh) <= 1:
        return True
    return False


def clean_lexicon(payload: dict, remove_tokens: Set[str], min_frequency: int = 1):
    signals = payload.get("signals", {})
    kept = {}
    removed = []
    for head, info in signals.items():
        if should_remove(head, remove_tokens):
            removed.append(head)
            continue
        if info.get("frequency", 0) < min_frequency:
            removed.append(head)
            continue
        kept[head] = info
    out = {"signals": kept}
    return out, removed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--out", dest="outfile", required=True)
    p.add_argument("--remove", nargs="*", default=DEFAULT_REMOVE,
                   help="Extra tokens to remove (space-separated)")
    p.add_argument("--min-frequency", type=int, default=1,
                   help="Minimum frequency to keep a signal (default 1)")
    args = p.parse_args()

    payload = load_lexicon(args.infile)
    remove_set = set([t.lower() for t in args.remove])
    cleaned, removed = clean_lexicon(
        payload, remove_set, min_frequency=args.min_frequency)
    save_lexicon(cleaned, args.outfile)

    print(f"Wrote cleaned lexicon: {args.outfile}")
    print(f"Signals kept: {len(cleaned.get('signals', {}))}")
    print(f"Signals removed: {len(removed)}")
    if removed:
        print("Sample removed:", ", ".join(removed[:20]))


if __name__ == "__main__":
    main()
