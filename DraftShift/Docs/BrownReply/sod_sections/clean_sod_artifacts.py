#!/usr/bin/env python3
import os
import json
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {'objections'}

def clean_text(s):
    orig = s
    # normalize NBSP -> space
    s = s.replace('\u00A0', ' ')
    # replace common ligatures with ascii equivalents (preserve words)
    s = s.replace('\uFB01', 'fi').replace('\uFB02', 'fl')
    # remove control chars except newline and tab and carriage return
    s = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', s)
    # collapse multiple spaces to single
    s = re.sub(r' {2,}', ' ', s)
    # trim spaces at line ends and starts
    lines = [line.strip() for line in s.splitlines()]
    s = '\n'.join(lines)
    # remove spaces before punctuation , . : ; ? ! )
    s = re.sub(r'\s+([,\.:;\?\)!%])', r'\1', s)
    # ensure single space after punctuation if directly followed by a letter/quote/paren
    s = re.sub(r'([,\.:;\?\)!%])([A-Za-z\"\(])', r'\1 \2', s)
    # collapse >2 blank lines to 2
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s if s != orig else orig

changed = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip objections dir
    parts = set(os.path.relpath(dirpath, ROOT).split(os.sep))
    if parts & SKIP_DIRS:
        continue
    for fn in filenames:
        if not fn.lower().endswith('.json'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f'WARN: could not read {path}: {e}')
            continue
        if 'text' not in data:
            continue
        orig = data['text']
        cleaned = clean_text(orig)
        if cleaned != orig:
            data['text'] = cleaned
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                changed.append(path)
            except Exception as e:
                print(f'ERROR: writing {path}: {e}')

print(f'Cleaned {len(changed)} files')
for p in changed:
    print('WROTE', p)
