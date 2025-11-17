#!/usr/bin/env python3
"""Convert a curated preview CSV (headword,frequency,keywords) into a lexicon JSON.

Input CSV columns expected:
- headword: the signal head (string)
- frequency: optional integer
- keywords: semicolon-separated keywords/phrases

Output path: `learning/user_overrides/openstax_psych_import_curated.json`
with structure matching other lexicons in the repo.
"""
from __future__ import annotations

import csv
import json
import os
import argparse


def parse_keywords(cell: str):
    if not cell:
        return []
    parts = [p.strip() for p in cell.split(";") if p.strip()]
    return parts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_csv",
                        default="data/openstax_psych_import_clean_preview.csv")
    parser.add_argument("--out", dest="out_json",
                        default="learning/user_overrides/openstax_psych_import_curated.json")
    args = parser.parse_args()

    if not os.path.exists(args.in_csv):
        print("Input CSV missing:", args.in_csv)
        return

    signals = {}
    with open(args.in_csv, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            head = (r.get("headword") or r.get("head") or "").strip()
            if not head:
                continue
            freq = r.get("frequency")
            try:
                freq_v = int(freq) if freq not in (None, "") else 0
            except Exception:
                freq_v = 0
            keywords = parse_keywords(
                r.get("keywords") or r.get("keywords; ") or "")
            signals[head] = {"frequency": freq_v, "keywords": keywords}

    out = {"signals": signals}
    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(
        f"Wrote curated lexicon JSON: {args.out_json} (signals: {len(signals)})")


if __name__ == "__main__":
    main()
