#!/usr/bin/env python3
import sqlite3
import os
import csv
import re

DB = os.path.join('emotional_os', 'glyphs', 'glyphs.db')
OUT = os.path.join('tools', 'glyphs_review_candidates.csv')


def normalize_name(s: str) -> str:
    if not s:
        return ''
    return re.sub(r'[^0-9a-z]', '', s.lower())


def analyze():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, glyph_name, description, display_name FROM glyph_lexicon")
    rows = cur.fetchall()

    # precompute usage counts and versions
    usage_counts = {}
    for r in cur.execute('SELECT glyph_name, COUNT(*) FROM glyph_usage_log GROUP BY glyph_name'):
        usage_counts[r[0]] = r[1]

    version_counts = {}
    for r in cur.execute('SELECT glyph_name, COUNT(*) FROM glyph_versions GROUP BY glyph_name'):
        version_counts[r[0]] = r[1]

    archived_set = set(r[0] for r in cur.execute(
        'SELECT glyph_name FROM glyph_lexicon_archived'))

    # normalized grouping
    norm_map = {}
    for id_, name, desc, dname in rows:
        norm = normalize_name(name or '')
        if not norm:
            continue
        norm_map.setdefault(norm, []).append((id_, name))

    # analyze each row
    os.makedirs('tools', exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=['id', 'glyph_name', 'name_len', 'desc_len', 'display_name_len', 'non_alnum_ratio',
                                'control_chars', 'high_unicode_chars', 'usage_count', 'versions_count', 'archived', 'norm_group_size', 'flags', 'sample_usage'])
        writer.writeheader()

        for id_, name, desc, dname in rows:
            name = name or ''
            desc = desc or ''
            dname = dname or ''
            name_len = len(name)
            desc_len = len(desc)
            display_name_len = len(dname)

            if name_len > 0:
                non_alnum = sum(1 for ch in name if not (
                    ch.isalnum() or ch.isspace()))
                non_alnum_ratio = non_alnum / name_len
                control_chars = sum(1 for ch in name if ord(
                    ch) < 32 and ch not in ('\n', '\r', '\t'))
                high_unicode = sum(1 for ch in name if ord(ch) > 127)
            else:
                non_alnum_ratio = 0.0
                control_chars = 0
                high_unicode = 0

            usage = usage_counts.get(name, 0)
            versions = version_counts.get(name, 0)
            archived = name in archived_set
            norm = normalize_name(name)
            norm_group_size = len(norm_map.get(norm, [])) if norm else 0

            flags = []
            if name_len > 120 or desc_len > 1000:
                flags.append('LONG_TEXT')
            if non_alnum_ratio > 0.3:
                flags.append('NON_ALNUM')
            if control_chars > 0:
                flags.append('CONTROL_CHARS')
            if high_unicode > 10:
                flags.append('HIGH_UNICODE')
            if usage == 0:
                flags.append('NO_USAGE')
            if versions > 10:
                flags.append('MANY_VERSIONS')
            if norm_group_size > 1:
                flags.append('NORM_DUP')

            # sample usage input_texts
            sample_texts = []
            if usage > 0:
                for r in cur.execute('SELECT input_text, matched_at FROM glyph_usage_log WHERE glyph_name=? ORDER BY matched_at DESC LIMIT 3', (name,)):
                    # avoid backslash in f-string expression by using % formatting
                    sample_texts.append("%s: %s" % (
                        r[1], (r[0] or '')[:200].replace('\n', ' ')))
            sample_field = ' | '.join(sample_texts)

            writer.writerow({
                'id': id_,
                'glyph_name': name,
                'name_len': name_len,
                'desc_len': desc_len,
                'display_name_len': display_name_len,
                'non_alnum_ratio': f"{non_alnum_ratio:.3f}",
                'control_chars': control_chars,
                'high_unicode_chars': high_unicode,
                'usage_count': usage,
                'versions_count': versions,
                'archived': archived,
                'norm_group_size': norm_group_size,
                'flags': ','.join(flags),
                'sample_usage': sample_field,
            })

    conn.close()
    print('Wrote', OUT)


if __name__ == '__main__':
    analyze()
