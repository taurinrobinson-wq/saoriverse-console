#!/usr/bin/env python3
import json
import datetime
from pathlib import Path

def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        try:
            return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
        except Exception:
            return None

p_demo = Path('demos/learning/detected_patterns.json')
p_learn = Path('learning/detected_patterns.json')

if not p_demo.exists() or not p_learn.exists():
    print('One or both files missing:', p_demo.exists(), p_learn.exists())
    raise SystemExit(1)

ad = json.loads(p_demo.read_text(encoding='utf8'))
bl = json.loads(p_learn.read_text(encoding='utf8'))

merged = {}
all_keys = set(ad.keys()) | set(bl.keys())
for k in sorted(all_keys):
    va = ad.get(k)
    vb = bl.get(k)
    if va and not vb:
        merged[k] = va
        continue
    if vb and not va:
        merged[k] = vb
        continue
    # both exist
    ent = {}
    # emotions: union preserving order, prefer ordering from 'learning' then 'demos'
    seen = []
    for w in (vb.get('emotions', []) + va.get('emotions', [])):
        if w not in seen:
            seen.append(w)
    ent['emotions'] = seen
    # intensity: choose majority or fallback to vb then va
    ent['intensity'] = va.get('intensity', vb.get('intensity'))
    # context_words union
    seen = []
    for w in (vb.get('context_words', []) + va.get('context_words', [])):
        if w not in seen:
            seen.append(w)
    ent['context_words'] = seen
    # frequency: sum
    ent['frequency'] = (va.get('frequency') or 0) + (vb.get('frequency') or 0)
    # first_seen: earliest
    fs_a = parse_iso(va.get('first_seen'))
    fs_b = parse_iso(vb.get('first_seen'))
    first = None
    if fs_a and fs_b:
        first = min(fs_a, fs_b)
    else:
        first = fs_a or fs_b
    ent['first_seen'] = first.isoformat() if first else (va.get('first_seen') or vb.get('first_seen'))
    # last_seen: latest
    ls_a = parse_iso(va.get('last_seen'))
    ls_b = parse_iso(vb.get('last_seen'))
    last = None
    if ls_a and ls_b:
        last = max(ls_a, ls_b)
    else:
        last = ls_a or ls_b
    ent['last_seen'] = last.isoformat() if last else (va.get('last_seen') or vb.get('last_seen'))
    merged[k] = ent

# Write merged file to both paths (pretty-printed)
for p in (p_demo, p_learn):
    p.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
print('Merged', len(merged), 'entries to', p_demo, 'and', p_learn)
