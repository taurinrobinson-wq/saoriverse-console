#!/usr/bin/env python3
"""Convert pruned reranked CSV into a curated lexicon JSON.

Reads `data/openstax_psych_phrases_emotional_compact_pruned.csv` by default
and writes `learning/user_overrides/openstax_psych_import_curated.json`.

Mapping:
- CSV `phrase` -> lexicon headword
- `score` is converted to an integer frequency (score * 10)
- `keywords` left empty
"""
from __future__ import annotations

import csv
import json
import os
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_csv",
                        default="data/openstax_psych_phrases_emotional_compact_pruned.csv")
    parser.add_argument("--out", dest="out_json",
                        default="learning/user_overrides/openstax_psych_import_curated.json")
    args = parser.parse_args()

    if not os.path.exists(args.in_csv):
        print("Input missing:", args.in_csv)
        return

    signals = {}
    with open(args.in_csv, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            phrase = (r.get("phrase") or "").strip()
            if not phrase:
                continue
            try:
                score = float(r.get("score") or 0.0)
            except Exception:
                score = 0.0
            freq = int(round(score * 10))
            signals[phrase] = {"frequency": freq, "keywords": []}

    out = {"signals": signals}
    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(
        f"Wrote curated lexicon JSON: {args.out_json} (signals: {len(signals)})")


if __name__ == "__main__":
    main()
