#!/usr/bin/env python3
"""
Expand lexicon keywords using spaCy lemmatization and Datamuse (synonyms/similar words).

Creates `learning/user_overrides/openstax_bulk_lexicon_expanded.json` with broader keyword lists.
"""

import json
import logging
import time
from pathlib import Path
from typing import List

import requests
import spacy

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def datamuse_synonyms(term: str, max_results: int = 10) -> List[str]:
    url = "https://api.datamuse.com/words"
    params = {"rel_syn": term, "max": max_results}
    try:
        resp = requests.get(url, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        return [d['word'] for d in data if 'word' in d]
    except Exception as e:
        logger.debug(f"Datamuse lookup failed for {term}: {e}")
        return []


def broaden_keywords(keywords: List[str], nlp, synonyms_per_kw: int = 8) -> List[str]:
    out = []
    seen = set()

    for kw in keywords:
        kw = kw.strip().lower()
        if not kw:
            continue
        if kw in seen:
            continue
        seen.add(kw)
        out.append(kw)

        # Lemma
        doc = nlp(kw)
        for tok in doc:
            lemma = tok.lemma_.lower()
            if lemma and lemma not in seen:
                seen.add(lemma)
                out.append(lemma)

        # Datamuse synonyms
        syns = datamuse_synonyms(kw, max_results=synonyms_per_kw)
        for s in syns:
            s = s.lower()
            if s not in seen:
                seen.add(s)
                out.append(s)

        # polite rate-limit
        time.sleep(0.08)

    # Limit to reasonable size
    return out[:40]


def main():
    src = Path('learning/user_overrides/openstax_bulk_lexicon.json')
    dst = Path('learning/user_overrides/openstax_bulk_lexicon_expanded.json')

    if not src.exists():
        logger.error(f"Source lexicon not found: {src}")
        return 2

    logger.info(f"Loading lexicon: {src}")
    lex = json.loads(src.read_text(encoding='utf-8'))
    signals = lex.get('signals', {})

    # Load spaCy model
    try:
        nlp = spacy.load('en_core_web_sm')
    except Exception:
        logger.info('spaCy model not found, attempting to download...')
        import subprocess
        subprocess.check_call(
            ['python3', '-m', 'spacy', 'download', 'en_core_web_sm'])
        nlp = spacy.load('en_core_web_sm')

    expanded = {'signals': {}}

    for sig, data in signals.items():
        kws = data.get('keywords', [])
        logger.info(f"Expanding signal '{sig}' ({len(kws)} keywords)")
        new_kws = broaden_keywords(kws, nlp)
        # keep original frequency
        expanded['signals'][sig] = {
            'frequency': data.get('frequency', 0),
            'keywords': new_kws,
        }

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(expanded, indent=2), encoding='utf-8')
    logger.info(f"Wrote expanded lexicon: {dst}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
