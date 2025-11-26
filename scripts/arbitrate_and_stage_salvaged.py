#!/usr/bin/env python3
"""Resolve gate conflicts using heuristic arbitration and stage salvaged glyphs into a testing table.

Writes:
- archive/glyph_exports/flags/gate_conflict_resolution.csv
- updates archive/salvaged_glyphs.jsonl and archive/salvaged_glyphs.db (gate field and notes)
- creates table glyph_lexicon_salvaged in archive/salvaged_glyphs.db and inserts all canonical records

Prints a brief summary and sample rows.
"""
import json
import os
import re
import sqlite3
import csv
from collections import defaultdict


FLAGGED_JSONL = 'archive/glyph_exports/flags/flagged_groups.jsonl'
FLAGGED_CSV = 'archive/glyph_exports/flags/gate_conflict_resolution.csv'
SALVAGED_JSONL = 'archive/salvaged_glyphs.jsonl'
SALVAGED_DB = 'archive/salvaged_glyphs.db'
STAGED_TABLE = 'glyph_lexicon_salvaged'


def extract_chunk_start(fname):
    # expects filenames like candidates_6001_6370.jsonl
    m = re.search(r'_(\d+)_', fname)
    if m:
        return int(m.group(1))
    m2 = re.search(r'_(\d+)\.jsonl$', fname)
    if m2:
        return int(m2.group(1))
    return 0


def load_flagged():
    groups = []
    if not os.path.exists(FLAGGED_JSONL):
        raise SystemExit('Missing flagged groups file: ' + FLAGGED_JSONL)
    with open(FLAGGED_JSONL, 'r', encoding='utf-8') as f:
        for line in f:
            groups.append(json.loads(line))
    return groups


