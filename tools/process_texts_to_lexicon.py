#!/usr/bin/env python3
"""
Process local plain-text books into an affective lexicon JSON.

Reads files from `data/poetry/texts/*.txt`, splits into overlapping line chunks,
extracts affective phrases using `parser.poetry_extractor.PoetryExtractor`,
aggregates phrase scores and writes `learning/user_overrides/gutenberg_texts_lexicon.json`.

This output is compatible with `scripts/utilities/poetry_glyph_generator.py`.
"""
from __future__ import annotations
from parser.poetry_extractor import PoetryExtractor

import json
from collections import defaultdict, Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    input_dir = Path("data/poetry/texts")
    out_path = Path("learning/user_overrides/gutenberg_texts_lexicon.json")

    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        return 1

    extractor = PoetryExtractor()

    phrase_stats: dict = {}

    files = sorted(input_dir.glob("*.txt"))
    if not files:
        print(f"No .txt files found in {input_dir}")
        return 1

    print(f"Processing {len(files)} files from {input_dir}")

    for idx, path in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] {path.name}")
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  ✗ Failed to read {path}: {e}")
            continue

        # chunk the text into overlapping pieces
        chunks = extractor.extract_text_chunks(
            text, book_id=idx, chunk_lines=200, overlap_lines=20)
        print(f"  → Created {len(chunks)} chunks")

        for c in chunks:
            try:
                phrases = extractor.extract_affective_phrases(
                    c['text'], top_n=30)
            except Exception as e:
                print(
                    f"    ✗ extract_affective_phrases failed for a chunk: {e}")
                continue

            for phrase_text, score, phrase_emotions in phrases:
                key = phrase_text.strip()
                if not key:
                    continue
                k = key.lower()
                if k not in phrase_stats:
                    phrase_stats[k] = {
                        'phrase': key,
                        'score_sum': float(score),
                        'count': 1,
                        'emotions': Counter(phrase_emotions or {})
                    }
                else:
                    phrase_stats[k]['score_sum'] += float(score)
                    phrase_stats[k]['count'] += 1
                    phrase_stats[k]['emotions'].update(phrase_emotions or {})

    if not phrase_stats:
        print("No affective phrases extracted from texts.")
        return 1

    # Build signals mapping: scale scores to integer frequencies
    # We'll multiply aggregate score by 10 to produce frequencies in the same rough scale
    signals = {}
    for k, v in phrase_stats.items():
        freq = int(round(v['score_sum'] * 10))
        if freq <= 0:
            continue
        signals[v['phrase']] = {"frequency": freq, "keywords": []}

    # Sort and keep top 1000 phrases to avoid huge lexicons
    sorted_items = sorted(
        signals.items(), key=lambda x: x[1]['frequency'], reverse=True)
    top_n = 1000
    top_signals = dict(sorted_items[:top_n])

    out = {"signals": top_signals}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote lexicon: {out_path} (signals: {len(top_signals)})")

    # Print top 25 phrases
    print("Top 25 phrases:")
    for i, (p, info) in enumerate(list(top_signals.items())[:25], 1):
        print(f"  {i:2d}. {p} — freq={info['frequency']}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
