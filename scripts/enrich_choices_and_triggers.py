#!/usr/bin/env python3
"""
Auto-populate `player_choices` and `narrative_triggers` in
`velinor/markdowngameinstructions/Glyph_Organizer.json` using heuristics.

Heuristics map keywords in storyline/theme/glyph_name/tags -> choices/triggers.
"""
import json
import os
import re

HERE = os.path.dirname(__file__)
DATA_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Organizer.json'))

# Mapping heuristics: keywords -> choices
CHOICE_MAP = {
    'follow': ['follow_or_ignore'],
    'followed': ['follow_or_ignore'],
    'follow him': ['follow_or_ignore'],
    'follow her': ['follow_or_ignore'],
    'follow route': ['follow_route_or_search'],
    'maze': ['follow_route_or_search'],
    'route': ['follow_route_or_search'],
    'hidden': ['follow_route_or_search'],
    'passage': ['follow_route_or_search'],
    'perform': ['observe_or_interrupt','follow_or_ignore'],
    'dance': ['observe_or_interrupt','follow_or_ignore'],
    'sit': ['sit_or_leave','hold_hand','say_nothing'],
    'stay': ['sit_or_leave','say_nothing'],
    'hold': ['hold_hand','sit_or_leave'],
    'hand': ['hold_hand'],
    'presence': ['sit_or_leave','say_nothing'],
    'witness': ['observe_or_intervene','sit_or_leave'],
    'trust': ['align_with_npc_or_oppose','choose_trust'],
    'betray': ['align_with_npc_or_oppose','choose_trust'],
    'trickster': ['align_with_npc_or_oppose','choose_trust'],
    'steal': ['collect_item','confront_or_ignore'],
    'steals': ['collect_item','confront_or_ignore'],
    'stolen': ['collect_item','confront_or_ignore'],
    'photograph': ['collect_item','return_item'],
    'find': ['collect_item','investigate_or_leave'],
    'finds': ['collect_item','investigate_or_leave'],
    'retrieve': ['collect_item','return_item'],
    'test': ['choose_trust','align_with_npc_or_oppose'],
    'choose': ['choose_trust','choose_sovereignty'],
    'mediate': ['mediate_or_ignore','observe_or_intervene'],
    'conflict': ['mediate_or_ignore','observe_or_intervene'],
    'song': ['observe_or_participate','join_or_watch'],
    'feast': ['observe_or_participate','join_or_watch'],
    'play': ['observe_or_participate','join_or_watch']
}

# Mapping heuristics: keywords -> triggers
TRIGGER_MAP = {
    'enters': ['player_enters_location'],
    'enter': ['player_enters_location'],
    'returns': ['player_returns_to_location'],
    'return': ['player_returns_to_location'],
    'mid-performance': ['npc_mid_performance'],
    'mid performance': ['npc_mid_performance'],
    'mid-performance_glitch': ['npc_mid_performance'],
    'glitch': ['npc_mid_performance','system_glitch_detected'],
    'whisper': ['witness_event','npc_whispers'],
    'whispers': ['witness_event','npc_whispers'],
    'sit': ['player_sits_with_npc'],
    'stay': ['player_sits_with_npc'],
    'found': ['player_collects_item'],
    'finds': ['player_collects_item'],
    'find': ['player_collects_item'],
    'collect': ['player_collects_item'],
    'collects': ['player_collects_item'],
    'maze': ['player_enters_hidden_passage'],
    'hidden': ['player_enters_hidden_passage'],
    'trickster': ['npc_gives_test'],
    'test': ['npc_gives_test'],
    'trust': ['npc_gives_test','alignment_check'],
    'betray': ['alignment_check']
}

def keywords_from_text(text):
    text = (text or '').lower()
    # split on non-word chars and keep tokens
    tokens = re.findall(r"[a-z0-9]+", text)
    return set(tokens)

def map_to_choices(tokens):
    found = []
    for kw, choices in CHOICE_MAP.items():
        if kw in tokens:
            for c in choices:
                if c not in found:
                    found.append(c)
    return found

def map_to_triggers(tokens):
    found = []
    for kw, triggers in TRIGGER_MAP.items():
        if kw in tokens:
            for t in triggers:
                if t not in found:
                    found.append(t)
    return found

def enrich():
    with open(DATA_PATH, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    # load rulebook
    RULEBOOK_PATH = os.path.normpath(os.path.join(HERE, '..', 'velinor', 'markdowngameinstructions', 'Glyph_Rules.json'))
    rules = {}
    if os.path.exists(RULEBOOK_PATH):
        with open(RULEBOOK_PATH, 'r', encoding='utf-8') as rf:
            rules = json.load(rf)

    for g in data.get('glyphs', []):
        text = ' '.join([g.get('original_storyline_text','') or '', g.get('theme','') or '', g.get('glyph_name','') or '', g.get('location','') or ''])
        tokens = keywords_from_text(text)
        # include tags as tokens
        tags = [t.lower() for t in (g.get('tags') or [])]
        for tag in tags:
            for t in re.findall(r"[a-z0-9]+", tag):
                tokens.add(t)

        # NPC authoritative overrides
        npc_name = (g.get('npc', {}).get('name') or '').lower()
        choices = []
        triggers = []
        if rules.get('npc_rules') and npc_name:
            for key, rule in rules['npc_rules'].items():
                if key in npc_name:
                    choices = rule.get('player_choices', [])[:]
                    triggers = rule.get('narrative_triggers', [])[:]
                    break

        if not choices:
            choices = map_to_choices(tokens)
        if not triggers:
            triggers = map_to_triggers(tokens)

        # defaults if nothing detected
        if not choices:
            # simple defaults by domain
            domain = (g.get('domain') or '').lower()
            if domain == 'presence':
                choices = ['sit_or_leave','say_nothing']
            elif domain == 'trust':
                choices = ['align_with_npc_or_oppose','choose_trust']
            elif domain == 'legacy':
                choices = ['collect_item','return_item']
            else:
                choices = ['observe_or_intervene']

        if not triggers:
            # default triggers
            if 'maze' in tokens or 'hidden' in tokens:
                triggers = ['player_enters_hidden_passage']
            else:
                triggers = ['player_enters_location']

        g['player_choices'] = choices
        g['narrative_triggers'] = triggers

    with open(DATA_PATH, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    print('Populated player_choices and narrative_triggers for', len(data.get('glyphs', [])))

if __name__ == '__main__':
    enrich()
