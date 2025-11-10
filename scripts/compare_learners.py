#!/usr/bin/env python3
"""Run HybridLearnerWithUserOverrides over a reclassified conversation and compare to existing learner output.

Writes: learning/imported_conversations/hybrid_compare_report.json
Prints a concise summary to stdout.
"""
import sys
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_json(p):
    with open(p, 'r') as f:
        return json.load(f)


def save_json(p, data):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w') as f:
        json.dump(data, f, indent=2)


def build_exchanges(parsed_turns):
    """Yield (user_text, ai_text) pairs from sequential turns."""
    for i in range(len(parsed_turns)-1):
        a = parsed_turns[i]
        b = parsed_turns[i+1]
        if a.get('role') in ('user', 'User') and b.get('role') in ('ai', 'assistant', 'system', 'AI'):
            yield a.get('text', ''), b.get('text', '')


def main():
    parsed_path = ROOT / 'learning/imported_conversations/parsed_conversation_reclassified.json'
    lexicon_results_path = ROOT / 'learning/imported_conversations/learning_results.json'

    if not parsed_path.exists():
        print(f"Missing parsed file: {parsed_path}")
        return 1

    parsed = load_json(parsed_path)

    # Import hybrid learner
    try:
        from emotional_os.learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides, get_hybrid_learner
    except Exception as e:
        print(f"Could not import HybridLearnerWithUserOverrides: {e}")
        return 2

    # Create instance (will load shared lexicon if present)
    learner = HybridLearnerWithUserOverrides(enable_anonymization=False)

    user_id = 'reclassified_test_user'

    # parsed file uses a top-level 'messages' array
    messages = parsed.get('messages') if isinstance(parsed, dict) else parsed
    if isinstance(messages, dict) and 'messages' in messages:
        messages = messages['messages']
    if not isinstance(messages, list):
        print('Parsed conversation has unexpected shape')
        return 3

    # Normalize turns to dicts with role/text
    turns = []
    for m in messages:
        # various schemas use 'type'/'content' or 'role'/'text'
        role = m.get('type') or m.get('role') or m.get('speaker')
        text = m.get('content') or m.get('text') or m.get('message')
        turns.append({'role': role, 'text': text})

    exchanges = list(build_exchanges(turns))
    results = []
    for user_text, ai_text in exchanges:
        res = learner.learn_from_exchange(
            user_id, user_text, ai_text, emotional_signals=None, glyphs=None)
        results.append(res)

    # Gather stats
    hybrid_stats = learner.get_learning_stats(user_id=None)
    user_stats = learner.get_learning_stats(user_id=user_id)

    # Load existing lexicon learner results for comparison if present
    lex_results = {}
    if lexicon_results_path.exists():
        try:
            lex_results = load_json(lexicon_results_path)
        except Exception:
            lex_results = {}

    report = {
        'hybrid_shared_stats': hybrid_stats,
        'hybrid_user_stats': user_stats,
        'hybrid_run_count': len(results),
        'hybrid_run_details': results,
        'lexicon_results_summary': lex_results.get('summary', lex_results) if isinstance(lex_results, dict) else lex_results,
    }

    out_path = ROOT / 'learning/imported_conversations/hybrid_compare_report.json'
    save_json(out_path, report)

    # Console summary
    print('\nHYBRID LEARNER RUN SUMMARY')
    print('exchanges processed:', len(exchanges))
    print('shared signals in lexicon:',
          hybrid_stats.get('signals_in_shared_lexicon'))
    print('user signals learned:', user_stats.get('signals_learned'))
    print('\nTop user signals (if any):')
    overrides_file = Path(learner.user_overrides_dir) / \
        f"{user_id}_lexicon.json"
    if overrides_file.exists():
        try:
            u = load_json(overrides_file)
            signals = u.get('signals', {})
            for sig, data in signals.items():
                print(
                    f" - {sig}: {len(data.get('keywords', []))} keywords, freq={data.get('frequency')}")
        except Exception as e:
            print('Could not read user overrides:', e)
    else:
        print(' None')

    print('\nWROTE:', out_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
