"""
Small harness to run conversational scenarios through the existing parser and collector.
Run from repo root: python3 dev_tools/simulate_conversations.py
Outputs a CSV with input, mode, response, and whether response looks 'canned' heuristically.
"""
import csv
import sys
import os
import re
import random

# ensure repo root on path
sys.path.insert(0, os.path.abspath('.'))

from emotional_os.glyphs import signal_parser as sp

SCENARIOS = [
    # profile queries
    "Can you tell me about yourself?",
    "who are you",
    "what do you do",
    "tell me more about urself",
    # greetings/reciprocal
    "how are you doing",
    "how r u",
    # emotional expressions
    "I'm feeling very sad and alone today",
    "I feel angry at my partner, they ignored me",
    "I can't sleep and it makes me anxious",
    # ambiguous
    "I had a weird dream last night",
    "I lost my job and I'm scared",
    # paraphrases and misspellings
    "tell me about uourselv",
    "how do you doin",
    # long narrative
    "This morning I woke up and everything felt heavy. I tried to get out of bed but the thoughts kept looping. I don't know what to do next.",
    "I'm okay, but sometimes I get panic attacks when the room feels too small",
    "I just want someone to listen without advice",
]

OUT_CSV = 'dev_tools/simulate_output.csv'

# When running a larger sweep, we'll randomly sample from the SCENARIOS list
# to produce a larger dataset for provenance analysis.
N_ITERATIONS = 500
RANDOM_SEED = 42

# naive canned heuristics: detect if response contains known glyph markers or exact templates
CANNED_MARKERS = [
    "Still Recognition",
    "Ritual",
    "glyph",
    "Here's a ritual",
    "Try this ritual",
]


def looks_canned(resp: str) -> bool:
    if not resp:
        return True
    lower = resp.lower()
    # if response is very short and templated
    if len(lower.split()) < 6:
        return True
    for m in CANNED_MARKERS:
        if m.lower() in lower:
            return True
    # heuristic: many repeated words like "try" "breathe" -> could be ritual
    if re.search(r"\b(try|breathe|repeat|ritual)\b", lower):
        return True
    return False


def main():
    rows = []
    random.seed(RANDOM_SEED)

    # Build a list of inputs by sampling the SCENARIOS list
    inputs = []
    for i in range(N_ITERATIONS):
        base = random.choice(SCENARIOS)
        # 10% chance to append a small punctuation/noise to simulate typos
        if random.random() < 0.1:
            base = base + random.choice([".", "..", "!?", "?"])
        inputs.append((i + 1, base))

    for idx, s in inputs:
        try:
            # call the parser's main entry if present
            response_text = None
            response_source = None
            best_glyph = None
            debug_sql = ""

            # prefer top-level parse function if available
            if hasattr(sp, 'parse_input'):
                lexicon_path = 'velonix_lexicon.json' if os.path.exists('velonix_lexicon.json') else 'emotional_os/glyphs/learned_lexicon.json'
                db_path = 'emotional_os/glyphs/glyphs.db' if os.path.exists('emotional_os/glyphs/glyphs.db') else 'glyphs.db'
                rdict = sp.parse_input(s, lexicon_path, db_path=db_path, conversation_context=None)
                # parse_input returns a dict; extract the selected fields
                if isinstance(rdict, dict):
                    response_text = rdict.get('voltage_response')
                    response_source = rdict.get('response_source')
                    best_glyph = rdict.get('best_glyph')
                    debug_sql = rdict.get('debug_sql', '') or ''
                else:
                    response_text = str(rdict)
            else:
                # Fallback to simple reciprocal detector when parse_input is absent
                response_text = sp._detect_and_respond_to_reciprocal_message(s)

            canned = looks_canned(response_text if response_text else '')
            # Normalize best_glyph to a printable string (glyph_name or repr)
            if isinstance(best_glyph, dict):
                best_glyph_str = best_glyph.get('glyph_name') or repr(best_glyph)
            else:
                best_glyph_str = str(best_glyph) if best_glyph is not None else ''

            # Clean debug_sql to single-line for CSV readability
            debug_sql_clean = re.sub(r"\s+", " ", debug_sql).strip()

            rows.append((idx, s, response_text, response_source, best_glyph_str, debug_sql_clean, canned))
        except Exception as e:
            rows.append((idx, s, f'ERROR: {e}', 'error', '', '', True))

    # write csv
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['iteration', 'input', 'response', 'response_source', 'best_glyph', 'debug_sql', 'looks_canned'])
        for r in rows:
            iter_idx, inp, resp, src, glyph_name, sql, canned = r
            # Ensure response is scalar and safe for CSV
            resp = resp if resp is not None else ''
            src = src if src is not None else ''
            glyph_name = glyph_name if glyph_name is not None else ''
            sql = sql if sql is not None else ''
            w.writerow([iter_idx, inp, resp, src, glyph_name, sql, canned])

    print(f'Wrote {OUT_CSV}')

if __name__ == '__main__':
    main()
