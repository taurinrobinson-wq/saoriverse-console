Here’s a fully formatted **Markdown implementation guide** you can copy directly into a `.md` file. It includes all the code scaffolding you need for the local‑only synonym pipeline, filtering, scoring, SQLite storage, and background enrichment runner. Since you already have `spacy`, `nltk`, and `textblob` installed, you’re set on dependencies.
##

```markdown

# Local‑Only Synonym Pipeline, Implementation Guide

This guide sets up a local synonym enrichment system using **WordNet (NLTK)** and **SpaCy embeddings**, with filtering, scoring, and SQLite storage. It runs fully offline, no API calls, no costs.
##

## 1. Setup

### Dependencies
Already installed: `spacy`, `nltk`, `textblob`.

One‑time setup:
```bash


python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
python -m spacy download en_core_web_md
```text
```
##

## 2. Scripts

### `scripts/local_synonyms.py`

```python


import json, re, os
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import spacy

lemmatizer = WordNetLemmatizer()
nlp = spacy.load("en_core_web_md")

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

def get_spacy_synonyms(word, candidates):
    doc = nlp(word)
    scored = [(cand, doc.similarity(nlp(cand))) for cand in candidates]
    return [w for w, s in sorted(scored, key=lambda x: -x[1])[:5]]

def build_synonyms(seed_words):
    merged = {}
    for w in seed_words:
        wn_syns = get_wordnet_synonyms(w)
        spacy_top = get_spacy_synonyms(w, wn_syns) if wn_syns else []
        merged[w] = {
            "wordnet": wn_syns,
            "spacy_top": spacy_top,
            "merged": sorted(set(wn_syns + spacy_top))
        }
    return merged

if __name__ == "__main__":
    seeds = ["joy", "anger", "trust"]  # replace with your glyph seeds
    result = build_synonyms(seeds)
    os.makedirs("data", exist_ok=True)
    json.dump(result, open("data/synonyms_local.json","w",encoding="utf-8"), indent=2)
```text
```
##

### `scripts/filter_synonyms.py`

```python


import json
import re
import os

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
    data = json.load(open(input_path, "r", encoding="utf-8"))
    filtered = {}
    for seed, sources in data.items():
        merged = sources.get("merged", [])
        clean = []
        for token in merged:
            token = normalize_token(token)
            if is_valid_token(token):
                clean.append(token)
        clean = list(dict.fromkeys(clean))
        filtered[seed] = {
            "merged_filtered": clean,
            "wordnet": sources.get("wordnet", []),
            "spacy_top": sources.get("spacy_top", [])
        }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    json.dump(filtered, open(output_path, "w", encoding="utf-8"), indent=2)
    print(f"Filtered synonyms written to {output_path}")

if __name__ == "__main__":
    filter_synonyms()
```text
```
##

### `scripts/score_synonyms.py`

```python


import json
import spacy

nlp = spacy.load("en_core_web_md")

def score_synonyms(input_path="data/synonyms_filtered.json", output_path="data/synonyms_scored.json"):
    data = json.load(open(input_path, "r", encoding="utf-8"))
    scored = {}

    for seed, sources in data.items():
        merged = sources.get("merged_filtered", [])
        seed_doc = nlp(seed)

        results = []
        for token in merged:
            try:
                score = seed_doc.similarity(nlp(token))
            except Exception:
                score = 0.0
            results.append({"word": token, "score": round(score, 3)})

        results = sorted(results, key=lambda x: -x["score"])

        scored[seed] = {
            "seed": seed,
            "synonyms_scored": results,
            "top_synonyms": [r["word"] for r in results[:5]],
            "provenance": {
                "wordnet": sources.get("wordnet", []),
                "spacy_top": sources.get("spacy_top", [])
            }
        }

    json.dump(scored, open(output_path, "w", encoding="utf-8"), indent=2)
    print(f"Scored synonyms written to {output_path}")

if __name__ == "__main__":
    score_synonyms()
```text
```
##

### `scripts/synonym_db.py`

```python


import sqlite3
import json
import os

DB_PATH = "data/synonyms.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS synonyms (
        seed TEXT,
        word TEXT,
        score REAL,
        source TEXT,
        PRIMARY KEY (seed, word, source)
    )
    """)
    conn.commit()
    conn.close()

def load_from_json(json_path="data/synonyms_scored.json"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = json.load(open(json_path, "r", encoding="utf-8"))
    for seed, entry in data.items():
        for syn in entry.get("synonyms_scored", []):
            cur.execute("""
            INSERT OR REPLACE INTO synonyms (seed, word, score, source)
            VALUES (?, ?, ?, ?)
            """, (seed, syn["word"], syn["score"], "scored"))
        for src in ["wordnet", "spacy_top"]:
            for w in entry.get("provenance", {}).get(src, []):
                cur.execute("""
                INSERT OR IGNORE INTO synonyms (seed, word, score, source)
                VALUES (?, ?, ?, ?)
                """, (seed, w, None, src))
    conn.commit()
    conn.close()

def query_synonyms(seed, top_k=5):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT word, score, source
    FROM synonyms
    WHERE seed = ?
    ORDER BY COALESCE(score, 0) DESC
    LIMIT ?
    """, (seed, top_k))
    rows = cur.fetchall()
    conn.close()
    return [{"word": w, "score": s, "source": src} for w, s, src in rows]

if __name__ == "__main__":
    init_db()
    load_from_json()
    print(query_synonyms("joy"))
```text
```
##

### `scripts/enrich_runner.py`

```python


import os
from synonym_db import init_db, load_from_json
from filter_synonyms import filter_synonyms
from score_synonyms import score_synonyms

def run_enrichment():
    print("Filtering synonyms...")
    filter_synonyms(
        input_path="data/synonyms_local.json",
        output_path="data/synonyms_filtered.json"
    )

    print("Scoring synonyms...")
    score_synonyms(
        input_path="data/synonyms_filtered.json",
        output_path="data/synonyms_scored.json"
    )

    print("Updating SQLite database...")
    init_db()
    load_from_json("data/synonyms_scored.json")

    print("Enrichment complete. Synonyms are refreshed in data/synonyms.db.")

if __name__ == "__main__":
    run_enrichment()
```text
```
##

## 3. Workflow

1. Run `local_synonyms.py` → produces `data/synonyms_local.json`.
2. Run `filter_synonyms.py` → produces `data/synonyms_filtered.json`.
3. Run `score_synonyms.py` → produces `data/synonyms_scored.json`.
4. Run `synonym_db.py` → builds `data/synonyms.db`.
5. Schedule `enrich_runner.py` with cron/Task Scheduler for automatic refresh.
##

## 4. Integration Example

```python


from synonym_db import query