def load_salvaged_index():
    idx = {}
    if not os.path.exists(SALVAGED_JSONL):
        raise SystemExit('Missing salvaged JSONL: ' + SALVAGED_JSONL)
    with open(SALVAGED_JSONL, 'r', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            idx[int(r.get('group_id'))] = r
    return idx


def decide_gate_for_group(group):
    # group contains 'group_id' and 'members' list
    gid = group.get('group_id')
    members = group.get('members') or []
    gates = [(m.get('gate') or '').strip()
             for m in members if (m.get('gate') or '').strip()]
    gates_set = set(gates)
    if len(gates_set) == 1:
        return gates[0], 1.0, 'unanimous'

    # aggregate emotional tags across members
    emos = set()
    combined_text = []
    for m in members:
        for t in (m.get('emotional_tags') or []):
            emos.add(t)
        combined_text.append((m.get('description') or '') + ' ' +
                             (m.get('title') or '') + ' ' + (m.get('glyph_name') or ''))
    text = ' '.join(combined_text).lower()

    # Rule: emotional tag biasing
    if 'grief' in emos:
        return 'Gate 7', 0.9, 'emotion bias: grief'
    if 'longing' in emos:
        # prefer Gate 3 unless content suggests Gate 8
        if re.search(r'transform|healing|integration', text):
            return 'Gate 8', 0.9, 'emotion bias: longing + content suggests Gate 8'
        return 'Gate 3', 0.9, 'emotion bias: longing'

    # Content-based inference
    if re.search(r'collapse|loss|grief|collapsed', text):
        return 'Gate 7', 0.9, 'content inference: collapse/loss/grief'
    if re.search(r'transform|healing|integration|repair|rebuild', text):
        return 'Gate 8', 0.9, 'content inference: transform/healing/integration'

    # Fallback: choose gate from best record per priority
    # Score each member by (confidence, len(description), has_activation, recency)
    best = None
    best_score = None
    for m in members:
        conf = float(m.get('confidence') or 0.0)
        desc_len = len((m.get('description') or ''))
        has_act = 1 if m.get('activation_signals') else 0
        # recency from source file
        sf = m.get('_source_file') or ''
        recency = extract_chunk_start(sf)
        score = (conf, desc_len, has_act, recency)
        if best is None or score > best_score:
            best = m
            best_score = score

    if best and (best.get('gate') or '').strip():
        rationale = f"fallback chosen from record {best.get('source_rowid')} by score"
        return best.get('gate'), float(best.get('confidence') or 0.0), rationale

    # If nothing else, choose Gate 7 as conservative default
    return 'Gate 7', 0.5, 'default fallback Gate 7'


def update_salvaged_jsonl(salvaged_idx):
    # overwritten file: write all records from salvaged_idx (dict of group_id->rec)
    path = SALVAGED_JSONL
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        for gid in sorted(salvaged_idx.keys()):
            f.write(json.dumps(salvaged_idx[gid], ensure_ascii=False) + '\n')
    os.replace(tmp, path)


def update_salvaged_db(salvaged_idx):
    if not os.path.exists(SALVAGED_DB):
        raise SystemExit('Missing DB: ' + SALVAGED_DB)
    conn = sqlite3.connect(SALVAGED_DB)
    cur = conn.cursor()
    # Update gate and notes fields for each updated record
    for gid, rec in salvaged_idx.items():
        cur.execute('UPDATE salvaged_glyphs SET gate=?, notes=?, confidence=? WHERE group_id=?', (
            rec.get('gate'), rec.get('notes'), rec.get('confidence'), gid
        ))
    conn.commit()
    conn.close()


def create_stage_table_and_insert():
    conn = sqlite3.connect(SALVAGED_DB)
    cur = conn.cursor()
    # drop existing staged table if present
    cur.execute(f"DROP TABLE IF EXISTS {STAGED_TABLE}")
    cur.execute('''CREATE TABLE glyph_lexicon_salvaged (
        group_id INTEGER,
        source_rowids TEXT,
        glyph_name TEXT,
        title TEXT,
        description TEXT,
        gate TEXT,
        emotional_tags TEXT,
        activation_signals TEXT,
        confidence REAL,
        notes TEXT
    )''')
    # read all records from salvaged_glyphs table
    cur.execute('SELECT group_id, source_rowids, glyph_name, title, description, gate, emotional_tags, activation_signals, confidence, notes FROM salvaged_glyphs')
    rows = cur.fetchall()
    for r in rows:
        cur.execute(
            f'INSERT INTO {STAGED_TABLE} (group_id, source_rowids, glyph_name, title, description, gate, emotional_tags, activation_signals, confidence, notes) VALUES (?,?,?,?,?,?,?,?,?,?)', r)
    conn.commit()
    # count rows
    cur.execute(f'SELECT COUNT(*) FROM {STAGED_TABLE}')
    count = cur.fetchone()[0]
    conn.close()
    return count


def main():
    flagged = load_flagged()
    salvaged_idx = load_salvaged_index()

    resolutions = []
    resolved_count = 0
    unresolved = []

    for g in flagged:
        gid = int(g.get('group_id'))
        resolved_gate, conf, rationale = decide_gate_for_group(g)
        resolutions.append({'group_id': gid, 'resolved_gate': resolved_gate,
                           'confidence': conf, 'rationale': rationale})
        # update salvaged record
        if gid in salvaged_idx:
            rec = salvaged_idx[gid]
            rec['gate'] = resolved_gate
            # append note
            note = rec.get('notes') or ''
            if note:
                note = note + '; Gate resolved from conflict using heuristic arbitration.'
            else:
                note = 'Gate resolved from conflict using heuristic arbitration.'
            rec['notes'] = note
            # update confidence to max(rec.confidence, conf)
            try:
                rec_conf = float(rec.get('confidence') or 0.0)
            except Exception:
                rec_conf = 0.0
            rec['confidence'] = round(max(rec_conf, float(conf or 0.0)), 2)
            salvaged_idx[gid] = rec
            resolved_count += 1
        else:
            unresolved.append(gid)

    # write resolutions CSV
    os.makedirs(os.path.dirname(FLAGGED_CSV), exist_ok=True)
    with open(FLAGGED_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['group_id', 'resolved_gate', 'confidence', 'rationale'])
        writer.writeheader()
        for r in resolutions:
            writer.writerow(r)

    # update salvaged jsonl and db
    update_salvaged_jsonl(salvaged_idx,)
    update_salvaged_db(salvaged_idx)

    # create staged table and insert
    staged_count = create_stage_table_and_insert()

    # summary
    print('Gate conflicts resolved (requested):', len(flagged))
    print('Resolved and updated salvaged records:', resolved_count)
    print('Unresolved group ids (not found in salvaged index):', unresolved)
    print('Staged records into table:', staged_count)

    # show 5 sample rows
    conn = sqlite3.connect(SALVAGED_DB)
    cur = conn.cursor()
    cur.execute(
        f'SELECT group_id, glyph_name, gate, emotional_tags, confidence FROM {STAGED_TABLE} ORDER BY group_id LIMIT 5')
    for row in cur.fetchall():
        print(row)
    conn.close()


if __name__ == '__main__':
    main()
