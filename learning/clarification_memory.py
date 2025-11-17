"""Clarification memory: store and lookup user clarification traces.

Storage format: JSONL at `learning/clarification_memory.jsonl`.
Each record is a dict with keys:
  - timestamp (ISO)
  - trigger (normalized user trigger phrase)
  - clarified_as (optional intent or canonical label)
  - original_input
  - system_response
  - user_clarification
  - metadata (optional dict)

This module provides simple append and lookup functions used by tools
and runtime components to pre-bias ambiguous inputs based on past clarifications.
"""
from pathlib import Path
import json
import datetime
import re
import uuid
from collections import defaultdict
from typing import Optional, List, Dict, Any


DEFAULT_PATH = Path('learning/clarification_memory.jsonl')


def _normalize_trigger(text: str) -> str:
    if not text:
        return ''
    t = text.lower().strip()
    # remove punctuation and collapse whitespace
    t = re.sub(r"[^a-z0-9\s]", ' ', t)
    t = re.sub(r"\s+", ' ', t)
    return t


def record_correction(trigger: str,
                      clarified_as: Optional[str],
                      original_input: str,
                      system_response: str,
                      user_clarification: str,
                      metadata: Optional[Dict[str, Any]] = None,
                      path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        'record_id': str(uuid.uuid4()),
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
        'trigger': _normalize_trigger(trigger),
        'clarified_as': clarified_as,
        'original_input': original_input,
        'system_response': system_response,
        'user_clarification': user_clarification,
        'metadata': metadata or {},
    }
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def load_all(path: Path = DEFAULT_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def aggregate_by_trigger(path: Path = DEFAULT_PATH) -> Dict[str, Dict[str, Any]]:
    records = load_all(path)
    agg = defaultdict(lambda: defaultdict(int))
    last_seen = {}
    for r in records:
        trig = r.get('trigger') or ''
        clarified = r.get('clarified_as') or r.get('user_clarification') or ''
        agg[trig][clarified] += 1
        last_seen[(trig, clarified)] = r.get('timestamp')

    result = {}
    for trig, mapping in agg.items():
        # compute a simple best suggestion and total count
        best = None
        best_count = 0
        total = 0
        choices = []
        for clarified, cnt in mapping.items():
            total += cnt
            choices.append({'clarified': clarified, 'count': cnt,
                           'last_seen': last_seen.get((trig, clarified))})
            if cnt > best_count:
                best_count = cnt
                best = clarified
        result[trig] = {
            'trigger': trig,
            'total': total,
            'best': best,
            'best_count': best_count,
            'choices': sorted(choices, key=lambda x: (-x['count'], x.get('last_seen'))),
        }
    return result


def suggest_for_input(user_input: str, min_count: int = 1, path: Path = DEFAULT_PATH) -> Optional[Dict[str, Any]]:
    trig = _normalize_trigger(user_input)
    agg = aggregate_by_trigger(path)
    # exact match first
    if trig in agg and agg[trig]['best_count'] >= min_count:
        info = agg[trig]
        confidence = info['best_count'] / max(1, info['total'])
        return {'trigger': trig, 'suggestion': info['best'], 'confidence': round(confidence, 3), 'meta': info}
    # try substring match (loose)
    for t, info in agg.items():
        if t and t in trig and info['best_count'] >= min_count:
            confidence = info['best_count'] / max(1, info['total'])
            return {'trigger': t, 'suggestion': info['best'], 'confidence': round(confidence, 3), 'meta': info}
    return None


if __name__ == '__main__':
    # quick demo
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--record', action='store_true')
    p.add_argument('--trigger')
    p.add_argument('--clarified_as')
    p.add_argument('--original')
    p.add_argument('--system')
    p.add_argument('--clarification')
    p.add_argument('--query')
    args = p.parse_args()
    if args.record:
        if not args.trigger or not args.original or not args.system or not args.clarification:
            print(
                'To record you must provide --trigger --original --system --clarification')
        else:
            record_correction(args.trigger, args.clarified_as,
                              args.original, args.system, args.clarification)
            print('Recorded correction for trigger:', args.trigger)
    elif args.query:
        s = suggest_for_input(args.query)
        print('Suggestion for', args.query, '->', s)
    else:
        print('No action specified. Use --record or --query')
