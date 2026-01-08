#!/usr/bin/env python3
"""Merge datamuse and wordnet synonym maps into a provenance-preserving JSON.

Writes: data/synonyms_merged.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DM_FILE = DATA_DIR / "datamuse_synonyms.json"
WN_FILE = DATA_DIR / "wordnet_synonyms.json"
OUT_FILE = DATA_DIR / "synonyms_merged.json"


def load_optional(path: Path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main():
    dm = load_optional(DM_FILE)
    wn = load_optional(WN_FILE)

    keys = set(dm.keys()) | set(wn.keys())
    merged = {}
    for k in sorted(keys):
        a = sorted(set(dm.get(k, [])))
        b = sorted(set(wn.get(k, [])))
        merged_list = sorted(set(a) | set(b))
        merged[k] = {"datamuse": a, "wordnet": b, "merged": merged_list}

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_FILE} with {len(merged)} seed entries")


if __name__ == "__main__":
    main()
