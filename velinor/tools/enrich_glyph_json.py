#!/usr/bin/env python3
"""
Enrich `Glyph_Organizer.json` by auto-populating `tone_integration` and
`remnants_integration` fields using keyword heuristics.

Writes the enriched JSON back to the same path.
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(__file__)
DATA_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Organizer.json'))

import json

# Load authoritative rulebook if present
RULEBOOK_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Rules.json'))
if os.path.exists(RULEBOOK_PATH):
    with open(RULEBOOK_PATH, 'r', encoding='utf-8') as rf:
        RULES = json.load(rf)
else:
    RULES = {}

# Fallback keyword maps (used when no authoritative rule applies)
TONES_MAP = {
    'somber': ['ache', 'loss', 'grief', 'mourning', 'sorrow', 'hollow', 'weary', 'quiet', 'tender', 'widow'],
    'mythic': ['ancestry', 'lineage', 'ritual', 'legacy', 'covenant', 'ancestor', 'tomb', 'ossuary', 'myth', 'inherit'],
    'intimate': ['presence', 'witness', 'touch', 'hand', 'quiet', 'intimate', 'hums', 'humming', 'sit', 'stay'],
    'eerie': ['mirage', 'ghost', 'echo', 'phantom', 'apparition', 'haunt', 'silent', 'silence', 'cloak', 'cloaked', 'whisper'],
    'hopeful': ['hope', 'return', 'restore', 'restor', 'reun', 'arrival', 'reunion', 'joy', 'renewal', 'arrival', 'return'],
    'fragmented': ['fracture', 'fragment', 'distort', 'corrupt', 'broken', 'shatter', 'shattered', 'stolen', 'stolen memory'],
    'ritualistic': ['ritual', 'ceremony', 'pass', 'fire', 'covenant', 'rite', 'heirloom', 'dance', 'song']
}

REMA_MAP = {
    'broken_corelink': ['corelink', 'console', 'node', 'network', 'data', 'tech', 'system', 'corelink'],
    'memory_echoes': ['memory', 'remember', 'forgot', 'stolen memory', 'echo', 'echoes', 'mirage'],
    'ghost_signals': ['phantom', 'signal', 'ghost', 'whisper', 'rumor', 'rumour', 'echo'],
    'corrupted_data': ['corrupt', 'corrupted', 'glitch', 'glitching', 'distortion', 'distorted', 'shatter', 'shattered'],
    'abandoned_rituals': ['ritual', 'ceremony', 'inherit', 'pass', 'song', 'dance', 'fire'],
    'environmental_scars': ['ruins', 'desert', 'swamp', 'market', 'harbor', 'tower', 'ossuary', 'cavern', 'shrine', 'archive', 'bridge', 'dock']
}

def find_matches(text, mapping):
    found = set()
    text = (text or '').lower()
    for key, keywords in mapping.items():
        for kw in keywords:
            if kw.lower() in text:
                found.add(key)
                break
    return sorted(found)

def map_tones(text, domain, tags):
    text_low = (text or '').lower()
    tones = set()
    for tone, kws in TONES_MAP.items():
        for kw in kws:
            if kw in text_low:
                tones.add(tone)
                break

    # domain-based defaults
    if not tones:
        if domain.lower() == 'ache':
            tones.add('somber')
        elif domain.lower() == 'collapse':
            tones.add('fragmented')
        elif domain.lower() == 'presence':
            tones.add('intimate')
        elif domain.lower() == 'joy':
            tones.add('hopeful')
        elif domain.lower() == 'legacy':
            tones.add('mythic')

    # boost from tags
    for t in tags:
        t = t.lower()
        if 'memory' in t or 'forgot' in t:
            tones.add('fragmented')
        if 'dance' in t or 'lineage' in t or 'inherit' in t:
            tones.add('mythic')

    return sorted(tones)

def map_remnants(text, tags):
    res = set(find_matches(text, REMA_MAP))
    # also check tags for environmental hints
    for t in tags:
        t = t.lower()
        if any(k in t for k in ('desert','swamp','market','harbor','archive','shrine','ruins','ossuary','tower','bridge','cavern')):
            res.add('environmental_scars')
    return sorted(res)

def enrich():
    with open(DATA_PATH, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    count = 0
    for g in data.get('glyphs', []):
        text = ' '.join([g.get('original_storyline_text','') or '', g.get('theme','') or '', g.get('glyph_name','') or ''])
        tags = g.get('tags', []) or []
        domain = g.get('domain','') or ''

        # Attempt authoritative NPC rules first
        npc_name = (g.get('npc', {}).get('name') or '').lower()
        tones = []
        rems = []
        if RULES.get('npc_rules') and npc_name:
            # match any rule key contained in the npc name
            for key, rule in RULES['npc_rules'].items():
                if key in npc_name:
                    tones = rule.get('tone_integration', [])
                    rems = rule.get('remnants_integration', [])
                    break

        # If no NPC rule matched, use domain defaults
        if not tones and RULES.get('domain_defaults'):
            domdef = RULES['domain_defaults'].get(domain)
            if domdef:
                tones = domdef.get('tone', [])
                rems = domdef.get('remnants', [])

        # Fall back to heuristic mapping if still empty
        if not tones:
            tones = map_tones(text, domain, tags)
        if not rems:
            rems = map_remnants(text, tags)

        g['tone_integration'] = tones
        g['remnants_integration'] = rems
        count += 1

    # write back
    with open(DATA_PATH, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    print(f'Enriched {count} glyphs (tone + remnants)')

if __name__ == '__main__':
    enrich()
