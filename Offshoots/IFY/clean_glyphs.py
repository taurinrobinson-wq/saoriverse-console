#!/usr/bin/env python3
"""
Safe glyph cleaning script.
- Scans directories for .json glyph files
- Validates shape against permissive rules
- Removes unknown top-level keys (per schema's allowed keys)
- Normalizes common fields
- Writes cleaned copies to a `canonical_cleaned/` folder preserving structure

Usage:
  python clean_glyphs.py --source path/to/glyphs --dest path/to/canonical_cleaned --dry-run

Note: This script avoids external deps so it can run in minimal Python env.
"""

import argparse
import json
import os
import shutil
from datetime import datetime

# Allowed top-level keys from our schema
ALLOWED_KEYS = {
    "id",
    "name",
    "description",
    "primary_emotions",
    "intensity",
    "tags",
    "glyph_type",
    "version",
    "provenance",
    "assets",
    "metadata",
}

DEFAULT_GLYPH = {
    "id": "",
    "name": "unnamed",
    "primary_emotions": [],
    "intensity": 0.5,
    "glyph_type": "emotion",
    "version": "1.0",
}


def normalize_glyph(data):
    changed = []
    # Remove extraneous keys
    keys = list(data.keys())
    for k in keys:
        if k not in ALLOWED_KEYS:
            data.pop(k, None)
            changed.append(f"removed_key:{k}")

    # Ensure required fields exist
    for k, v in DEFAULT_GLYPH.items():
        if k not in data or data[k] in (None, ""):
            data[k] = v
            changed.append(f"defaulted:{k}")

    # Normalize types
    if not isinstance(data.get("primary_emotions"), list):
        data["primary_emotions"] = [str(data.get("primary_emotions"))] if data.get("primary_emotions") else []
        changed.append("normalized:primary_emotions")

    try:
        intensity = float(data.get("intensity", 0.5))
        intensity = max(0.0, min(1.0, intensity))
        if intensity != data.get("intensity"):
            changed.append("normalized:intensity")
        data["intensity"] = intensity
    except Exception:
        data["intensity"] = 0.5
        changed.append("fixed:intensity")

    # Ensure tags is list
    if not isinstance(data.get("tags", []), list):
        data["tags"] = [str(data.get("tags"))]
        changed.append("normalized:tags")

    # Provenance normalization
    prov = data.get("provenance") or {}
    if isinstance(prov, str):
        prov = {"source": prov}
        changed.append("normalized:provenance")
    if "created_at" in prov:
        # try parse / leave as string if unknown
        pass
    data["provenance"] = prov

    return data, changed


def process_file(path, src_root, dest_root, dry_run=True):
    rel = os.path.relpath(path, src_root)
    dest_path = os.path.join(dest_root, rel)
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            return {"path": path, "error": f"json_error:{e}"}

    cleaned, changes = normalize_glyph(data)
    result = {"path": path, "changes": changes}

    if not dry_run:
        # write backup
        bak = path + ".bak"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with open(dest_path, "w", encoding="utf-8") as fout:
            json.dump(cleaned, fout, indent=2, ensure_ascii=False)
        result["written"] = dest_path

    return result


def scan_and_clean(source, dest, dry_run=True):
    results = []
    for root, dirs, files in os.walk(source):
        for name in files:
            if name.lower().endswith(".json"):
                path = os.path.join(root, name)
                r = process_file(path, source, dest, dry_run=dry_run)
                results.append(r)
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="Source folder to scan for glyph JSONs")
    p.add_argument("--dest", required=True, help="Destination folder for cleaned glyphs")
    p.add_argument("--dry-run", action="store_true", help="Do not write files; only report")
    args = p.parse_args()

    start = datetime.utcnow().isoformat() + "Z"
    print(f"IFY glyph cleaner started at {start}")
    out = scan_and_clean(args.source, args.dest, dry_run=args.dry_run)
    print(json.dumps({"started": start, "summary_count": len(out), "results": out}, indent=2, ensure_ascii=False))
