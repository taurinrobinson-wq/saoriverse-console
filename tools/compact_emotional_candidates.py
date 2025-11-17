#!/usr/bin/env python3
"""Generate a compact CSV of top emotional candidate phrases.

Reads `data/openstax_psych_phrases_emotional.csv`, filters by blacklist and
boilerplate, and writes top-N rows to
`data/openstax_psych_phrases_emotional_compact.csv`.
"""
from __future__ import annotations

import csv
import os
import re
import argparse


def tokenize_text(s: str):
    return re.findall(r"[A-Za-z0-9]+", (s or "").lower())


def is_boilerplate(s: str) -> bool:
    if not s:
        return True
    low = s.lower()
    if any(tok in low for tok in ("openstax", "creative commons", "access for free", "publisher/website", "authors:", "support center", "terms of use", "licensing", "privacy policy")):
        return True
    if re.search(r"^https?://", low):
        return True
    # short non-informative tokens
    toks = tokenize_text(low)
    if len(toks) <= 1 and len(low) < 6:
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_csv",
                        default="data/openstax_psych_phrases_emotional.csv")
    parser.add_argument("--out", dest="out_csv",
                        default="data/openstax_psych_phrases_emotional_compact.csv")
    parser.add_argument("--top", type=int, default=150)
    parser.add_argument("--blacklist", type=str,
                        default="houston,texas,lovett,spielman,jenkins,m.,j.,d.,openstax,book,author,publisher")
    args = parser.parse_args()

    blacklist = set(x.strip().lower()
                    for x in args.blacklist.split(",") if x.strip())

    if not os.path.exists(args.in_csv):
        print("Input CSV missing:", args.in_csv)
        return

    rows = []
    with open(args.in_csv, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)

    def bad(r):
        phrase = (r.get("phrase") or "").lower()
        lemmas = (r.get("lemmas") or "").lower()
        example = (r.get("example") or "").lower()
        # blacklist token presence
        for b in blacklist:
            if b and (b in phrase or b in lemmas or b in example):
                return True
        # boilerplate
        if is_boilerplate(phrase) or is_boilerplate(example):
            return True
        return False

    filtered = [r for r in rows if not bad(r)]
    # ensure numeric score exists; default to 0
    for r in filtered:
        try:
            r["score"] = float(r.get("score", 0))
        except Exception:
            r["score"] = 0.0

    filtered.sort(key=lambda x: x["score"], reverse=True)

    top = filtered[: args.top]
    os.makedirs(os.path.dirname(args.out_csv) or ".", exist_ok=True)
    if top:
        fields = list(top[0].keys())
    else:
        fields = ["phrase", "lemmas", "pos", "example", "source_urls", "score"]

    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in top:
            w.writerow(r)

    print(f"Wrote compact CSV: {args.out_csv} (rows: {len(top)})")


if __name__ == "__main__":
    main()
