#!/usr/bin/env python3
"""Import OpenStax phrase CSV and group phrases by headword lemma.

Produces: learning/user_overrides/openstax_psych_import.json

Usage: python3 tools/import_openstax_headword_lexicon.py --top 300
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict, Counter

try:
    import spacy
except Exception:
    spacy = None


CSV_PATH = "data/openstax_psych_phrases.csv"
OUT_PATH = "learning/user_overrides/openstax_psych_import.json"


def load_spacy():
    if spacy is None:
        print("spaCy is not installed. Install with: pip install spacy",
              file=sys.stderr)
        return None
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except Exception:
        try:
            # fallback to blank English model
            nlp = spacy.blank("en")
            return nlp
        except Exception:
            print("Failed to load or create a spaCy model.", file=sys.stderr)
            return None


def find_head_lemma(nlp, phrase):
    # Return a lemma string to use as signal name.
    if not nlp:
        # simple fallback: last token lowercased
        return phrase.strip().lower().split()[-1]
    doc = nlp(phrase)
    # prefer a token that is NOUN or PROPN; else take the rightmost content token
    for tok in doc:
        if tok.pos_ in ("NOUN", "PROPN"):
            return tok.lemma_.lower()
    # fallback: last non-punct token
    for tok in reversed(doc):
        if not tok.is_punct and not tok.is_space:
            return tok.lemma_.lower()
    return phrase.strip().lower()


def read_phrases(path):
    rows = []
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def build_headword_groups(rows, nlp=None, top_k_phrases=300):
    # Filter and take top_k_phrases by their order in CSV (assumed ranked)
    filtered = []
    unwanted_pos = {"PRON", "ADP", "PART",
                    "CCONJ", "DET", "PUNCT", "NUM", "SYM"}
    for r in rows:
        phrase = (r.get("phrase") or "").strip()
        pos = (r.get("pos") or "").strip()
        if not phrase:
            continue
        if len(phrase) < 3:
            continue
        if pos in unwanted_pos:
            continue
        # skip numeric phrases
        if any(ch.isdigit() for ch in phrase):
            continue
        filtered.append(r)
        if len(filtered) >= top_k_phrases:
            break

    groups = defaultdict(list)
    group_counts = Counter()
    for r in filtered:
        phrase = r.get("phrase").strip()
        head = find_head_lemma(nlp, phrase)
        groups[head].append(phrase)
        group_counts[head] += 1

    # Build signals dict
    signals = {}
    for head, phrases in groups.items():
        name = head.replace(" ", "_")
        signals[name] = {"frequency": group_counts[head],
                         "keywords": sorted(list(set(phrases)))}

    # Filter out stopwords and very low-frequency groups to reduce noise
    stopset = set()
    if nlp:
        stopset = set([s.lower() for s in nlp.Defaults.stop_words])
    else:
        stopset = {"the", "a", "an", "to", "of", "in", "and",
                   "or", "be", "is", "are", "for", "on", "by"}

    filtered_signals = {}
    for head, info in signals.items():
        plain_head = head.replace("_", " ")
        if plain_head in stopset:
            continue
        if info.get("frequency", 0) < 2:
            continue
        if len(plain_head) < 2:
            continue
        filtered_signals[head] = info

    return filtered_signals, group_counts


def write_lexicon(signals, out_path):
    payload = {"signals": signals}
    d = os.path.dirname(out_path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default=CSV_PATH)
    p.add_argument("--out", default=OUT_PATH)
    p.add_argument("--top", default=300, type=int,
                   help="Top phrases to consider (default 300)")
    p.add_argument("--preview", action="store_true",
                   help="Print preview of top groups")
    args = p.parse_args()

    try:
        rows = read_phrases(args.csv)
    except FileNotFoundError:
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        sys.exit(2)

    nlp = load_spacy()
    signals, counts = build_headword_groups(
        rows, nlp=nlp, top_k_phrases=args.top)

    # sort signals by frequency desc
    sorted_signals = dict(
        sorted(signals.items(), key=lambda kv: kv[1]["frequency"], reverse=True))
    write_lexicon(sorted_signals, args.out)
    print(f"Wrote lexicon: {args.out} (signals: {len(sorted_signals)})")

    if args.preview:
        import itertools
        print("\nTop 30 headword groups:")
        for i, (k, v) in enumerate(itertools.islice(sorted_signals.items(), 30), start=1):
            print(
                f"{i:02d}. {k} — {v['frequency']} keywords: {', '.join(v['keywords'][:6])}")


if __name__ == "__main__":
    main()
