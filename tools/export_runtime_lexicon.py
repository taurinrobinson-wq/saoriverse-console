#!/usr/bin/env python3
"""
Export a compact runtime lexicon that removes large `examples` arrays and keeps
only the fields needed for runtime matching.
"""
import json
import os

SRC = os.path.join('emotional_os', 'parser', 'signal_lexicon.json')
DST = os.path.join('emotional_os', 'parser', 'signal_lexicon_runtime.json')


def compact_signals(signals):
    out = {}
    for k, v in signals.items():
        # Keep keywords, frequency, community_contributed, and any other small fields
        entry = {}
        for fld in ('keywords', 'frequency', 'community_contributed'):
            if fld in v:
                entry[fld] = v[fld]
        # include small summary info: examples_count
        examples = v.get('examples')
        if examples:
            try:
                entry['examples_count'] = len(examples)
            except Exception:
                entry['examples_count'] = 1
        out[k] = entry
    return out


def main():
    with open(SRC, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    runtime = {}
    # compact signals
    signals = data.get('signals') or {}
    runtime['signals'] = compact_signals(signals)

    # copy all other top-level token mappings (these are usually token -> metadata)
    for k, v in data.items():
        if k == 'signals':
            continue
        # Attempt to remove any huge nested `examples` in token entries (unlikely)
        if isinstance(v, dict) and 'examples' in v:
            v = dict(v)
            v.pop('examples', None)
        runtime[k] = v

    # write runtime file
    with open(DST, 'w', encoding='utf-8') as fh:
        json.dump(runtime, fh, ensure_ascii=False, indent=2)

    print('Wrote', DST)


if __name__ == '__main__':
    main()
