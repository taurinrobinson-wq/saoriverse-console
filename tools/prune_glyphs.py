#!/usr/bin/env python3
"""
Prune duplicate / noisy glyphs by normalized name.

Usage:
  python3 tools/prune_glyphs.py --dry-run
  python3 tools/prune_glyphs.py --apply  # destructive: archives rows

Behavior:
 - For each normalized name group with more than 1 member, choose a "keep" id:
   * Prefer row with non-empty response_template
   * else prefer row with highest versions_count
   * else prefer lowest id
 - All other rows in the group are proposed for archival (moved to glyph_lexicon_archived)

The script writes a CSV `tools/glyphs_prune_report.csv` with proposed actions. With `--apply` it will perform the archive (copy to archived table and delete from glyph_lexicon) after creating a SQL dump backup `tools/glyphs_prune_backup.sql`.

Note: This is destructive when --apply is used. Review the CSV first.
"""
import sqlite3
import os
import csv
import argparse
import re
import unicodedata

DB = os.path.join('emotional_os', 'glyphs', 'glyphs.db')
REPORT = os.path.join('tools', 'glyphs_prune_report.csv')
BACKUP_SQL = os.path.join('tools', 'glyphs_prune_backup.sql')


def normalize(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKD', s)
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def gather(conn):
    cur = conn.cursor()
    cur.execute(
        'SELECT id,glyph_name,display_name,description FROM glyph_lexicon')
    rows = cur.fetchall()
    groups = {}
    for id_, name, dname, desc in rows:
        norm = normalize(name or dname)
        groups.setdefault(norm, []).append(
            {'id': id_, 'name': name or '', 'display_name': dname or ''})
    return groups


def choose_keep(conn, members):
    # members: list of dicts with id,name,display_name
    cur = conn.cursor()
    best = None
    best_score = None
    for m in members:
        mid = m['id']
        # check response_template presence
        cur.execute(
            'SELECT response_template FROM glyph_lexicon WHERE id=?', (mid,))
        row = cur.fetchone()
        has_template = bool(row and row[0] and row[0].strip())
        # versions_count
        cur.execute(
            'SELECT COUNT(*) FROM glyph_versions WHERE glyph_name=(SELECT glyph_name FROM glyph_lexicon WHERE id=?)', (mid,))
        versions = cur.fetchone()[0]
        # compute score tuple: prefer template (1/0), versions, negative id (to prefer low id)
        score = (1 if has_template else 0, versions, -mid)
        if best is None or score > best_score:
            best = mid
            best_score = score
    return best


def dry_run(conn, groups, limit=50):
    actions = []
    for norm, members in groups.items():
        if not norm or len(members) <= 1:
            continue
        # choose keep
        keep = choose_keep(conn, members)
        for m in members:
            if m['id'] == keep:
                continue
            actions.append({'norm': norm, 'keep': keep,
                           'remove_id': m['id'], 'remove_name': m['name']})
    # write report
    os.makedirs('tools', exist_ok=True)
    with open(REPORT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['norm', 'keep', 'remove_id', 'remove_name'])
        writer.writeheader()
        for a in actions:
            writer.writerow(a)
    return actions


def dump_backup(conn, remove_ids):
    # create SQL INSERT statements for rows we will remove (copy to archived table)
    cur = conn.cursor()
    with open(BACKUP_SQL, 'w', encoding='utf-8') as fh:
        for rid in remove_ids:
            cur.execute('SELECT * FROM glyph_lexicon WHERE id=?', (rid,))
            row = cur.fetchone()
            if not row:
                continue
            # build INSERT INTO glyph_lexicon_archived (...) VALUES (...);
            colinfo = cur.execute(
                "PRAGMA table_info('glyph_lexicon')").fetchall()
            cols = [c[1] for c in colinfo]
            # serialize values safely
            vals = []
            for v in row:
                if v is None:
                    vals.append('NULL')
                else:
                    vals.append("'" + str(v).replace("'", "''") + "'")
            fh.write(
                f"INSERT INTO glyph_lexicon_archived ({','.join(cols)}) VALUES ({','.join(vals)});\n")
    return BACKUP_SQL


def apply_changes(conn, actions):
    cur = conn.cursor()
    remove_ids = [a['remove_id'] for a in actions]
    # backup SQL
    dump_backup(conn, remove_ids)
    # perform archival: copy rows and delete
    for rid in remove_ids:
        # copy to archived
        cur.execute('SELECT * FROM glyph_lexicon WHERE id=?', (rid,))
        row = cur.fetchone()
        if not row:
            continue
        colinfo = cur.execute("PRAGMA table_info('glyph_lexicon')").fetchall()
        cols = [c[1] for c in colinfo]
        placeholders = ','.join('?' for _ in cols)
        cur.execute(
            f"INSERT INTO glyph_lexicon_archived ({','.join(cols)}) VALUES ({placeholders})", row)
        cur.execute('DELETE FROM glyph_lexicon WHERE id=?', (rid,))
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                        help='Do not modify DB; just create report')
    parser.add_argument('--apply', action='store_true',
                        help='Apply changes (destructive)')
    args = parser.parse_args()

    if not os.path.exists(DB):
        print('DB not found at', DB)
        return
    conn = sqlite3.connect(DB)
    groups = gather(conn)
    actions = dry_run(conn, groups)
    print(
        f'Proposed actions: {len(actions)} rows to archive. Report at {REPORT}')

    # show sample
    for a in actions[:30]:
        print(a)

    if args.apply:
        confirm = input(
            'This will archive rows and delete them from glyph_lexicon. Type YES to proceed:')
        if confirm == 'YES':
            apply_changes(conn, actions)
            print('Applied changes. Backup SQL at', BACKUP_SQL)
        else:
            print('Aborted')
    conn.close()


if __name__ == '__main__':
    main()
