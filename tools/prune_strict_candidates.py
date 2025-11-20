#!/usr/bin/env python3
"""
Find normalized-name glyph groups meeting stricter prune criteria:
 - group size >= 10
 - all members have zero usage
 - all members have no response_template

Writes `tools/glyphs_prune_strict.csv` with candidate rows (keep id, remove ids list etc.)
"""
import sqlite3
import os
import csv
import re
import unicodedata
from collections import defaultdict

DB = os.path.join('emotional_os', 'glyphs', 'glyphs.db')
OUT = os.path.join('tools', 'glyphs_prune_strict.csv')

if not os.path.exists(DB):
    print('DB not found at', DB)
    raise SystemExit(2)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# load glyph rows
cur.execute(
    'SELECT id,glyph_name,display_name,response_template FROM glyph_lexicon')
rows = cur.fetchall()

# usage counts
usage = {}
for r in cur.execute('SELECT glyph_name, COUNT(*) FROM glyph_usage_log GROUP BY glyph_name'):
    usage[r[0]] = r[1]


def normalize(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKD', s)
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# group by normalized name
groups = defaultdict(list)
for id_, name, dname, template in rows:
    key = normalize(name or dname)
    groups[key].append({'id': id_, 'name': name or '',
                       'display_name': dname or '', 'template': template or ''})

candidates = []
for norm, members in groups.items():
    if not norm:
        continue
    if len(members) < 10:
        continue
    # check usage and templates
    all_zero_usage = True
    any_template = False
    for m in members:
        nm = m['name']
        u = usage.get(nm, 0)
        if u != 0:
            all_zero_usage = False
            break
        if m['template'] and m['template'].strip():
            any_template = True
            break
    if not all_zero_usage:
        continue
    if any_template:
        continue
    # candidate: choose keep as lowest id
    keep = min(m['id'] for m in members)
    remove_ids = [m['id'] for m in members if m['id'] != keep]
    candidates.append({'norm': norm, 'count': len(members), 'keep': keep, 'remove_ids': remove_ids,
                      'sample_names': '; '.join((m['name'] or m['display_name'])[:80] for m in members[:10])})

# write
os.makedirs('tools', exist_ok=True)
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=[
                            'norm', 'count', 'keep', 'remove_count', 'remove_ids', 'sample_names'])
    writer.writeheader()
    for c in sorted(candidates, key=lambda x: -x['count']):
        writer.writerow({'norm': c['norm'], 'count': c['count'], 'keep': c['keep'], 'remove_count': len(
            c['remove_ids']), 'remove_ids': ','.join(map(str, c['remove_ids'])), 'sample_names': c['sample_names']})

print('Wrote', OUT, 'with', len(candidates), 'candidate groups')
conn.close()
