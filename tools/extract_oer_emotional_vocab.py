#!/usr/bin/env python3
"""
Fetch a small set of OER pages and extract emotionally-relevant phrases.

Targets (by default):
- Language Textbooks Collection (OER Commons)
- Psychology 2e (OpenStax) / treatment modalities page
- Positive Psychology collection (OER Commons)

This script extracts visible text, finds sentences containing emotion keywords,
collects noun-chunk and 1-3gram phrases from those sentences, ranks them by
frequency and returns a CSV at `data/oer_emotional_phrases.csv` with columns:
phrase, lemmas, pos, example, source

Note: This is heuristic and intended to produce candidate phrases for manual review.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter
from typing import List

DEFAULT_URLS = [
    "https://oercommons.org/curated-collections/458",  # Language Textbooks Collection
    # OpenStax Psychology 2e
    "https://openstax.org/books/psychology-2e/pages/16-3-treatment-modalities",
    # Tao / Positive Psychology collection
    "https://oercommons.org/curated-collections/479",
]

OUT_CSV = os.path.join("data", "oer_emotional_phrases.csv")
TMP_DIR = "/tmp/oer_extraction"

EMOTION_KEYWORDS = [
    "grief",
    "bereavement",
    "sadness",
    "loss",
    "mourning",
    "cope",
    "coping",
    "support",
    "therapy",
    "counsel",
    "counselling",
    "resilience",
    "hope",
    "comfort",
    "stress",
    "depression",
    "well-being",
    "wellbeing",
    "empathy",
    "compassion",
    "healing",
    "trauma",
    "bereaved",
]


def ensure_packages():
    try:
        import requests  # noqa: F401
        from bs4 import BeautifulSoup  # noqa: F401
        import spacy  # noqa: F401
    except Exception:
        print("Installing dependencies: requests, beautifulsoup4, spacy, en_core_web_sm")
        import subprocess

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "spacy"])
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"])


def fetch_url(url: str) -> str:
    import requests

    os.makedirs(TMP_DIR, exist_ok=True)
    fname = os.path.join(TMP_DIR, re.sub(
        r"[^0-9a-zA-Z]+", "_", url)[:200] + ".html")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(fname, "wb") as f:
            f.write(r.content)
        print(f"Fetched {url} -> {fname}")
        return fname
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""


def extract_visible_text_from_file(path: str) -> str:
    from bs4 import BeautifulSoup

    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        raw = f.read()
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()
    pieces: List[str] = []
    for tagname in ["h1", "h2", "h3", "h4", "p", "li", "dd"]:
        for tag in soup.find_all(tagname):
            text = tag.get_text(separator=" ", strip=True)
            if text:
                pieces.append(text)
    text = "\n".join(pieces)
    return text


def sentences_with_emotion(text: str) -> List[str]:
    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    kw_pat = re.compile(r"\b(?:" + "|".join(re.escape(k)
                        for k in EMOTION_KEYWORDS) + r")\b", flags=re.I)
    sents = [s.text.strip() for s in doc.sents if kw_pat.search(s.text)]
    return sents


def phrases_from_sentences(sents: List[str], top_k=500) -> List[str]:
    import spacy

    nlp = spacy.load("en_core_web_sm")
    phrases = []
    for sent in sents:
        doc = nlp(sent)
        for chunk in doc.noun_chunks:
            p = re.sub(r"\s+", " ", chunk.text.strip().lower())
            if 2 <= len(p) <= 100:
                phrases.append(p)
        words = [t.text.lower()
                 for t in doc if not t.is_punct and not t.is_space]
        for n in (1, 2, 3):
            for i in range(max(0, len(words) - n + 1)):
                ng = " ".join(words[i: i + n])
                phrases.append(ng)
    ctr = Counter(phrases)
    common = [p for p, _ in ctr.most_common(top_k)]
    return common


def select_top_and_tag(phrases: List[str], sentences_text: str, top_n=200):
    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sentences_text)
    sents = list(doc.sents)
    rows = []
    seen = set()
    for p in phrases:
        if p in seen:
            continue
        # find example
        pat = re.compile(r"\b" + re.escape(p) + r"\b", flags=re.I)
        example = ""
        for s in sents:
            if pat.search(s.text):
                example = s.text.strip()
                break
        docp = nlp(p)
        lemmas = " ".join(tok.lemma_ for tok in docp)
        pos = ",".join(tok.pos_ for tok in docp)
        rows.append({"phrase": p, "lemmas": lemmas,
                    "pos": pos, "example": example})
        seen.add(p)
        if len(rows) >= top_n:
            break
    return rows


def run(urls=DEFAULT_URLS):
    ensure_packages()
    all_sentences = []
    sources = []
    for u in urls:
        f = fetch_url(u)
        if not f:
            continue
        text = extract_visible_text_from_file(f)
        sents = sentences_with_emotion(text)
        if not sents:
            # fallback: take the whole text's sentences (limited)
            import spacy

            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            sents = [s.text.strip() for s in doc.sents][:300]
        all_sentences.extend(sents)
        sources.append(u)

    big_text = "\n".join(all_sentences)
    phrases = phrases_from_sentences(all_sentences, top_k=2000)
    tagged = select_top_and_tag(phrases, big_text, top_n=300)
    # add source field heuristically (first source)
    for r in tagged:
        r["source"] = ",".join(sources)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["phrase", "lemmas", "pos", "example", "source"])
        writer.writeheader()
        for r in tagged:
            writer.writerow(r)
    print("Wrote", OUT_CSV)


if __name__ == "__main__":
    run()
