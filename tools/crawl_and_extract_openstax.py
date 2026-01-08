#!/usr/bin/env python3
"""Crawl OpenStax Psychology pages, save cleaned texts into per-section
subfolders, and extract candidate lexicon using poetry extractors.

Saves cleaned texts to: data/openstax/<top_slug>/<subslug>_cleaned.txt
Writes combined CSV to: data/openstax_psych_phrases_full.csv (default)

This reuses `PoetryTextCleaner` for cleaning and the same extraction
logic used previously (noun-chunks + 1-3grams), and augments candidates
with terms from `lexicon_enhanced.json` to prefer the expanded lexicon.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from typing import List
from urllib.parse import urljoin

# Lazy-loaded spaCy model cache
_NLP = None


def get_nlp():
    global _NLP
    if _NLP is None:
        import spacy

        _NLP = spacy.load("en_core_web_sm")
    return _NLP


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

DEFAULT_OUT_DIR = os.path.join("data", "openstax")
DEFAULT_OUT_CSV = os.path.join("data", "openstax_psych_phrases_full.csv")
DEFAULT_TMP_DIR = "/tmp/openstax_crawl"


def ensure_packages(allow_install: bool = True):
    try:
        import requests  # noqa: F401
        import spacy  # noqa: F401
        from bs4 import BeautifulSoup  # noqa: F401
    except Exception:
        if not allow_install:
            raise
        print("Installing dependencies: requests, beautifulsoup4, spacy, en_core_web_sm")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "spacy"])
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])


def fetch_url(url: str, tmp_dir: str) -> str:
    import requests

    os.makedirs(tmp_dir, exist_ok=True)
    safe = re.sub(r"[^0-9a-zA-Z]+", "_", url)[:180]
    fname = os.path.join(tmp_dir, safe + ".html")
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


def find_section_links(html_path: str, chapter_prefix: str, base_url: str = "https://openstax.org") -> List[str]:
    """Return absolute URLs for links that match a chapter prefix (e.g., '/pages/11')."""
    from bs4 import BeautifulSoup

    links = []
    if not html_path or not os.path.exists(html_path):
        return links
    with open(html_path, "rb") as f:
        raw = f.read()
    soup = BeautifulSoup(raw, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#"):
            continue
        full = urljoin(base_url, href)
        if chapter_prefix in full and "openstax.org/books/psychology-2e/pages/" in full:
            links.append(full.split("#")[0])
    # unique while preserving order
    seen = set()
    out = []
    for u in links:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def extract_phrases_from_corpus(corpus_text: str, top_k: int = 500) -> List[str]:
    nlp = get_nlp()
    doc = nlp(corpus_text)

    phrases = []
    for chunk in doc.noun_chunks:
        p = re.sub(r"\s+", " ", chunk.text.strip().lower())
        if 2 <= len(p) <= 120:
            phrases.append(p)
    words = [t.text.lower() for t in doc if not t.is_punct and not t.is_space]
    for n in (1, 2, 3):
        for i in range(len(words) - n + 1):
            ng = " ".join(words[i : i + n])
            phrases.append(ng)

    ctr = Counter(phrases)
    common = [p for p, _ in ctr.most_common(top_k)]
    return common


def select_top_with_examples(phrases: List[str], text: str, top_n: int = 400):
    nlp = get_nlp()
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
        out.append({"phrase": p, "lemmas": lemmas, "pos": pos, "example": example})
        seen.add(p)
        if len(out) >= top_n:
            break
    return out


def load_expanded_lexicon(path: str = "lexicon_enhanced.json") -> List[str]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    # support structure where lexicon is nested under 'emotional_territories'
    if isinstance(data, dict) and "emotional_territories" in data:
        data = data["emotional_territories"]
    terms = set()
    for gate, info in (data.items() if isinstance(data, dict) else []):
        if not isinstance(info, dict):
            continue
        for k in ("primary_concepts", "activation_focus"):
            for t in info.get(k, []):
                terms.add(str(t).lower())
        for t in info.get("unique_signals", []):
            terms.add(str(t).lower())
    return sorted(t for t in terms if t)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Crawl OpenStax Psychology and extract lexicon")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--out-csv", default=DEFAULT_OUT_CSV)
    parser.add_argument("--tmp-dir", default=DEFAULT_TMP_DIR)
    parser.add_argument("--no-install", action="store_true")
    parser.add_argument("--top-k", type=int, default=3000)
    parser.add_argument("--top-n", type=int, default=800)
    args = parser.parse_args()

    ensure_packages(allow_install=not args.no_install)

    sys.path.insert(0, os.path.join(os.getcwd(), "scripts", "utilities"))
    try:
        from poetry_text_cleaner import PoetryTextCleaner
    except Exception as e:
        print("Failed to import PoetryTextCleaner:", e)
        return

    cleaner = PoetryTextCleaner()

    OUT_DIR = args.out_dir
    OUT_CSV = args.out_csv
    TMP_DIR = args.tmp_dir

    os.makedirs(OUT_DIR, exist_ok=True)

    cleaned_texts = {}
    combined_corpus_parts = []

    expanded_terms = load_expanded_lexicon()
    print(f"Loaded expanded lexicon terms: {len(expanded_terms)}")

    for top_url in URLS:
        chapter_match = re.search(r"/pages/(\d+)", top_url)
        chapter_prefix = f"/pages/{chapter_match.group(1)}" if chapter_match else "/pages/"
        top_slug = slug_from_url(top_url)
        section_dir = os.path.join(OUT_DIR, top_slug)
        os.makedirs(section_dir, exist_ok=True)

        # Fetch main page
        main_html = fetch_url(top_url, TMP_DIR)
        main_raw = extract_visible_text(main_html)
        main_clean = cleaner.clean_text(main_raw)
        if main_clean:
            out_path = os.path.join(section_dir, top_slug + "_cleaned.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(main_clean)
            cleaned_texts[top_url] = main_clean
            combined_corpus_parts.append(main_clean)
            print(f"Saved: {out_path}")

        # Find sublinks within same chapter prefix
        sublinks = find_section_links(main_html, chapter_prefix)
        # ensure the top_url itself is included as first
        for sub in sublinks:
            if sub == top_url:
                continue
            sub_slug = slug_from_url(sub)
            sub_html = fetch_url(sub, TMP_DIR)
            raw = extract_visible_text(sub_html)
            cleaned = cleaner.clean_text(raw)
            if cleaned:
                out_path = os.path.join(section_dir, sub_slug + "_cleaned.txt")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                cleaned_texts[sub] = cleaned
                combined_corpus_parts.append(cleaned)
                print(f"Saved subpage: {out_path}")

    if not combined_corpus_parts:
        print("No texts fetched/cleaned. Exiting.")
        return

    combined = "\n".join(combined_corpus_parts)

    # Extract candidate phrases
    print("Extracting candidate phrases from combined corpus...")
    candidates = extract_phrases_from_corpus(combined, top_k=args.top_k)

    # Augment candidates with expanded lexicon terms (ensure presence)
    for t in expanded_terms:
        if t not in candidates:
            candidates.insert(0, t)

    # Select top with examples and POS/lemmas
    rows = select_top_with_examples(candidates, combined, top_n=args.top_n)

    # Save CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    import csv

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["phrase", "lemmas", "pos", "example", "source_urls"])
        writer.writeheader()
        for r in rows:
            matches = [
                u for u, t in cleaned_texts.items() if re.search(r"\b" + re.escape(r["phrase"]) + r"\b", t, flags=re.I)
            ]
            r_out = {**r, "source_urls": ",".join(matches)}
            writer.writerow(r_out)

    print(f"Wrote candidate CSV: {OUT_CSV}")


if __name__ == "__main__":
    main()
