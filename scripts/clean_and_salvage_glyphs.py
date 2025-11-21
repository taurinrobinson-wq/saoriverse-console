#!/usr/bin/env python3
"""Clean and salvage glyph candidates from exported CSV chunk.

Usage: python3 scripts/clean_and_salvage_glyphs.py <csv-path> [out-jsonl-path]

Outputs a JSONL file of cleaned records and prints a brief summary and samples.
"""
import csv
import json
import os
import re
import sys
from difflib import SequenceMatcher


DEFAULT_IN = 'archive/glyph_exports/candidates_1_1000.csv'
OUT_DIR = 'archive/glyph_exports/cleaned'


def load_fallback_lexicon():
    path = 'emotional_os/parser/runtime_fallback_lexicon.json'
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def strip_export_artifacts(text):
    if not text:
        return ''
    s = text
    # Remove common export markers and headers
    patterns = [r'CORE PRINCIPLES:.*', r'TITLE:\s*', r'📅.*',
                r'JSON Export.*', r'\bVELΩNIX\b', r'— JSON Export.*']
    for p in patterns:
        s = re.sub(p, '', s, flags=re.IGNORECASE | re.DOTALL)

    # Remove HTML blocks
    s = re.sub(r'<[^>]+>', '', s)

    # Remove fenced code blocks
    s = re.sub(r'```[\s\S]*?```', '', s)

    # Remove lines that look like export meta or long marker lines
    lines = []
    for line in s.splitlines():
        if re.search(r'EXPORT|EXPORTED|MARKDOWN EXPORT|JSON EXPORT|CONVERSATION ARCHIVE|TITLE:', line, flags=re.IGNORECASE):
            continue
        if line.strip().startswith('—') or line.strip().startswith('---'):
            continue
        lines.append(line)
    s = '\n'.join(lines)

    # Normalize whitespace
    s = re.sub(r'\r\n?', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    s = s.strip()
    return s


def extract_title(description, glyph_name):
    if not description:
        return glyph_name or ''
    # TITLE: marker
    m = re.search(r'TITLE:\s*(.+)', description, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # first markdown H1/H2
    for line in description.splitlines():
        line = line.strip()
        if line.startswith('#'):
            return line.lstrip('#').strip()
        if len(line) > 0:
            # first non-empty short line could be title candidate but prefer headings
            break
    return glyph_name or ''


def infer_gate_and_emotions(glyph_name, description, fallback):
    text = ' '.join([glyph_name or '', description or '']).lower()
    gate = None
    emotions = []
    confidence = 0.0

    # If gate token present like 'gate:' in description, try to capture
    gm = re.search(r'gate[:\s]+([A-Za-z0-9_\-]+)',
                   description or '', flags=re.IGNORECASE)
    if gm:
        gate = gm.group(1).strip()
        confidence = max(confidence, 0.9)

    # Keyword matching using fallback lexicon
    matches = []
    for k, v in fallback.items():
        if k in text:
            tone = v.get('tone')
            if tone and tone not in emotions:
                emotions.append(tone)
            matches.append(k)

    if matches:
        confidence = max(confidence, 0.75 if gate is None else 0.9)

    # Simple heuristic: if description contains 'ritual' or 'archive', set gate=ritual/archive
    if not gate:
        if re.search(r'\barchive\b', text):
            gate = 'archive'
            confidence = max(confidence, 0.6)
        elif re.search(r'\britual\b', text):
            gate = 'ritual'
            confidence = max(confidence, 0.65)

    # fallback empty emotions -> []
    if not emotions:
        emotions = []

    return gate, emotions, confidence, matches


def canonicalize_name(name):
    if not name:
        return ''
    n = name.strip()
    n = re.sub(r'\s+', ' ', n)
    return n


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def process_csv(inpath, outpath, fallback):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    records = []
    with open(inpath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Columns: rowid, id, voltage_pair, glyph_name, description, gate, activation_signals, display_name, response_template
            src_rowid = int(row.get('rowid') or 0)
            glyph_name = canonicalize_name(
                row.get('glyph_name') or row.get('display_name') or '')
            raw_desc = row.get('description') or ''
            desc_clean = strip_export_artifacts(raw_desc)
            title = extract_title(desc_clean, glyph_name)
            gate_orig = (row.get('gate') or '').strip() or None
            activation_signals = row.get('activation_signals') or None

            gate_inferred = gate_orig
            emotions = []
            confidence = 1.0 if gate_orig else 0.0
            matches = []
            if not gate_orig or True:
                g, emos, conf, mats = infer_gate_and_emotions(
                    glyph_name, desc_clean, fallback)
                matches = mats
                if not gate_orig and g:
                    gate_inferred = g
                # merge emotions
                emotions = emos
                confidence = max(confidence, conf)

            rec = {
                'source_rowid': src_rowid,
                'glyph_name': glyph_name,
                'title': title,
                'description': desc_clean,
                'gate': gate_inferred,
                'emotional_tags': emotions,
                'activation_signals': activation_signals,
                'confidence': round(float(confidence), 2),
                'notes': ''
            }

            # notes: if matches found or artifact markers removed
            notes = []
            if matches:
                notes.append('matched lexicon:' + ','.join(matches[:5]))
            if raw_desc and raw_desc != desc_clean:
                notes.append('cleaned description')
            if not glyph_name:
                notes.append('missing glyph_name')
            rec['notes'] = '; '.join(notes)

            records.append(rec)

    # simple per-chunk dedupe: exact glyph_name dedupe, pick one with higher confidence/longer description
    grouped = {}
    for r in records:
        key = (r['glyph_name'] or '').lower()
        if not key:
            key = f"<empty>-{r['source_rowid']}"
        if key not in grouped:
            grouped[key] = [r]
        else:
            grouped[key].append(r)

    cleaned = []
    flagged = []
    for name, items in grouped.items():
        if len(items) == 1:
            cleaned.append(items[0])
            continue
        # choose canonical: highest confidence, then longer description
        items_sorted = sorted(items, key=lambda x: (
            x.get('confidence', 0), len(x.get('description') or '')), reverse=True)
        canonical = items_sorted[0]
        cleaned.append(canonical)
        # flag near-duplicates
        for other in items_sorted[1:]:
            sim = similar(canonical.get('description', '')[
                          :200], other.get('description', '')[:200])
            if sim > 0.86:
                # likely duplicate; skip but note
                canonical['notes'] = (canonical.get(
                    'notes') or '') + f'; dedup:{other["source_rowid"]}'
            else:
                flagged.append((canonical, other, sim))

    # write JSONL
    with open(outpath, 'w', encoding='utf-8') as outf:
        for r in cleaned:
            outf.write(json.dumps(r, ensure_ascii=False) + '\n')

    # return summary
    return {
        'in_count': len(records),
        'out_count': len(cleaned),
        'flagged_near_duplicates': len(flagged),
        'samples': cleaned[:10]
    }


def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IN
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        OUT_DIR, os.path.basename(inp).replace('.csv', '.jsonl'))
    fallback = load_fallback_lexicon()
    print('Using fallback lexicon entries:', len(fallback))
    print('Processing', inp, '->', out)
    summary = process_csv(inp, out, fallback)
    print('Processed:', summary['in_count'], '->',
          summary['out_count'], 'cleaned records')
    print('Flagged near-duplicates:', summary['flagged_near_duplicates'])
    print('\nSample cleaned records (up to 10):')
    for s in summary['samples']:
        print('-', s['source_rowid'], s['glyph_name'], 'gate=', s['gate'],
              'tags=', s['emotional_tags'], 'conf=', s['confidence'])


if __name__ == '__main__':
    main()
