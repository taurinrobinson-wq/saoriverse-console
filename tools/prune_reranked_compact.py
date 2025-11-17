#!/usr/bin/env python3
"""Prune a reranked OpenStax compact CSV to remove stopword/function-word noise.

Writes `data/openstax_psych_phrases_emotional_compact_pruned.csv`.

Heuristics:
- Drop low-score rows (score < 1.0)
- Drop phrases composed mostly of stopwords or obvious boilerplate bigrams
- Drop single-token function words and pronouns
"""
from __future__ import annotations

import csv
import re
import os
from typing import List


STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "for", "to", "and", "or", "is", "are",
    "that", "this", "it", "we", "you", "they", "he", "she", "as", "with", "by",
    "from", "be", "was", "were", "has", "have", "had", "at", "which", "their",
    "our", "its", "these", "those", "but", "not", "such", "there", "then",
}

BLACKLIST_PHRASES = {
    "of the", "in the", "tend to", "for example", "et al", "our mission", "educational access",
    "the united states", "united states", "in this", "on the", "is a", "that the", "of a",
}

# common proper-name tokens to drop (lowercase)
PROPER_NAME_BLACKLIST = {"freud", "skinner", "wundt",
                         "rogers", "eysenck", "mischel", "maslow"}


def tokenize(s: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", (s or "").lower())


def should_keep(row: dict, score_threshold: float = 1.0) -> bool:
    phrase = (row.get("phrase") or "").strip()
    if not phrase:
        return False
    try:
        score = float(row.get("score") or 0.0)
    except Exception:
        score = 0.0

    if score < score_threshold:
        return False

    low = phrase.lower()
    if low in BLACKLIST_PHRASES:
        return False

    toks = tokenize(phrase)
    if not toks:
        return False

    token_count = len(toks)
    stop_count = sum(1 for t in toks if t in STOPWORDS)
    stop_frac = stop_count / token_count

    # Drop single-token stopwords/pronouns
    if token_count == 1 and toks[0] in STOPWORDS:
        return False

    # Drop if majority of tokens are stopwords
    if stop_frac > 0.6:
        return False

    # Drop obvious short function-word bigrams (e.g., 'of the', 'in the')
    if token_count <= 3 and low in BLACKLIST_PHRASES:
        return False

    # Prefer noun/adjective content — if POS hints heavy function words, drop
    pos = (row.get("pos") or "").upper()
    if any(p in pos for p in ("PRON", "AUX", "ADP")) and token_count <= 2:
        return False

    # drop if any token is a blacklisted proper name
    if any(t in PROPER_NAME_BLACKLIST for t in toks):
        return False

    return True


def main():
    in_csv = "data/openstax_psych_phrases_emotional_compact_reranked.csv"
    out_csv = "data/openstax_psych_phrases_emotional_compact_pruned.csv"

    if not os.path.exists(in_csv):
        print("Input not found:", in_csv)
        return

    rows = []
    with open(in_csv, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)

    kept = [r for r in rows if should_keep(r, score_threshold=1.0)]

    # ensure sorted by score desc
    try:
        kept.sort(key=lambda x: float(x.get("score") or 0.0), reverse=True)
    except Exception:
        pass

    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    out_fields = list(rows[0].keys()) if rows else [
        "phrase", "lemmas", "pos", "example", "source_urls", "score"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for r in kept:
            w.writerow(r)

    print(f"Wrote pruned CSV: {out_csv} (rows: {len(kept)})")


if __name__ == "__main__":
    main()
