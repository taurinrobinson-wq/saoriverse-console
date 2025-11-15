#!/usr/bin/env python3
"""
Fetch NHS bereavement guidance page, extract visible text, pull candidate phrases,
POS-tag them and write top-50 CSV to data/nhs_bereavement_phrases.csv.

This script uses requests + beautifulsoup4 + spacy (small English model).
If not installed, it will try to pip-install them locally.
"""
import csv
import os
import re
import sys
from collections import Counter

URL = "https://www.nhs.uk/conditions/stress-anxiety-depression/bereavement/"
HTML_PATH = "/tmp/nhs_bereavement.html"
OUT_CSV = os.path.join("data", "nhs_bereavement_phrases.csv")


def ensure_packages():
    try:
        import requests  # noqa: F401
        from bs4 import BeautifulSoup  # noqa: F401
        import spacy  # noqa: F401
    except Exception:
        print("Missing packages; installing requests, beautifulsoup4, spacy, and en_core_web_sm")
        import subprocess

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "spacy"])
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"])


def fetch_html():
    import requests

    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    with open(HTML_PATH, "wb") as f:
        f.write(r.content)
    print(f"Saved HTML to {HTML_PATH}")


def extract_text():
    from bs4 import BeautifulSoup

    with open(HTML_PATH, "rb") as f:
        doc = f.read()
    soup = BeautifulSoup(doc, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    # Extract headings and paragraphs and list items
    pieces = []
    for tagname in ["h1", "h2", "h3", "h4", "p", "li"]:
        for tag in soup.find_all(tagname):
            text = tag.get_text(separator=" ", strip=True)
            if text:
                pieces.append(text)

    text = "\n".join(pieces)
    return text


def candidate_phrases(text, top_k=200):
    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Collect noun chunks and 1-3 grams
    phrases = []
    for chunk in doc.noun_chunks:
        p = chunk.text.strip().lower()
        p = re.sub(r"\s+", " ", p)
        if 2 <= len(p) <= 80:
            phrases.append(p)

    # Also n-grams from sentences
    from itertools import islice

    words = [t.text.lower() for t in doc if not t.is_punct and not t.is_space]
    for n in (1, 2, 3):
        for i in range(len(words) - n + 1):
            ng = " ".join(words[i: i + n])
            phrases.append(ng)

    # Rank by frequency
    ctr = Counter(phrases)
    common = [p for p, _ in ctr.most_common(top_k)]
    return common


def select_top(phrases, text, top_n=50):
    # For each phrase, find an example sentence
    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sents = list(doc.sents)

    results = []
    for p in phrases:
        pat = re.compile(r"\b" + re.escape(p) + r"\b", flags=re.I)
        example = None
        for s in sents:
            if pat.search(s.text):
                example = s.text.strip()
                break
        results.append((p, example or "",))

    # Deduplicate and take top_n
    seen = set()
    out = []
    for p, example in results:
        if p in seen:
            continue
        seen.add(p)
        out.append((p, example))
        if len(out) >= top_n:
            break
    return out


def pos_and_lemma(rows):
    import spacy

    nlp = spacy.load("en_core_web_sm")
    out_rows = []
    for phrase, example in rows:
        doc = nlp(phrase)
        lemmas = " ".join(tok.lemma_ for tok in doc)
        pos = ",".join(tok.pos_ for tok in doc)
        out_rows.append({"phrase": phrase, "lemmas": lemmas,
                        "pos": pos, "example": example, "source": URL})
    return out_rows


def write_csv(rows):
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["phrase", "lemmas", "pos", "example", "source"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote CSV to {OUT_CSV}")


def main():
    ensure_packages()
    fetch_html()
    text = extract_text()
    phrases = candidate_phrases(text, top_k=1000)
    selected = select_top(phrases, text, top_n=50)
    pos_rows = pos_and_lemma(selected)
    write_csv(pos_rows)


if __name__ == "__main__":
    main()
