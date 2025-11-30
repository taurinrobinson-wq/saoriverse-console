#!/usr/bin/env python3
"""Remove likely fragment seeds from a seed file.

Heuristic: a token is considered a fragment if it is NOT present as a WordNet
lemma but is a strict prefix of one or more WordNet lemmas (e.g. 'collap' -> 'collapse').
This keeps domain-specific tokens that are not in WordNet but removes truncated artifacts.

Usage:
  python3 scripts/remove_fragment_seeds.py --in data/seeds.filtered.txt --out data/seeds.cleaned.txt
"""
import argparse
import json
from pathlib import Path

try:
    import nltk
    from nltk.corpus import wordnet as wn

    nltk.data.find("corpora/wordnet")
except Exception:
    wn = None


def load_wordnet_lemmas():
    if wn is None:
        return set()
    # Build lemma set by iterating synsets (compatible across nltk versions)
    lemmas = set()
    for ss in wn.all_synsets():
        for l in ss.lemmas():
            lemmas.add(l.name().lower())
    return lemmas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", default="data/seeds.filtered.txt")
    p.add_argument("--out", dest="outfile", default="data/seeds.cleaned.txt")
    p.add_argument("--report", dest="report", default="data/seeds.cleaned.report.json")
    args = p.parse_args()

    infile = Path(args.infile)
    outfile = Path(args.outfile)
    reportp = Path(args.report)

    if not infile.exists():
        print("Input file not found:", infile)
        return

    seeds = [l.strip() for l in infile.read_text(encoding="utf-8").splitlines() if l.strip()]

    lemmas = load_wordnet_lemmas()
    removed = []
    kept = []

    for t in seeds:
        t_lower = t.lower()
        # if wordnet not available, keep everything
        if not lemmas:
            kept.append(t)
            continue

        if t_lower in lemmas:
            kept.append(t)
            continue

        # if t is strict prefix of some lemma, consider it a fragment
        is_prefix = any(l.startswith(t_lower) and l != t_lower for l in lemmas)
        if is_prefix:
            removed.append(t)
        else:
            kept.append(t)

    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text("\n".join(kept) + "\n", encoding="utf-8")
    report = {
        "input_count": len(seeds),
        "kept_count": len(kept),
        "removed_count": len(removed),
        "removed": removed[:200],
    }
    reportp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote cleaned seeds to {outfile} ({len(kept)} kept, {len(removed)} removed)")
    print("Report:", reportp)


if __name__ == "__main__":
    main()
