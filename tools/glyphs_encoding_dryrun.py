#!/usr/bin/env python3
"""
Dry-run encoding repair and noise detection for `glyph_lexicon`.

Produces:
 - `tools/glyphs_encoding_fix_report.csv` : per-row original vs fixed snippets and change metrics
 - `tools/glyphs_noise_flags.csv` : rows flagged as noisy (high nonprintable ratio or large changes)

This script does NOT modify the DB. It's safe to run repeatedly.
"""
import sqlite3
import os
import csv
import unicodedata
import re
from difflib import SequenceMatcher

DB = os.path.join('emotional_os', 'glyphs', 'glyphs.db')
OUT_REPORT = os.path.join('tools', 'glyphs_encoding_fix_report.csv')
OUT_FLAGS = os.path.join('tools', 'glyphs_noise_flags.csv')


def fix_encoding(text):
    if text is None:
        return ''
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return ''
    # common mojibake fix: latin1 bytes interpreted as utf-8
    try:
        candidate = text.encode('latin1').decode('utf-8')
    except Exception:
        candidate = text
    # normalize unicode
    candidate = unicodedata.normalize('NFKC', candidate)
    # strip control/non-printable (preserve common whitespace)
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+', '', candidate)
    # collapse weird repeated replacement characters
    cleaned = re.sub(r'[\ufffd]{2,}', '\ufffd', cleaned)
    # remove common emoji / pictograph ranges (e.g., 🌑, 🌀, 🧱, 📖)
    emoji_pattern = re.compile(
        '[\U0001F300-\U0001F6FF'  # symbols & pictographs
        '\U0001F900-\U0001F9FF'  # supplemental symbols & pictographs
        '\U0001F680-\U0001F6FF'  # transport & map
        '\u2600-\u26FF'          # miscellaneous symbols
        '\u2700-\u27BF]+', flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', cleaned)
    return cleaned


def nonprintable_ratio(s):
    if not s:
        return 0.0
    total = len(s)
    nonprintable = sum(1 for ch in s if ord(ch) < 32 and ch not in '\n\t\r')
    # also count uncommon control ranges
    nonprintable += sum(1 for ch in s if 0xFFFD == ord(ch))
    return nonprintable / total if total else 0.0


def changed_ratio(a, b):
    if a == b:
        return 0.0
    return 1.0 - SequenceMatcher(None, a, b).ratio()


def main():
    if not os.path.exists(DB):
        raise SystemExit('DB not found at ' + DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        'SELECT id, glyph_name, display_name, description, response_template FROM glyph_lexicon')
    rows = cur.fetchall()

    os.makedirs('tools', exist_ok=True)
    report_fh = open(OUT_REPORT, 'w', newline='', encoding='utf-8')
    flags_fh = open(OUT_FLAGS, 'w', newline='', encoding='utf-8')
    report_writer = csv.DictWriter(report_fh, fieldnames=['id',
                                                          'glyph_name_orig', 'glyph_name_fixed', 'glyph_name_change', 'glyph_name_change_ratio',
                                                          'display_name_orig', 'display_name_fixed', 'display_name_change', 'display_name_change_ratio',
                                                          'description_snip_orig', 'description_snip_fixed', 'description_change', 'description_change_ratio',
                                                          'response_template_orig', 'response_template_fixed', 'response_template_change', 'response_template_change_ratio',
                                                          'nonprintable_ratio', 'suggested_action'])
    flags_writer = csv.DictWriter(
        flags_fh, fieldnames=['id', 'issue', 'reason', 'metric', 'note'])
    report_writer.writeheader()
    flags_writer.writeheader()

    flagged = 0
    likely_fixed = 0

    for id_, gname, dname, desc, templ in rows:
        gname = gname or ''
        dname = dname or ''
        desc = desc or ''
        templ = templ or ''

        g_fixed = fix_encoding(gname)
        d_fixed = fix_encoding(dname)
        desc_fixed = fix_encoding(desc)
        t_fixed = fix_encoding(templ)

        g_ratio = changed_ratio(gname, g_fixed)
        d_ratio = changed_ratio(dname, d_fixed)
        desc_ratio = changed_ratio(desc[:300], desc_fixed[:300])
        t_ratio = changed_ratio(templ, t_fixed)

        np_ratio = max(nonprintable_ratio(gname), nonprintable_ratio(
            dname), nonprintable_ratio(desc), nonprintable_ratio(templ))

        # heuristic decisions
        change_any = any(x > 0.01 for x in (
            g_ratio, d_ratio, desc_ratio, t_ratio))
        suspect_nonprint = np_ratio > 0.30
        suggested = 'OK'
        if suspect_nonprint or change_any:
            if suspect_nonprint or max(g_ratio, d_ratio, desc_ratio, t_ratio) > 0.20:
                suggested = 'REVIEW'
            else:
                suggested = 'AUTO_FIX_POSSIBLE'

        if suggested != 'OK':
            flagged += 1
            flags_writer.writerow({'id': id_, 'issue': 'ENCODING/NOISE', 'reason': suggested,
                                  'metric': round(max(g_ratio, d_ratio, desc_ratio, t_ratio, np_ratio), 3), 'note': ''})

        if suggested == 'AUTO_FIX_POSSIBLE':
            likely_fixed += 1

        report_writer.writerow({
            'id': id_,
            'glyph_name_orig': gname,
            'glyph_name_fixed': g_fixed,
            'glyph_name_change': 'yes' if g_ratio > 0.01 else 'no',
            'glyph_name_change_ratio': round(g_ratio, 4),
            'display_name_orig': dname,
            'display_name_fixed': d_fixed,
            'display_name_change': 'yes' if d_ratio > 0.01 else 'no',
            'display_name_change_ratio': round(d_ratio, 4),
            'description_snip_orig': desc[:200].replace('\n', ' '),
            'description_snip_fixed': desc_fixed[:200].replace('\n', ' '),
            'description_change': 'yes' if desc_ratio > 0.01 else 'no',
            'description_change_ratio': round(desc_ratio, 4),
            'response_template_orig': templ[:200].replace('\n', ' '),
            'response_template_fixed': t_fixed[:200].replace('\n', ' '),
            'response_template_change': 'yes' if t_ratio > 0.01 else 'no',
            'response_template_change_ratio': round(t_ratio, 4),
            'nonprintable_ratio': round(np_ratio, 4),
            'suggested_action': suggested,
        })

    report_fh.close()
    flags_fh.close()

    print('Encoding dry-run complete')
    print('Report:', OUT_REPORT)
    print('Flags:', OUT_FLAGS)
    print('Totals: rows scanned:', len(rows), 'flagged:',
          flagged, 'likely_auto_fix:', likely_fixed)


if __name__ == '__main__':
    main()
