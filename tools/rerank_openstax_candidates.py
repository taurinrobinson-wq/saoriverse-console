#!/usr/bin/env python3
"""Rerank OpenStax phrase candidates to prefer emotionally-relevant items.

Scoring heuristics (simple, transparent):
- seed overlap: matches with terms from `lexicon_enhanced.json` (high weight)
- POS bonus: ADJ+NOUN or ADJ present (moderate weight)
- penalty for boilerplate tokens (openstax, authors, http, copyright)

Writes a ranked CSV (`data/openstax_psych_phrases_emotional.csv`) with score.
"""
from __future__ import annotations

import os
import re
import csv
import json
import argparse
from typing import List


def load_expanded_lexicon(path: str = "lexicon_enhanced.json") -> List[str]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    if isinstance(data, dict) and "emotional_territories" in data:
        data = data["emotional_territories"]
    terms = set()
    for gate, info in (data.items() if isinstance(data, dict) else []):
        if not isinstance(info, dict):
            continue
        for k in ("primary_concepts", "activation_focus"):
            for t in info.get(k, []):
                terms.add(str(t).lower())
        for t in info.get("unique_signals", []):
            terms.add(str(t).lower())
    return sorted(t for t in terms if t)


def tokenize_text(s: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", (s or "").lower())


def is_boilerplate(p: str) -> bool:
    low = (p or "").lower()
    if "openstax" in low or "http" in low or "copyright" in low or "©" in low:
        return True
    if re.search(r"authors?:", low):
        return True
    if len(tokenize_text(low)) <= 1 and len(low) < 6:
        return True
    return False


def score_row(row: dict, seeds: List[str]) -> float:
    phrase = (row.get("phrase") or "").lower()
    lemmas = (row.get("lemmas") or "").lower()
    pos = (row.get("pos") or "").upper()
    example = (row.get("example") or "").lower()

    tokens = set(tokenize_text(phrase) +
                 tokenize_text(lemmas) + tokenize_text(example))

    # seed overlap (heavy)
    seed_hits = sum(1 for s in seeds if any(tok in s.split()
                    for tok in tokens) or s in phrase)
    seed_score = seed_hits * 3.0

    # POS bonus
    pos_score = 0.0
    if "ADJ" in pos:
        pos_score += 1.0
    # prefer adjective+noun or noun+noun
    if re.search(r"ADJ,?NOUN|NOUN,?NOUN", pos):
        pos_score += 0.8

    # length heuristics
    token_count = len(tokenize_text(phrase))
    len_score = 0.0
    if 1 < token_count <= 4:
        len_score += 0.5
    elif token_count > 4:
        len_score -= 0.3

    # penalty for boilerplate / metadata
    penalty = 0.0
    if is_boilerplate(phrase) or is_boilerplate(example) or re.search(r"\b(author|publisher|openstax|access for free|license|creative commons)\b", example):
        penalty -= 5.0

    # boost if phrase contains clear emotional terms (simple list)
    emotional_terms = {"emotion", "feel", "fear", "anger", "sad", "happy", "anxiety", "stress", "love", "attachment",
                       "intimacy", "aggression", "empathy", "personality", "trait", "attitude", "prejudice", "conformity", "altruism"}
    emo_hits = sum(1 for t in tokens if t in emotional_terms)
    emo_score = emo_hits * 2.0

    total = seed_score + pos_score + len_score + emo_score + penalty
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_csv",
                        default="data/openstax_psych_phrases_full.csv")
    parser.add_argument("--out", dest="out_csv",
                        default="data/openstax_psych_phrases_emotional.csv")
    parser.add_argument("--top", type=int, default=800)
    parser.add_argument("--lex", default="lexicon_enhanced.json")
    args = parser.parse_args()

    seeds = load_expanded_lexicon(args.lex)
    print(f"Loaded {len(seeds)} seed terms from {args.lex}")

    if not os.path.exists(args.in_csv):
        print("Input CSV not found:", args.in_csv)
        return

    rows = []
    with open(args.in_csv, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)

    scored = []
    for r in rows:
        s = score_row(r, seeds)
        r2 = dict(r)
        r2["score"] = s
        scored.append(r2)

    scored.sort(key=lambda x: x["score"], reverse=True)

    out_fields = list(rows[0].keys()) + ["score"] if rows else ["phrase",
                                                                "lemmas", "pos", "example", "source_urls", "score"]
    os.makedirs(os.path.dirname(args.out_csv) or ".", exist_ok=True)
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for r in scored[: args.top]:
            w.writerow(r)

    print(
        f"Wrote reranked CSV: {args.out_csv} (top {min(args.top, len(scored))})")


if __name__ == "__main__":
    main()
