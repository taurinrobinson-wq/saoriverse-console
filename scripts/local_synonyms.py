#!/usr/bin/env python3
"""Build local synonyms from WordNet and (optionally) SpaCy similarity.

Reads seeds from `data/seeds.cleaned.txt` (one per line) if present, otherwise
falls back to a small builtin list. Produces `data/synonyms_local.json`.
"""
import json
import os
import re
from pathlib import Path
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

try:
    import spacy
    _HAS_SPACY = True
except Exception:
    _HAS_SPACY = False

lemmatizer = WordNetLemmatizer()


def normalize_token(t):
    t = t.lower().strip()
    t = re.sub(r"[^\w\s'-]", "", t)
    t = re.sub(r"\s+", " ", t)
    return lemmatizer.lemmatize(t)


def get_wordnet_synonyms(word):
    norm = normalize_token(word)
    syns = set()
    for ss in wn.synsets(norm):
        for lemma in ss.lemmas():
            val = normalize_token(lemma.name().replace("_", " "))
            if val:
                syns.add(val)
    return sorted(syns)


def get_spacy_top(word, candidates, n=5, nlp=None):
    if not _HAS_SPACY or nlp is None or not candidates:
        return []
    doc = nlp(word)
    scored = []
    for cand in candidates:
        try:
            score = doc.similarity(nlp(cand))
        except Exception:
            score = 0.0
        scored.append((cand, score))
    scored.sort(key=lambda x: -x[1])
    return [w for w, s in scored[:n]]


def load_seeds():
    p = Path('data/seeds.cleaned.txt')
    if p.exists():
        with p.open('r', encoding='utf-8') as fh:
            return [l.strip() for l in fh if l.strip()]
    # fallback
    return ['joy', 'anger', 'trust']


def build_synonyms(seed_words):
    merged = {}
    nlp = None
    if _HAS_SPACY:
        try:
            nlp = spacy.load('en_core_web_md')
        except Exception:
            nlp = None

    for w in seed_words:
        try:
            wn_syns = get_wordnet_synonyms(w)
            spacy_top = get_spacy_top(
                w, wn_syns, n=5, nlp=nlp) if wn_syns else []
            merged[w] = {
                'wordnet': wn_syns,
                'spacy_top': spacy_top,
                'merged': sorted(set(wn_syns + spacy_top))
            }
        except Exception as e:
            merged[w] = {'wordnet': [], 'spacy_top': [], 'merged': []}
    return merged


def main():
    os.makedirs('data', exist_ok=True)
    seeds = load_seeds()
    print(f'Building synonyms for {len(seeds)} seeds')
    out = build_synonyms(seeds)
    Path('data/synonyms_local.json').write_text(json.dumps(out,
                                                           ensure_ascii=False, indent=2), encoding='utf-8')
    print('Wrote data/synonyms_local.json')


if __name__ == '__main__':
    main()
