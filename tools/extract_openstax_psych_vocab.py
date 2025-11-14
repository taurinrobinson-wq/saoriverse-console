#!/usr/bin/env python3
"""
Fetch the provided OpenStax Psychology pages (personality & social sections),
clean using `PoetryTextCleaner`, perform a poetry-style extraction (noun-chunks
+ 1-3grams), POS-tag and lemmatize, and write outputs:

- `data/openstax/<slug>_cleaned.txt` (cleaned page text)
- `data/openstax_psych_phrases.csv` (combined CSV of top candidate phrases)

This script reuses `scripts.utilities.poetry_text_cleaner.PoetryTextCleaner` for
consistent cleaning.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter, defaultdict
from typing import List

URLS = [
    "https://openstax.org/books/psychology-2e/pages/11-introduction",
    "https://openstax.org/books/psychology-2e/pages/11-1-what-is-personality",
    "https://openstax.org/books/psychology-2e/pages/11-2-freud-and-the-psychodynamic-perspective",
    "https://openstax.org/books/psychology-2e/pages/11-3-neo-freudians-adler-erikson-jung-and-horney",
    "https://openstax.org/books/psychology-2e/pages/11-4-learning-approaches",
    "https://openstax.org/books/psychology-2e/pages/11-5-humanistic-approaches",
    "https://openstax.org/books/psychology-2e/pages/11-6-biological-approaches",
    "https://openstax.org/books/psychology-2e/pages/11-7-trait-theorists",
    "https://openstax.org/books/psychology-2e/pages/11-8-cultural-understandings-of-personality",
    "https://openstax.org/books/psychology-2e/pages/11-9-personality-assessment",
    "https://openstax.org/books/psychology-2e/pages/11-key-terms",
    "https://openstax.org/books/psychology-2e/pages/11-summary",
    "https://openstax.org/books/psychology-2e/pages/12-introduction",
    "https://openstax.org/books/psychology-2e/pages/12-1-what-is-social-psychology",
    "https://openstax.org/books/psychology-2e/pages/12-2-self-presentation",
    "https://openstax.org/books/psychology-2e/pages/12-3-attitudes-and-persuasion",
    "https://openstax.org/books/psychology-2e/pages/12-4-conformity-compliance-and-obedience",
    "https://openstax.org/books/psychology-2e/pages/12-5-prejudice-and-discrimination",
    "https://openstax.org/books/psychology-2e/pages/12-6-aggression",
    "https://openstax.org/books/psychology-2e/pages/12-7-prosocial-behavior",
    "https://openstax.org/books/psychology-2e/pages/12-key-terms",
    "https://openstax.org/books/psychology-2e/pages/12-summary",
]

OUT_DIR = os.path.join("data", "openstax")
OUT_CSV = os.path.join("data", "openstax_psych_phrases.csv")
TMP_DIR = "/tmp/openstax_html"


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
    safe = re.sub(r"[^0-9a-zA-Z]+", "_", url)[:180]
    fname = os.path.join(TMP_DIR, safe + ".html")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        with open(fname, "wb") as f:
            f.write(r.content)
        print(f"Fetched {url}")
        return fname
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""


def extract_visible_text(path: str) -> str:
    from bs4 import BeautifulSoup

    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        raw = f.read()
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()
    pieces: List[str] = []
    # capture headings, paragraphs, list items, captions
    for tagname in ["h1", "h2", "h3", "h4", "p", "li", "dd", "figcaption"]:
        for tag in soup.find_all(tagname):
            text = tag.get_text(separator=" ", strip=True)
            if text:
                pieces.append(text)
    return "\n".join(pieces)


def slug_from_url(url: str) -> str:
    return re.sub(r"^https?://", "", url).replace("/", "_")


def extract_phrases_from_corpus(corpus_text: str, top_k: int = 500) -> List[str]:
    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(corpus_text)

    phrases = []
    for chunk in doc.noun_chunks:
        p = re.sub(r"\s+", " ", chunk.text.strip().lower())
        if 2 <= len(p) <= 120:
            phrases.append(p)
    words = [t.text.lower() for t in doc if not t.is_punct and not t.is_space]
    for n in (1, 2, 3):
        for i in range(len(words) - n + 1):
            ng = " ".join(words[i: i + n])
            phrases.append(ng)

    ctr = Counter(phrases)
    common = [p for p, _ in ctr.most_common(top_k)]
    return common


def select_top_with_examples(phrases: List[str], text: str, top_n: int = 300):
    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sents = list(doc.sents)

    out = []
    seen = set()
    for p in phrases:
        if p in seen:
            continue
        pat = re.compile(r"\b" + re.escape(p) + r"\b", flags=re.I)
        example = ""
        for s in sents:
            if pat.search(s.text):
                example = s.text.strip()
                break
        docp = nlp(p)
        lemmas = " ".join(tok.lemma_ for tok in docp)
        pos = ",".join(tok.pos_ for tok in docp)
        out.append({"phrase": p, "lemmas": lemmas,
                   "pos": pos, "example": example})
        seen.add(p)
        if len(out) >= top_n:
            break
    return out


def main():
    ensure_packages()

    # Reuse the poetry cleaner
    sys.path.insert(0, os.path.join(os.getcwd(), "scripts", "utilities"))
    try:
        from poetry_text_cleaner import PoetryTextCleaner
    except Exception as e:
        print("Failed to import PoetryTextCleaner:", e)
        return

    cleaner = PoetryTextCleaner()

    os.makedirs(OUT_DIR, exist_ok=True)

    cleaned_texts = {}
    combined_corpus_parts = []
    sources_map = defaultdict(list)

    for url in URLS:
        fname = fetch_url(url)
        if not fname:
            continue
        raw = extract_visible_text(fname)
        cleaned = cleaner.clean_text(raw)
        slug = slug_from_url(url)
        out_path = os.path.join(OUT_DIR, slug + "_cleaned.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"Saved cleaned text: {out_path}")
        cleaned_texts[url] = cleaned
        combined_corpus_parts.append(cleaned)
        sources_map[url].append(out_path)

    if not combined_corpus_parts:
        print("No texts fetched/cleaned. Exiting.")
        return

    combined = "\n".join(combined_corpus_parts)

    # Extract candidate phrases
    print("Extracting candidate phrases from combined corpus...")
    candidates = extract_phrases_from_corpus(combined, top_k=2000)

    # Select top with examples and POS/lemmas
    rows = select_top_with_examples(candidates, combined, top_n=400)

    # Save CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["phrase", "lemmas", "pos", "example", "source_urls"])
        writer.writeheader()
        for r in rows:
            # heuristically find sources that contain the phrase
            matches = [u for u, t in cleaned_texts.items() if re.search(
                r"\b" + re.escape(r['phrase']) + r"\b", t, flags=re.I)]
            r_out = {**r, "source_urls": ",".join(matches)}
            writer.writerow(r_out)

    print(f"Wrote candidate CSV: {OUT_CSV}")


if __name__ == "__main__":
    main()
