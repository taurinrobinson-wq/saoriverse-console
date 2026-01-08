#!/usr/bin/env python3
"""Fetch synonyms from Datamuse for a seed list.

Usage: python scripts/datamuse_ingest.py --seed-file data/seeds.txt
Writes: data/datamuse_synonyms.json and cached per-word JSON under cache/datamuse/
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CACHE_DIR = ROOT / "cache" / "datamuse"
OUT_FILE = DATA_DIR / "datamuse_synonyms.json"

HEADERS = {"User-Agent": "firstperson-synonym-ingest/1.0 (+https://example.org)"}


def normalize_token(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"[^\w\s'-]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def session_with_retries():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def fetch_synonyms(session, word: str, force=False):
    key = normalize_token(word)
    cache_path = CACHE_DIR / f"{key}.json"
    if cache_path.exists() and not force:
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    url = "https://api.datamuse.com/words"
    params = {"rel_syn": word, "max": 100}
    resp = session.get(url, params=params, headers=HEADERS, timeout=8)
    resp.raise_for_status()
    items = [normalize_token(e["word"]) for e in resp.json() if "word" in e]
    # preserve order and dedupe
    out = list(dict.fromkeys(items))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    time.sleep(0.12)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed-file", default=DATA_DIR / "seeds.txt")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    seeds_path = Path(args.seed_file)
    if not seeds_path.exists():
        print(f"Seed file not found: {seeds_path}")
        return

    session = session_with_retries()
    out = {}
    for line in seeds_path.read_text(encoding="utf-8").splitlines():
        word = line.strip()
        if not word:
            continue
        try:
            syns = fetch_synonyms(session, word, force=args.force)
            out[word] = syns
            print(f"{word}: {len(syns)} datamuse hits")
        except Exception as e:
            print(f"Failed for {word}: {e}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
