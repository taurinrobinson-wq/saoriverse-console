#!/usr/bin/env python3
"""Score filtered synonyms using SpaCy embeddings.

Reads `data/synonyms_filtered.json` and writes `data/synonyms_scored.json`.
If SpaCy model isn't available, scores will be 0.
"""
import json
from pathlib import Path

try:
    import spacy
    _HAS_SPACY = True
except Exception:
    _HAS_SPACY = False


def score_synonyms(input_path="data/synonyms_filtered.json", output_path="data/synonyms_scored.json"):
    p = Path(input_path)
    if not p.exists():
        print('Input not found:', input_path)
        return
    data = json.loads(p.read_text(encoding='utf-8'))
    nlp = None
    if _HAS_SPACY:
        try:
            nlp = spacy.load('en_core_web_md')
        except Exception:
            nlp = None

    scored = {}
    for seed, sources in data.items():
        merged = sources.get('merged_filtered', [])
        seed_doc = nlp(seed) if nlp else None
        results = []
        for token in merged:
            try:
                score = seed_doc.similarity(
                    nlp(token)) if nlp and seed_doc is not None else 0.0
            except Exception:
                score = 0.0
            results.append({'word': token, 'score': round(score, 3)})

        results = sorted(results, key=lambda x: -x['score'])
        scored[seed] = {
            'seed': seed,
            'synonyms_scored': results,
            'top_synonyms': [r['word'] for r in results[:5]],
            'provenance': {
                'wordnet': sources.get('wordnet', []),
                'spacy_top': sources.get('spacy_top', [])
            }
        }

    Path(output_path).write_text(json.dumps(
        scored, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Scored synonyms written to {output_path}')


if __name__ == '__main__':
    score_synonyms()
