from typing import List, Dict
import re


def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


def simple_lemmatize(token: str) -> str:
    if token.endswith("ing"):
        return token[:-3]
    if token.endswith("ed"):
        return token[:-2]
    if token.endswith("ly"):
        return token[:-2]
    if token.endswith("s") and len(token) > 3:
        return token[:-1]
    return token


# Minimal lexicon for tests: lemma -> {tag, conf}
LEXICON: Dict[str, Dict] = {
    "invisibl": {"tag": "feeling_unseen", "conf": 0.95},
    "invisible": {"tag": "feeling_unseen", "conf": 0.95},
    "ignore": {"tag": "feeling_unseen", "conf": 0.9},
    "anger": {"tag": "anger", "conf": 0.95},
    "angry": {"tag": "anger", "conf": 0.95},
    "sad": {"tag": "sadness", "conf": 0.9},
    "stung": {"tag": "sadness", "conf": 0.75},
    "frustrat": {"tag": "sadness", "conf": 0.6},
}


def detect_overlays(tokens: List[str], lexicon: Dict[str, Dict] = None) -> Dict[str, float]:
    if lexicon is None:
        lexicon = LEXICON

    negation_words = {"not", "no", "never", "n't"}
    tag_confidence: Dict[str, List[float]] = {}

    for idx, tok in enumerate(tokens):
        lemma = simple_lemmatize(tok)
        matched = None
        if lemma in lexicon:
            matched = lexicon[lemma]
        else:
            for key in lexicon:
                if lemma.startswith(key) or tok.startswith(key) or key.startswith(lemma):
                    matched = lexicon[key]
                    break

        if not matched:
            continue

        base_conf = float(matched["conf"])
        window_start = max(0, idx - 3)
        window = tokens[window_start:idx]
        if any(w in negation_words for w in window):
            base_conf *= 0.1

        tag = matched["tag"]
        tag_confidence.setdefault(tag, []).append(base_conf)

    combined: Dict[str, float] = {}
    for tag, confs in tag_confidence.items():
        prod = 1.0
        for p in confs:
            prod *= (1.0 - p)
        combined[tag] = round(1.0 - prod, 4)

    return combined


def analyze_text(text: str, lexicon: Dict[str, Dict] = None) -> Dict:
    tokens = tokenize(text)
    combined = detect_overlays(tokens, lexicon=lexicon)
    infos = [{"tag": t, "confidence": combined[t]}
             for t in sorted(combined, key=lambda k: -combined[k])]
    tags = [i["tag"] for i in infos if i["confidence"] > 0.0]
    return {"tokens": tokens, "glyph_overlays_info": infos, "glyph_overlays": tags}
