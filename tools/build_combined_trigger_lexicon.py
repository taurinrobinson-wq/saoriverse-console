#!/usr/bin/env python3
"""
Build a combined trigger lexicon by merging the expanded lexicon and glyph-associated keywords.

Output: learning/user_overrides/openstax_bulk_lexicon_expanded_triggers.json
"""
import json
import logging
from pathlib import Path

import spacy

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def lemmatize_terms(terms, nlp):
    out = []
    seen = set()
    for t in terms:
        t = t.strip().lower()
        if not t or t in seen:
            continue
        doc = nlp(t)
        lemmas = " ".join(tok.lemma_ for tok in doc).strip()
        if lemmas and lemmas not in seen:
            seen.add(lemmas)
            out.append(lemmas)
    return out


def main():
    expanded_path = Path("learning/user_overrides/openstax_bulk_lexicon_expanded.json")
    glyphs_path = Path("data/generated_glyphs_from_openstax.json")
    out_path = Path("learning/user_overrides/openstax_bulk_lexicon_expanded_triggers.json")

    if not expanded_path.exists():
        logger.error(f"Expanded lexicon missing: {expanded_path}")
        return 2
    if not glyphs_path.exists():
        logger.error(f"Glyphs file missing: {glyphs_path}")
        return 2

    expanded = json.loads(expanded_path.read_text(encoding="utf-8"))
    glyphs = json.loads(glyphs_path.read_text(encoding="utf-8"))

    # Load spaCy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        import subprocess

        subprocess.check_call(["python3", "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")

    signals = {}
    # Start from expanded lexicon
    for sig, data in expanded.get("signals", {}).items():
        keywords = list(dict.fromkeys([k.strip().lower() for k in data.get("keywords", []) if k]))
        signals[sig] = {"frequency": data.get("frequency", 0), "keywords": keywords}

    # Merge glyph-associated keywords
    for g in glyphs:
        core = g.get("core_emotions", [])
        assoc = g.get("associated_keywords", [])
        for sig in core:
            if sig not in signals:
                signals[sig] = {"frequency": 0, "keywords": []}
            for a in assoc:
                a = a.strip().lower()
                if a and a not in signals[sig]["keywords"]:
                    signals[sig]["keywords"].append(a)

    # Lemmatize and dedupe keywords per signal
    combined = {"signals": {}}
    for sig, data in signals.items():
        kws = data.get("keywords", [])
        lemmas = lemmatize_terms(kws, nlp)
        # Ensure original keywords are also included (lemmatization may change form)
        merged = list(dict.fromkeys([k for k in kws] + lemmas))
        combined["signals"][sig] = {"frequency": data.get("frequency", 0), "keywords": merged}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    logger.info(f"Wrote combined trigger lexicon: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
