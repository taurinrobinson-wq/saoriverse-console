#!/usr/bin/env python3
"""
Check parity between the full lexicon and the runtime lexicon for the
fields the runtime will use (signal keys, keywords, frequency, and token
mapping keys).
"""
import json
import os
import sys

FULL = os.path.join('emotional_os', 'parser', 'signal_lexicon.json')
RUNTIME = os.path.join('emotional_os', 'parser', 'signal_lexicon_runtime.json')


def load(path):
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def main():
    if not os.path.exists(FULL):
        print('Full lexicon not found at', FULL)
        sys.exit(2)
    if not os.path.exists(RUNTIME):
        print('Runtime lexicon not found at', RUNTIME)
        sys.exit(2)

    full = load(FULL)
    rt = load(RUNTIME)

    full_signals = set((full.get('signals') or {}).keys())
    rt_signals = set((rt.get('signals') or {}).keys())

    missing_in_rt = full_signals - rt_signals
    extra_in_rt = rt_signals - full_signals

    if missing_in_rt:
        print('Signals missing in runtime:', sorted(missing_in_rt))
    else:
        print('All signals present in runtime')

    if extra_in_rt:
        print('Extra signals in runtime:', sorted(extra_in_rt))

    # compare keywords and frequency for each signal (if present in both)
    mismatches = []
    for s in sorted(full_signals & rt_signals):
        fentry = full['signals'].get(s, {})
        rentry = rt['signals'].get(s, {})
        fk = set((fentry.get('keywords') or []))
        rk = set((rentry.get('keywords') or []))
        if fk != rk:
            mismatches.append((s, 'keywords', fk, rk))
        ff = fentry.get('frequency')
        rf = rentry.get('frequency')
        if ff != rf:
            mismatches.append((s, 'frequency', ff, rf))

    if mismatches:
        print('Signal mismatches:')
        for m in mismatches:
            print(' ', m)
    else:
        print('Signal keyword/frequency parity OK')

    # token mappings keys parity
    full_token_keys = set(k for k in full.keys() if k != 'signals')
    rt_token_keys = set(k for k in rt.keys() if k != 'signals')
    missing_tokens = full_token_keys - rt_token_keys
    if missing_tokens:
        print('Token mappings missing in runtime (showing 20):')
        for i, t in enumerate(sorted(missing_tokens)):
            if i >= 20:
                break
            print(' ', t)
    else:
        print('Token mapping keys parity OK')

    # done


if __name__ == '__main__':
    main()
