#!/usr/bin/env python3
"""Filter multi-word candidates from OpenStax CSV, remove stopword-led phrases,
and rank/boost multi-word noun phrases using spaCy POS checks.

Outputs:
- `data/openstax_psych_phrases_multi_filtered.tsv`
- `data/openstax_psych_phrases_multi_filtered.json`
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
import sys

IN_CSV = Path("data/openstax_psych_phrases_full.csv")
OUT_TSV = Path("data/openstax_psych_phrases_multi_filtered.tsv")
OUT_JSON = Path("data/openstax_psych_phrases_multi_filtered.json")


def main():
    if not IN_CSV.exists():
        print("Missing input CSV:", IN_CSV)
        sys.exit(1)

    try:
        import spacy
    except Exception as e:
        print("spaCy import error:", e)
        raise

    nlp = spacy.load("en_core_web_sm")
    # build stopword blacklist: spaCy defaults plus a conservative custom list
    stop_blacklist = set([w.lower() for w in nlp.Defaults.stop_words])
    # expand custom blacklist with common prepositions, conjunctions, and weak tokens
    custom = {
        # articles, demonstratives, basic function words
        'of', 'the', 'in', 'on', 'and', 'or', 'for', 'to', 'by', 'with', 'a', 'an',
        'this', 'that', 'these', 'those', 'as', 'at', 'from',

        # common prepositions / connectors (expanded)
        'about', 'above', 'across', 'after', 'against', 'along', 'among', 'around',
        'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'but',
        'concerning', 'despite', 'during', 'except', 'inside', 'into', 'like', 'near',
        'of', 'off', 'onto', 'out', 'outside', 'over', 'past', 'regarding', 'since',
        'through', 'throughout', 'toward', 'towards', 'under', 'underneath', 'until',
        'up', 'upon', 'via', 'within', 'without',

        # temporal / discourse tokens
        'again', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',

        # quantifiers / determiners / modal-like
        'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'can', 'will', 'just', 'now', 'may', 'might', 'should', 'could'
    }
    stop_blacklist.update(custom)

    candidates = []
    with IN_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            phrase = (row.get("phrase") or "").strip()
            if not phrase or " " not in phrase:
                continue
            doc = nlp(phrase)
            first_alpha = next(
                (tok for tok in doc if not tok.is_space and not tok.is_punct), None)
            if first_alpha is None or first_alpha.is_stop:
                continue
            tokens_alpha = [tok for tok in doc if (
                tok.is_alpha or tok.like_num) and not tok.is_punct]
            if len(tokens_alpha) < 2:
                continue
            alpha_tokens = [tok for tok in tokens_alpha if re.search(
                r"[A-Za-z]", tok.text)]
            if len(alpha_tokens) < 1:
                continue
            # drop phrases that contain any stopword from the blacklist
            lower_tokens = [tok.text.lower() for tok in tokens_alpha]
            if any(t in stop_blacklist for t in lower_tokens):
                continue
            noun_like = sum(1 for tok in tokens_alpha if tok.pos_ in (
                "NOUN", "PROPN", "ADJ"))
            noun_score = noun_like / len(tokens_alpha)
            alpha_len = len(" ".join([tok.text for tok in alpha_tokens]))
            candidates.append((idx, phrase, row.get("lemmas", ""), row.get("pos", ""), (row.get(
                "example") or "").replace("\n", " "), row.get("source_urls", ""), noun_score, alpha_len))

    candidates.sort(key=lambda t: (-t[6], -t[7], t[0]))

    seen = set()
    filtered = []
    for tup in candidates:
        _, phrase, lemmas, pos, example, source_urls, noun_score, alpha_len = tup
        key = phrase.lower()
        if key in seen:
            continue
        seen.add(key)
        filtered.append({
            "phrase": phrase,
            "lemmas": lemmas,
            "pos": pos,
            "example": example,
            "source_urls": source_urls,
            "noun_score": round(float(noun_score), 3),
            "alpha_len": int(alpha_len),
        })

    # Write TSV using csv.writer for robust quoting
    with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["phrase", "lemmas", "pos", "example",
                        "source_urls", "noun_score"])
        for r in filtered:
            writer.writerow([
                r.get("phrase", ""),
                r.get("lemmas", ""),
                r.get("pos", ""),
                r.get("example", ""),
                r.get("source_urls", ""),
                "{:.3f}".format(r.get("noun_score", 0.0)),
            ])

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(filtered)} filtered candidates -> {OUT_TSV}, {OUT_JSON}")


if __name__ == "__main__":
    main()
