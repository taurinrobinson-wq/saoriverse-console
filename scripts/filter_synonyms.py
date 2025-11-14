#!/usr/bin/env python3
"""Filter merged synonyms to remove multi-word, short, numeric or low-quality items.

Reads a merged synonym map produced by `scripts/merge_synonyms.py` with the
structure:
  { seed: { 'datamuse': [...], 'wordnet': [...], 'merged': [...] } }

Writes a filtered map with the same structure plus a `filtered` list and
produces a small JSON report with counts.

Usage:
  python3 scripts/filter_synonyms.py --in data/synonyms_merged.json --out data/synonyms_filtered.json

This script intentionally avoids any external API calls.
"""
import argparse
import json
import re
from pathlib import Path
from collections import Counter

GENERIC_FILTER = {
    'thing', 'things', 'stuff', 'something', 'anything', 'everything',
    'item', 'items', 'object', 'objects', 'etc', 'etcetera', 'one', 'ones'
}


def is_low_quality(token: str, min_len: int) -> bool:
    if not token:
        return True
    # Remove tokens with digits or weird punctuation
    if re.search(r"\d", token):
        return True
    # token should be alphabetic (allow hyphen and apostrophe)
    if not re.match(r"^[\w\-']+$", token):
        return True
    # too short
    if len(token.replace("-", "").replace("'", "")) < min_len:
        return True
    # generic
    if token in GENERIC_FILTER:
        return True
    return False


def filter_syn_list(syns, remove_multiword: bool, min_len: int):
    kept = []
    removed = []
    for s in syns:
        s_norm = s.strip().lower()
        if not s_norm:
            removed.append((s, 'empty'))
            continue
        if remove_multiword and ' ' in s_norm:
            removed.append((s, 'multiword'))
            continue
        if is_low_quality(s_norm, min_len):
            removed.append((s, 'low_quality'))
            continue
        kept.append(s_norm)
    # dedupe preserving order
    out = []
    seen = set()
    for t in kept:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out, removed


def main():
    p = argparse.ArgumentParser()
    #!/usr/bin/env python3
    """Filter local synonyms produced by `scripts/local_synonyms.py`.

    This script implements the same filtering logic described in
    `data/Local_Only_Interface.md` and writes `data/synonyms_filtered.json`.
    """
    import json
    import re
    import os
    from pathlib import Path

    STOPWORDS = {"thing", "stuff", "item", "something"}
    MIN_LENGTH = 2
    ALLOW_SHORT = {"ai", "os"}

    def normalize_token(t: str) -> str:
        t = t.lower().strip()
        t = re.sub(r"[^\w\s'-]", "", t)
        t = re.sub(r"\s+", " ", t)
        return t

    def is_valid_token(t: str) -> bool:
        if not t:
            return False
        if t in STOPWORDS:
            return False
        if len(t) < MIN_LENGTH and t not in ALLOW_SHORT:
            return False
        if t.isdigit():
            return False
        return True

    def filter_synonyms(input_path="data/synonyms_local.json", output_path="data/synonyms_filtered.json"):
        data_p = Path(input_path)
        if not data_p.exists():
            print('Input file not found:', input_path)
            return {}
        data = json.loads(data_p.read_text(encoding='utf-8'))
        filtered = {}
        for seed, sources in data.items():
            merged = sources.get('merged', [])
            clean = []
            for token in merged:
                token = normalize_token(token)
                if is_valid_token(token):
                    clean.append(token)
            # dedupe preserving order
            clean = list(dict.fromkeys(clean))
            filtered[seed] = {
                'merged_filtered': clean,
                'wordnet': sources.get('wordnet', []),
                'spacy_top': sources.get('spacy_top', [])
            }
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        Path(output_path).write_text(json.dumps(
            filtered, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Filtered synonyms written to {output_path}')
        return filtered

    if __name__ == '__main__':
        filter_synonyms()
