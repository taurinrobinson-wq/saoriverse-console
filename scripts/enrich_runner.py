#!/usr/bin/env python3
"""Run the full local enrichment pipeline: build -> filter -> score -> DB

This script orchestrates the local-only pipeline and is safe to run in CI
or locally. It expects the spaCy model and NLTK WordNet data to be installed.
"""
from pathlib import Path
import os

from scripts.local_synonyms import build_synonyms, load_seeds
from scripts.filter_synonyms import filter_synonyms
from scripts.score_synonyms import score_synonyms
from scripts.synonym_db import init_db, load_from_json


def run_enrichment():
    print('Building local synonyms...')
    seeds = load_seeds()
    merged = build_synonyms(seeds)
    Path('data').mkdir(parents=True, exist_ok=True)
    Path('data/synonyms_local.json').write_text(__import__('json').dumps(merged,
                                                                         ensure_ascii=False, indent=2), encoding='utf-8')

    print('Filtering synonyms...')
    filter_synonyms(input_path='data/synonyms_local.json',
                    output_path='data/synonyms_filtered.json')

    print('Scoring synonyms...')
    score_synonyms(input_path='data/synonyms_filtered.json',
                   output_path='data/synonyms_scored.json')

    print('Updating SQLite database...')
    init_db()
    load_from_json('data/synonyms_scored.json')

    print('Enrichment complete. Synonyms are refreshed in data/synonyms.db.')


if __name__ == '__main__':
    run_enrichment()
