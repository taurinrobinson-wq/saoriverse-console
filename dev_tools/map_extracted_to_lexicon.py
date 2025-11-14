#!/usr/bin/env python3
import json
import re
from pathlib import Path

LEX_PATH = Path('emotional_os/glyphs/glyph_lexicon_rows_validated.json')
OUT_CSV = Path('dev_tools/glyph_mapping.csv')

EXTRACTED = [
    {"name": "feeling_unmoored",
        "phrase": "I feel unmoored and need something to hold onto"},
    {"name": "seeking_stability",
        "phrase": "I feel unmoored and need something to hold onto"},
    {"name": "anger", "phrase": "I'm furious about how they dismissed me at work"},
    {"name": "dismissal", "phrase": "I'm furious about how they dismissed me at work"},
    {"name": "longing", "phrase": "I miss her so much it aches"},
    {"name": "heartache", "phrase": "I miss her so much it aches"},
    {"name": "quiet_joy", "phrase": "There's a quiet joy in watching them sleep"},
    {"name": "overwhelm", "phrase": "I'm overwhelmed by everything I'm carrying"}
]

# simple levenshtein


def levenshtein(a: str, b: str) -> int:
    if a == b: return 0
    if not a: return len(b)
    if not b: return len(a)
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[m][n]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# load lexicon
with open(LEX_PATH, 'r', encoding='utf-8') as f:
    lex = json.load(f)

rows = []
all_names = []
for r in lex:
    name = r.get('glyph_name') or r.get('name') or r.get('glyph') or ''
    desc = r.get('description') or ''
    all_names.append({'name': name, 'desc': desc})

# match heuristics
lines = []
lines.append('extracted_name,source_phrase,matched,top_match,match_score,match_type,suggested_synonyms,suggested_triggers,new_glyph')

for ex in EXTRACTED:
    ex_name = ex['name']
    ex_phrase = ex['phrase']
    ex_norm = norm(ex_name)
    candidates = []
    for entry in all_names:
        gname = entry['name']
        gdesc = entry['desc']
        g_norm = norm(gname)
        # exact token match
        token_overlap = 0
        ex_tokens = set(ex_norm.split())
        g_tokens = set(g_norm.split())
        overlap = ex_tokens & g_tokens
        token_overlap = len(overlap)
        # substring checks in name or desc
        substr = 1 if ex_norm in g_norm or ex_norm in norm(gdesc) else 0
        # levenshtein similarity
        a = ex_norm.replace(' ', '')
        b = g_norm.replace(' ', '')
        dist = levenshtein(a, b)
        maxlen = max(len(a), len(b)) if max(len(a), len(b)) > 0 else 1
        sim = 1 - dist/maxlen
        # overall score
        score = token_overlap*0.5 + substr*0.4 + max(0, sim)*0.6
        candidates.append((score, gname, gdesc, token_overlap, substr, sim))
    candidates.sort(reverse=True, key=lambda x: x[0])
    top = candidates[0]
    top_score, top_name, top_desc, tover, tsubstr, tsim = top
    matched = 'Yes' if top_score > 0.6 else 'No'
    match_type = 'exact' if tover > 0 or tsubstr else (
        'fuzzy' if tsim > 0.65 else 'none')
    # suggestions: synonyms/triggers from phrase tokens and common paraphrases
    phrase_tokens = [t for t in norm(ex_phrase).split() if len(t) > 2]
    suggested_synonyms = []
    # simple heuristics
    if ex_name in ['feeling_unmoored', 'seeking_stability']:
        suggested_synonyms = ['adrift', 'ungrounded',
            'anchored', 'stability', 'secure']
    elif ex_name in ['anger', 'dismissal']:
        suggested_synonyms = ['angry', 'irate',
            'dismissed', 'rejected', 'undervalued']
    elif ex_name in ['longing', 'heartache']:
        suggested_synonyms = ['miss', 'ache', 'yearning', 'grief', 'nostalgia']
    elif ex_name in ['quiet_joy']:
        suggested_synonyms = ['serene joy', 'contentment', 'peaceful joy']
    elif ex_name in ['overwhelm']:
        suggested_synonyms = ['burdened', 'swamped', 'stressed', 'overloaded']
    else:
        suggested_synonyms = phrase_tokens[:5]
    # suggested triggers: short phrases
    suggested_triggers = []
    if ex_name == 'feeling_unmoored': suggested_triggers = [
        'unmoored', 'need something to hold onto', 'adrift']
    if ex_name == 'seeking_stability': suggested_triggers = [
        'need something to hold onto', 'seek stability', 'looking for solid ground']
    if ex_name == 'anger': suggested_triggers = [
        'furious', 'angry', 'they dismissed me', 'I was dismissed']
    if ex_name == 'dismissal': suggested_triggers = [
        'dismissed', 'they dismissed me', 'felt disregarded']
    if ex_name == 'longing': suggested_triggers = [
        'I miss her', 'I miss them', 'yearning', 'I miss']
    if ex_name == 'heartache': suggested_triggers = [
        'it aches', 'heartache', 'hurts so much']
    if ex_name == 'quiet_joy': suggested_triggers = [
        'quiet joy', 'watching them sleep', 'serene happiness']
    if ex_name == 'overwhelm': suggested_triggers = [
        'overwhelmed', 'everything I\'m carrying', 'burdened by']

    new_glyph = 'no' if matched == 'Yes' else 'yes'
    # if top match has low score but contains related token like 'longing', treat as matched
    if ex_name in ['longing', 'heartache']:
        # detect presence of 'long' in top_name
        if 'long' in top_name.lower() or 'ache' in top_name.lower():
            matched = 'Yes'; new_glyph = 'no'; match_type = 'token'
    # write CSV line
    line = (
        f'{ex_name}, {"\""+ex_phrase.replace("\"", "\"\"")+
