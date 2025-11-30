#!/usr/bin/env python3
"""SQLite storage for scored synonyms.

Creates `data/synonyms.db` and provides load/query helpers.
"""
import json
import os
import sqlite3
from pathlib import Path

DB_PATH = "data/synonyms.db"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS synonyms (
        seed TEXT,
        word TEXT,
        score REAL,
        source TEXT,
        PRIMARY KEY (seed, word, source)
    )
    """
    )
    conn.commit()
    conn.close()


def load_from_json(json_path="data/synonyms_scored.json"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    for seed, entry in data.items():
        for syn in entry.get("synonyms_scored", []):
            cur.execute(
                """
            INSERT OR REPLACE INTO synonyms (seed, word, score, source)
            VALUES (?, ?, ?, ?)
            """,
                (seed, syn["word"], syn["score"], "scored"),
            )
        for src in ["wordnet", "spacy_top"]:
            for w in entry.get("provenance", {}).get(src, []):
                cur.execute(
                    """
                INSERT OR IGNORE INTO synonyms (seed, word, score, source)
                VALUES (?, ?, ?, ?)
                """,
                    (seed, w, None, src),
                )
    conn.commit()
    conn.close()


def query_synonyms(seed, top_k=5):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
    SELECT word, score, source
    FROM synonyms
    WHERE seed = ?
    ORDER BY COALESCE(score, 0) DESC
    LIMIT ?
    """,
        (seed, top_k),
    )
    rows = cur.fetchall()
    conn.close()
    return [{"word": w, "score": s, "source": src} for w, s, src in rows]


if __name__ == "__main__":
    init_db()
    # safe: only load if file exists
    p = Path("data/synonyms_scored.json")
    if p.exists():
        load_from_json("data/synonyms_scored.json")
    print(query_synonyms("joy"))
