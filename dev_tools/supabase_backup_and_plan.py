#!/usr/bin/env python3
"""
Fetch a full table backup from Supabase (PostgREST) and prepare a safe upsert plan

Usage (dry-run, no write):
  SUPABASE_URL=https://xyz.supabase.co SUPABASE_KEY=<service-role> \
    python3 dev_tools/supabase_backup_and_plan.py --table glyphs

This script requires the environment variables SUPABASE_URL and SUPABASE_KEY
or the equivalent CLI options. It will:
 - download all rows from the specified table into a timestamped JSON/CSV backup
 - compare the backup with a local cleaned export (dev_tools/cleaned_glyphs.json by default)
 - produce a staged upsert plan (JSON + per-action CSVs) in dev_tools/

By default it runs in dry-run mode (no writes to Supabase). See README comment
in dev_tools/supabase_upsert_plan.md for safety instructions.
"""

from __future__ import annotations
import argparse
import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple

import requests

DEFAULT_OUT_DIR = "dev_tools"
PAGE_SIZE = 1000


def iso_ts() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def fetch_all_rows(supabase_url: str, supabase_key: str, table: str) -> List[Dict[str, Any]]:
    base = supabase_url.rstrip('/') + f"/rest/v1/{table}"
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Accept': 'application/json'
    }

    rows: List[Dict[str, Any]] = []
    start = 0
    while True:
        end = start + PAGE_SIZE - 1
        r = requests.get(base, headers={
                         **headers, 'Range': f'items={start}-{end}'}, params={'select': '*'})
        if r.status_code not in (200, 206):
            raise RuntimeError(
                f"Failed to fetch rows: {r.status_code} {r.text}")
        page = r.json()
        if not page:
            break
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        start += PAGE_SIZE

    return rows


def save_json(out_path: str, data: Any) -> None:
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(out_path: str, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('')
        return
    keys = sorted({k for r in rows for k in r.keys()})
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        for r in rows:
            def cell(v):
                if isinstance(v, (dict, list)):
                    return json.dumps(v, ensure_ascii=False)
                return v
            w.writerow({k: cell(r.get(k, None)) for k in keys})


def load_local_cleaned(cleaned_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(cleaned_path):
        print(f"Local cleaned file not found: {cleaned_path}")
        return []
    with open(cleaned_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_upsert_plan(backup: List[Dict[str, Any]], cleaned: List[Dict[str, Any]], key: str) -> Dict[str, Any]:
    """Compare backup to cleaned rows and produce insert/update/identical lists.

    key: the canonical key to match rows (e.g., 'slug')
    """
    by_key_backup = {
        str(r.get(key)): r for r in backup if key in r and r.get(key) is not None}
    by_key_cleaned = {
        str(r.get(key)): r for r in cleaned if key in r and r.get(key) is not None}

    inserts = []
    updates = []
    identical = []

    for k, cleaned_row in by_key_cleaned.items():
        if k not in by_key_backup:
            inserts.append(cleaned_row)
        else:
            old = by_key_backup[k]
            if rows_equal(old, cleaned_row):
                identical.append(cleaned_row)
            else:
                updates.append({'key': k, 'old': old, 'new': cleaned_row})

    deletions = [r for k, r in by_key_backup.items()
                 if k not in by_key_cleaned]

    return {'inserts': inserts, 'updates': updates, 'identical': identical, 'deletions': deletions}


def rows_equal(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    if set(a.keys()) != set(b.keys()):
        return False
    for k in a.keys():
        if a[k] == b[k]:
            continue
        try:
            if json.dumps(a[k], sort_keys=True, ensure_ascii=False) == json.dumps(b[k], sort_keys=True, ensure_ascii=False):
                continue
        except Exception:
            pass
        return False
    return True


def write_plan_files(out_dir: str, plan: Dict[str, Any], ts: str) -> Tuple[str, str, str]:
    base = os.path.join(out_dir, f"supabase_upsert_plan_{ts}")
    json_path = base + ".json"
    inserts_csv = base + "_inserts.csv"
    updates_csv = base + "_updates.csv"

    os.makedirs(out_dir, exist_ok=True)
    save_json(json_path, plan)

    save_csv(inserts_csv, plan.get('inserts', []))
    updates_new = [it['new'] for it in plan.get('updates', [])]
    save_csv(updates_csv, updates_new)

    return json_path, inserts_csv, updates_csv


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--supabase-url',
                   help='Supabase URL (overrides SUPABASE_URL env)')
    p.add_argument(
        '--supabase-key', help='Supabase Service Role key (overrides SUPABASE_KEY env)')
    p.add_argument('--table', default='glyphs', help='Table name to backup')
    p.add_argument('--out-dir', default=DEFAULT_OUT_DIR)
    p.add_argument(
        '--cleaned', default=os.path.join(DEFAULT_OUT_DIR, 'cleaned_glyphs.json'))
    p.add_argument('--key', default='slug',
                   help='Canonical key to match rows for upsert (default: slug)')
    p.add_argument('--no-backup', action='store_true',
                   help='Skip remote fetch; only build plan from local cleaned file')
    return p.parse_args()


def main():
    args = parse_args()
    supabase_url = args.supabase_url or os.environ.get('SUPABASE_URL')
    supabase_key = args.supabase_key or os.environ.get(
        'SUPABASE_KEY') or os.environ.get('SERVICE_ROLE_KEY')

    ts = iso_ts()
    out_dir = args.out_dir

    if args.no_backup:
        print("Skipping remote backup (--no-backup). Loading local cleaned file only.")
        backup_rows: List[Dict[str, Any]] = []
    else:
        if not supabase_url or not supabase_key:
            print("SUPABASE_URL and SUPABASE_KEY are required to fetch a live backup.\n"
                  "If you prefer to only stage a plan from local data, re-run with --no-backup.")
            sys.exit(1)
        print(
            f"Fetching table '{args.table}' from Supabase at {supabase_url}...")
        backup_rows = fetch_all_rows(supabase_url, supabase_key, args.table)
        backup_json = os.path.join(out_dir, f"supabase_backup_{ts}.json")
        backup_csv = os.path.join(out_dir, f"supabase_backup_{ts}.csv")
        os.makedirs(out_dir, exist_ok=True)
        save_json(backup_json, backup_rows)
        save_csv(backup_csv, backup_rows)
        print(
            f"Wrote backup: {backup_json} and {backup_csv} ({len(backup_rows)} rows)")

    cleaned = load_local_cleaned(args.cleaned)
    print(f"Loaded local cleaned input: {args.cleaned} ({len(cleaned)} rows)")

    plan = build_upsert_plan(backup_rows, cleaned, args.key)
    plan_json, inserts_csv, updates_csv = write_plan_files(out_dir, plan, ts)

    summary = (
        f"Upsert plan written:\n  plan: {plan_json}\n  inserts CSV: {inserts_csv} ({len(plan.get('inserts', []))})\n"
        f"  updates CSV: {updates_csv} ({len(plan.get('updates', []))})\n  identical: {len(plan.get('identical', []))}\n"
        f"  deletions (present in remote, not in cleaned): {len(plan.get('deletions', []))}\n"
    )
    print(summary)
    print("Next: review these files, verify the plan, then run dev_tools/supabase_upsert_runner.py --apply with credentials to perform the upsert in safe batches.")


if __name__ == '__main__':
    main()
