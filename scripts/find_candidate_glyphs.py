#!/usr/bin/env python3
"""Search for candidate glyph rows matching curated labels that weren't found exactly.

Usage: python3 scripts/find_candidate_glyphs.py

Prints top candidates for each missing curated entry using substring matching and difflib.
"""
import os
import sqlite3
import re
import difflib

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(
    __file__), '..', 'emotional_os', 'glyphs', 'glyphs.db'))

MISSING = [
    "Resonance fragments without system...",
    "It entangles it — so that the ache is...",
    "That’s the quiet scream of coherence in...",
]

WORD_RE = re.compile(r"[A-Za-z\u0080-\uFFFF0-9]+")


def tokens(s):
    if not s:
        return []
    return [w.lower() for w in WORD_RE.findall(s) if len(w) > 2]


def score_match(missing_tokens, glyph_name, description):
    # simple token overlap score
    gn = (glyph_name or '').lower()
    desc = (description or '').lower()
    score = 0
    for t in set(missing_tokens):
        if t in gn:
            score += 3
        elif t in desc:
            score += 2
    return score


def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT rowid, glyph_name, description FROM glyph_lexicon")
    rows = cur.fetchall()
    glyphs = [{'rowid': r[0], 'glyph_name': r[1] or '',
               'description': r[2] or ''} for r in rows]

    all_names = [g['glyph_name'] for g in glyphs]

    for missing in MISSING:
        print('\n=== Candidates for:')
        print(missing)
        m_tokens = tokens(missing)
        candidates = []
        for g in glyphs:
            s = score_match(m_tokens, g['glyph_name'], g['description'])
            candidates.append(
                (s, g['glyph_name'], g['description'], g['rowid']))

        # add difflib close matches to boost
        close = difflib.get_close_matches(
            missing, all_names, n=10, cutoff=0.55)
        close_set = set(close)

        # sort by score then whether in close_set
        candidates.sort(key=lambda x: (x[0], x[1] in close_set), reverse=True)

        # present top results with details; include any close matches even if score 0
        shown = 0
        seen = set()
        for s, name, desc, rid in candidates:
            if shown >= 12:
                break
            if name in seen:
                continue
            seen.add(name)
            marker = ''
            if name in close_set:
                marker = ' (difflib-close)'
            if s == 0 and name not in close_set:
                # skip low-relevance unless we have very few candidates shown
                continue
            snippet = (
                desc[:120] + '...') if desc and len(desc) > 120 else desc
            print(f" - rowid={rid} score={s}{marker} | {name} | {snippet}")
            shown += 1

        # if we had no token-score hits, show pure difflib suggestions
        if shown == 0 and close:
            print('\n  difflib suggestions:')
            for c in close:
                print(f"   - {c}")

    conn.close()


if __name__ == '__main__':
    main()
