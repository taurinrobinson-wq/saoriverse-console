#!/usr/bin/env python3
"""
Archive strict prune candidates from `tools/glyphs_prune_strict.csv`.

Actions performed (dry-run = False will apply changes):
 - create a timestamped backup copy of the SQLite DB
 - ensure `glyph_lexicon_archived` exists (created from schema if needed)
 - for each remove id in the CSV, copy the full row into archived table and delete from glyph_lexicon
 - write `tools/glyphs_prune_strict_archive_report.csv` with details for each archived row

This script is intended to be conservative and reversible because the DB backup is created.
"""
import sqlite3
import os
import shutil
import csv
import datetime
import sys

BASE_DB = os.path.join('emotional_os', 'glyphs', 'glyphs.db')
CSV_IN = os.path.join('tools', 'glyphs_prune_strict.csv')
REPORT_OUT = os.path.join('tools', 'glyphs_prune_strict_archive_report.csv')


def backup_db(db_path):
    if not os.path.exists(db_path):
        raise SystemExit(f"DB not found at {db_path}")
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup_path = db_path + f'.bak.{ts}'
    shutil.copy2(db_path, backup_path)
    print('Created DB backup:', backup_path)
    return backup_path


def ensure_archived_table(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='glyph_lexicon_archived'")
    if not cur.fetchone():
        print('Creating `glyph_lexicon_archived` table with explicit schema...')
        cur.execute('''
            CREATE TABLE glyph_lexicon_archived (
                id INTEGER,
                voltage_pair TEXT,
                glyph_name TEXT,
                description TEXT,
                gate TEXT,
                activation_signals TEXT,
                display_name TEXT,
                response_template TEXT,
                archived_at TEXT
            )
        ''')
        conn.commit()
        return

    cols = [c[1]
            for c in cur.execute("PRAGMA table_info('glyph_lexicon_archived')")]
    if 'id' not in cols:
        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        old_name = f'glyph_lexicon_archived_old_{ts}'
        print(
            f'Existing `glyph_lexicon_archived` has unexpected schema; renaming to {old_name} and creating proper table')
        cur.execute(f'ALTER TABLE glyph_lexicon_archived RENAME TO {old_name}')
        cur.execute('''
            CREATE TABLE glyph_lexicon_archived (
                id INTEGER,
                voltage_pair TEXT,
                glyph_name TEXT,
                description TEXT,
                gate TEXT,
                activation_signals TEXT,
                display_name TEXT,
                response_template TEXT,
                archived_at TEXT
            )
        ''')
        conn.commit()


def parse_csv_candidates(path):
    if not os.path.exists(path):
        raise SystemExit(f'CSV not found at {path}')
    groups = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            remove_ids = [int(x) for x in r.get(
                'remove_ids', '').split(',') if x.strip()]
            groups.append({'norm': r.get('norm'), 'keep': int(r.get(
                'keep') or 0), 'remove_ids': remove_ids, 'count': int(r.get('count') or 0)})
    return groups


def archive_rows(conn, groups):
    cur = conn.cursor()
    report_rows = []
    ts = datetime.datetime.utcnow().isoformat() + 'Z'
    total_archived = 0
    for g in groups:
        norm = g['norm']
        keep = g['keep']
        for rid in g['remove_ids']:
            cur.execute('SELECT * FROM glyph_lexicon WHERE id = ?', (rid,))
            row = cur.fetchone()
            if not row:
                print(f'WARN: id {rid} not found; skipping')
                continue
            # column names
            col_info = list(cur.execute("PRAGMA table_info('glyph_lexicon')"))
            col_names = [c[1] for c in col_info]
            # build insert into archived table
            placeholders = ','.join(['?'] * len(row))
            insert_sql = f"INSERT INTO glyph_lexicon_archived ({', '.join(col_names)}, archived_at) VALUES ({placeholders}, ?)"
            try:
                cur.execute(insert_sql, tuple(row) + (ts,))
            except sqlite3.IntegrityError:
                print(
                    f'WARN: Could not insert id {rid} into archived (possible duplicate)')
            # delete original
            cur.execute('DELETE FROM glyph_lexicon WHERE id = ?', (rid,))
            total_archived += 1
            # collect report row: include id plus some common fields if available
            try:
                glyph_name = row[col_names.index(
                    'glyph_name')] if 'glyph_name' in col_names else ''
            except Exception:
                glyph_name = ''
            try:
                display_name = row[col_names.index(
                    'display_name')] if 'display_name' in col_names else ''
            except Exception:
                display_name = ''
            try:
                response_template = row[col_names.index(
                    'response_template')] if 'response_template' in col_names else ''
            except Exception:
                response_template = ''
            report_rows.append({'id': rid, 'norm': norm, 'keep': keep, 'glyph_name': glyph_name,
                               'display_name': display_name, 'response_template': response_template, 'archived_at': ts})
    conn.commit()
    print(f'Archived {total_archived} rows into `glyph_lexicon_archived`.')
    return report_rows


def write_report(path, rows):
    if not rows:
        print('No rows archived; skipping report generation.')
        return
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=[
                                'id', 'norm', 'keep', 'glyph_name', 'display_name', 'response_template', 'archived_at'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print('Wrote archive report:', path)


def main():
    print('Starting strict-prune archival...')
    backup_db(BASE_DB)
    groups = parse_csv_candidates(CSV_IN)
    if not groups:
        print('No candidate groups found in CSV; exiting.')
        return
    conn = sqlite3.connect(BASE_DB)
    ensure_archived_table(conn)
    report_rows = archive_rows(conn, groups)
    write_report(REPORT_OUT, report_rows)
    conn.close()
    print('Done.')


if __name__ == '__main__':
    main()
