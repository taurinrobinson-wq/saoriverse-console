#!/usr/bin/env python3
"""Add a `base_emotion` column to `glyphs.db` and populate it using
heuristic keyword matching over `glyph_name` and `description`.

This helps the ToneCore UI pick an emotion when glyph rows are returned
by the parser.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'glyphs.db'

EMOTION_KEYWORDS = {
    'longing': ['long', 'longing', 'yearn', 'ache', 'yearning', 'longed'],
    'stress': ['stress', 'anxiet', 'tension', 'fear', 'panic', 'worry'],
    'joy': ['joy', 'happy', 'bliss', 'jubilan', 'celebrat', 'delight'],
    'calm': ['calm', 'still', 'quiet', 'peace', 'ground', 'settle'],
    'wonder': ['wonder', 'surpris', 'awe', 'insight', 'curiosity'],
    'resolve': ['resolv', 'resolve', 'determination', 'resolve'],
    'hope': ['hope', 'anticipat', 'expect'],
    'melancholy': ['melanchol', 'sad', 'grief', 'mourning', 'sorrow']
}


def infer_emotion(text: str):
    if not text:
        return None
    t = text.lower()
    scores = {}
    for emo, kw_list in EMOTION_KEYWORDS.items():
        for kw in kw_list:
            if kw in t:
                scores[emo] = scores.get(emo, 0) + 1
    if not scores:
        return None
    # return top-scoring emotion
    return max(scores.items(), key=lambda x: x[1])[0]


def main():
    if not DB.exists():
        print(
            f"glyphs.db not found at {DB}; run import_glyphs_json_to_sqlite.py first")
        return

    conn = sqlite3.connect(str(DB))
    try:
        cur = conn.cursor()
        # add column if missing
        cols = [r[1] for r in cur.execute("PRAGMA table_info(glyph_lexicon)")]
        if 'base_emotion' not in cols:
            cur.execute(
                'ALTER TABLE glyph_lexicon ADD COLUMN base_emotion TEXT')
            conn.commit()

        # fetch rows and update
        cur.execute('SELECT rowid, glyph_name, description FROM glyph_lexicon')
        rows = cur.fetchall()
        updated = 0
        for rowid, name, desc in rows:
            text = ' '.join([str(name or ''), str(desc or '')])
            emo = infer_emotion(text)
            if emo:
                cur.execute(
                    'UPDATE glyph_lexicon SET base_emotion = ? WHERE rowid = ?', (emo, rowid))
                updated += 1
        conn.commit()
        print(f"Populated base_emotion for {updated} rows in {DB}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
