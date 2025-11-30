"""Convert Tonecore Excel pivot to a clean JSON schema.

Produces `Offshoots/tonecore_chord_pivot.json` where each row is:
{
  "key": "A#m",
  "triad": ["a#","c#","e#"],
  "function": "i",
  "allowed_chords": {"V7": null, "vi": "C#M"}
}

This script reads all sheets and outputs a dict of sheet->rows.
"""

import json
import math
from pathlib import Path

import pandas as pd

SOURCE_XLSX = Path("Offshoots/Chord Pivot.xlsx")
OUT_JSON = Path("Offshoots/tonecore_chord_pivot.json")


def normalize_triads(val):
    if val is None:
        return []
    s = str(val).strip()
    if not s:
        return []
    # split on commas or slashes
    parts = [p.strip() for p in s.split(",") if p.strip()]
    # further split parts that contain spaces
    out = []
    for p in parts:
        for tok in p.split():
            t = tok.strip().lower()
            if t:
                out.append(t)
    return out


def to_none_if_empty(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    low = s.lower()
    if low in ("none", "nope", "nan"):
        return None
    return s


def convert_sheet(df: pd.DataFrame):
    rows = []
    # Ensure consistent column ordering
    cols = list(df.columns)
    if len(cols) < 3:
        raise ValueError("Expected at least 3 columns (key, triad, function)")

    for _, r in df.iterrows():
        # Use first three columns as key, triad, function (heuristic)
        key = to_none_if_empty(r[cols[0]])
        if key is None:
            # skip blank key rows
            continue
        triad = normalize_triads(r[cols[1]])
        function = to_none_if_empty(r[cols[2]]) or ""

        allowed = {}
        for c in cols[3:]:
            val = to_none_if_empty(r[c])
            # use the column header as the slot name (cleaned)
            slot = str(c).strip()
            if slot == "":
                continue
            allowed[slot] = val

        entry = {
            "key": str(key).strip(),
            "triad": triad,
            "function": str(function).strip(),
            "allowed_chords": allowed,
        }
        rows.append(entry)
    return rows


def main():
    if not SOURCE_XLSX.exists():
        raise FileNotFoundError(f"Source Excel not found at {SOURCE_XLSX}")

    xls = pd.ExcelFile(SOURCE_XLSX)
    out = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, dtype=object)
        # clean column names
        df.columns = [str(c).strip() for c in df.columns]
        if len(df.columns) < 3:
            print(f"Skipping sheet '{sheet}' — fewer than 3 columns ({len(df.columns)})")
            continue
        out[sheet] = convert_sheet(df)

    # write JSON
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf8")
    print(f"Wrote {sum(len(v) for v in out.values())} rows across {len(out)} sheets to {OUT_JSON}")


if __name__ == "__main__":
    main()
