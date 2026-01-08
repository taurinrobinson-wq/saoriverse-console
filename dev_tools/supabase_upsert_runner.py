#!/usr/bin/env python3
"""
Safe runner to apply an upsert plan to Supabase in batches.

This script is intentionally conservative. By default it performs a dry-run
and prints what would be sent. To actually apply the upsert, supply:

  SUPABASE_URL and SUPABASE_KEY (service role) as env vars or via --supabase-url/--supabase-key
  --apply flag to perform network writes

It POSTs batches to the Supabase REST endpoint with on_conflict set to the
canonical key (e.g., slug) and Prefer: resolution=merge-duplicates.

See dev_tools/supabase_upsert_plan.md for full safety instructions.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List

import requests

DEFAULT_OUT_DIR = "dev_tools"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", help="Path to supabase_upsert_plan_*.json", default=None)
    p.add_argument("--inserts-csv", help="CSV of records to insert", default=None)
    p.add_argument("--updates-csv", help="CSV of records to update (new values)", default=None)
    p.add_argument("--supabase-url", help="Supabase URL (overrides ENV)")
    p.add_argument("--supabase-key", help="Supabase service role key (overrides ENV)")
    p.add_argument("--table", default="glyphs")
    p.add_argument("--on-conflict", default="slug", help="on_conflict key (default: slug)")
    p.add_argument("--batch-size", type=int, default=200, help="Records per HTTP batch")
    p.add_argument("--apply", action="store_true", help="Actually perform network POSTs (default: dry-run)")
    return p.parse_args()


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv_as_json(path: str) -> List[Dict[str, Any]]:
    import csv

    rows = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            # try to parse JSON fields when applicable
            parsed = {}
            for k, v in row.items():
                if v is None:
                    parsed[k] = None
                    continue
                v = v.strip()
                if not v:
                    parsed[k] = None
                    continue
                # heuristics: if starts with { or [, try json.loads
                if v.startswith("{") or v.startswith("["):
                    try:
                        parsed[k] = json.loads(v)
                        continue
                    except Exception:
                        pass
                parsed[k] = v
            rows.append(parsed)
    return rows


def post_batch(supabase_url: str, supabase_key: str, table: str, on_conflict: str, batch: List[Dict[str, Any]]):
    url = supabase_url.rstrip("/") + f"/rest/v1/{table}?on_conflict={on_conflict}"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    r = requests.post(url, headers=headers, data=json.dumps(batch))
    return r


def apply_batches(
    url: str, key: str, table: str, on_conflict: str, rows: List[Dict[str, Any]], batch_size: int, do_apply: bool
):
    total = len(rows)
    print(f"Preparing to {'apply' if do_apply else 'dry-run'} {total} rows to {table} in batches of {batch_size}")
    i = 0
    success_count = 0
    errors = []
    while i < total:
        batch = rows[i : i + batch_size]
        print(f"Batch {i//batch_size + 1}: {len(batch)} rows")
        if do_apply:
            r = post_batch(url, key, table, on_conflict, batch)
            if r.status_code in (200, 201, 204):
                success_count += len(batch)
            else:
                errors.append({"status": r.status_code, "text": r.text})
                print(f"Batch failed: {r.status_code} {r.text}")
                # conservative: stop on first failure
                break
            # small delay to avoid hammering
            time.sleep(0.2)
        else:
            # dry-run: show sample of rows
            print(json.dumps(batch[:3], indent=2, ensure_ascii=False))
        i += batch_size

    return {"success": success_count, "errors": errors}


def main():
    args = parse_args()
    supabase_url = args.supabase_url or os.environ.get("SUPABASE_URL")
    supabase_key = args.supabase_key or os.environ.get("SUPABASE_KEY") or os.environ.get("SERVICE_ROLE_KEY")

    if args.apply and (not supabase_url or not supabase_key):
        print("Applying to Supabase requires SUPABASE_URL and SUPABASE_KEY (service role).")
        sys.exit(1)

    rows = []
    if args.inserts_csv:
        rows.extend(load_csv_as_json(args.inserts_csv))
    if args.updates_csv:
        rows.extend(load_csv_as_json(args.updates_csv))
    if args.plan and not (args.inserts_csv or args.updates_csv):
        plan = load_json(args.plan)
        rows.extend(plan.get("inserts", []))
        rows.extend([it["new"] for it in plan.get("updates", [])])

    if not rows:
        print("No rows found to upsert. Provide --plan or CSV inputs.")
        sys.exit(0)

    result = apply_batches(supabase_url, supabase_key, args.table, args.on_conflict, rows, args.batch_size, args.apply)

    print("Result:", result)


if __name__ == "__main__":
    main()
