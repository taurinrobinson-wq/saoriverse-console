#!/usr/bin/env python3
"""
Bulk upsert glyph lexicon into Supabase `glyphs` table using the REST API.

Usage:
  export SUPABASE_URL=...\
         SUPABASE_SERVICE_ROLE_KEY=...\
  python3 dev_tools/upsert_glyphs_to_supabase.py --source emotional_os/glyphs/glyph_lexicon_rows.json

Notes:
- This script uses the service role key. Keep it secret and run in a safe env.
- It upserts by `name` (global glyphs have `user_id` = null). If your DB uses
  different uniqueness constraints, adjust the `on_conflict` param.
"""
import json
import os
import sys
import time
from argparse import ArgumentParser
from typing import List

import requests


def chunked(it: List, size: int):
    for i in range(0, len(it), size):
        yield it[i : i + size]


def load_glyphs(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    # Accept both {"glyphs": [...] } and raw list
    if isinstance(data, dict) and "glyphs" in data:
        return data["glyphs"]
    if isinstance(data, list):
        return data
    raise SystemExit("Unsupported glyph JSON format")


def build_row(src: dict):
    # Map local JSON keys to DB columns
    return {
        "name": src.get("glyph_name") or src.get("glyph") or src.get("name"),
        "description": src.get("description") or None,
        "response_layer": None,
        "depth": None,
        "glyph_type": None,
        "symbolic_pairing": src.get("voltage_pair") or None,
        "created_from_chat": False,
        "source_message": None,
        "emotional_tone": src.get("gate") or None,
        "user_id": None,
    }


def upsert_chunk(supabase_url: str, key: str, rows: List[dict], on_conflict: str = "name"):
    url = f"{supabase_url.rstrip('/')}/rest/v1/glyphs?on_conflict={on_conflict}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    resp = requests.post(url, headers=headers, json=rows, timeout=60)
    try:
        resp.raise_for_status()
    except Exception:
        print("Upsert failed:", resp.status_code, resp.text[:1000])
        raise
    return resp.json()


def main():
    p = ArgumentParser()
    p.add_argument("--source", "-s", default="emotional_os/glyphs/glyph_lexicon_rows.json")
    p.add_argument("--batch", "-b", type=int, default=200)
    args = p.parse_args()

    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE")
    if not supabase_url or not service_key:
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in the environment")
        sys.exit(2)

    glyphs = load_glyphs(args.source)
    print(f"Loaded {len(glyphs)} glyphs from {args.source}")

    rows = [build_row(g) for g in glyphs]

    inserted = 0
    for i, chunk in enumerate(chunked(rows, args.batch), start=1):
        print(f"Upserting batch {i} ({len(chunk)} rows) ...", flush=True)
        try:
            res = upsert_chunk(supabase_url, service_key, chunk)
            inserted += len(res)
            print(f"  upserted {len(res)} rows")
        except Exception as e:
            print("  batch failed:", e)
            break
        time.sleep(0.2)

    print(f"Done. Attempted upsert for {len(rows)} rows. Inserted/updated reported: {inserted}")


if __name__ == "__main__":
    main()
