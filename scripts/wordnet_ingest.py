#!/usr/bin/env python3
"""Fetch synonyms from NLTK WordNet for a seed list.

Writes: data/wordnet_synonyms.json
"""
import argparse
import json
import re
from pathlib import Path

from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
OUT_FILE = DATA_DIR / 'wordnet_synonyms.json'

lemmatizer = WordNetLemmatizer()


def normalize_token(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"[^\w\s'-]", '', t)
    t = re.sub(r"\s+", ' ', t)
    return t


def get_wordnet_synonyms(word: str):
    norm = normalize_token(word)
    syns = set()
    for ss in wn.synsets(norm):
        for lemma in ss.lemmas():
            val = lemma.name().replace('_', ' ')
            val = normalize_token(val)
            val = lemmatizer.lemmatize(val)
            if val:
                syns.add(val)
    return sorted(syns)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--seed-file', default=DATA_DIR / 'seeds.txt')
    args = p.parse_args()

    seeds_path = Path(args.seed_file)
    if not seeds_path.exists():
        print(f"Seed file not found: {seeds_path}")
        return

    out = {}
    for line in seeds_path.read_text(encoding='utf-8').splitlines():
        word = line.strip()
        if not word:
            continue
        try:
            syns = get_wordnet_synonyms(word)
            out[word] = syns
            print(f"{word}: {len(syns)} wordnet hits")
        except Exception as e:
            print(f"Failed for {word}: {e}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(
        out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {OUT_FILE}")


if __name__ == '__main__':
    main()
