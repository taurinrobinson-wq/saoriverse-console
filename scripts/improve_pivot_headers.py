"""Attempt to infer human-friendly slot names for unnamed columns in the pivot JSON.

Heuristic: for keys like 'Unnamed: N' or 'Unnamed' or 'colX', look at the most
common non-null value in that slot across rows; if it looks like a slot token
(no commas and short), use it as the new slot name.
"""

import json
from pathlib import Path
from collections import Counter
import re


IN_PATH = Path("Offshoots/tonecore_chord_pivot.json")
BACKUP = Path("Offshoots/tonecore_chord_pivot.json.bak")


def looks_like_slot(s: str) -> bool:
    if not s:
        return False
    if "," in s:
        return False
    if len(s) > 20:
        return False
    # allow typical roman numerals, chord names like C#M, Am, V7, viio, etc.
    return bool(re.match(r"^[A-Za-z0-9()#+\-]+$", s))


def improve():
    data = json.loads(IN_PATH.read_text(encoding="utf8"))
    Path(BACKUP).write_text(json.dumps(
        data, indent=2, ensure_ascii=False), encoding="utf8")
    changed = False
    for sheet, rows in data.items():
        # collect per-slot values
        slot_values = {}
        for r in rows:
            allowed = r.get("allowed_chords", {})
            for k, v in allowed.items():
                slot_values.setdefault(k, []).append(v)

        # attempt to rename ambiguous keys
        rename_map = {}
        for k, vals in slot_values.items():
            if k.startswith("Unnamed") or k.lower().startswith("col"):
                # find most common non-null value
                non_nulls = [str(x).strip()
                             for x in vals if x is not None and str(x).strip()]
                if not non_nulls:
                    continue
                mode, freq = Counter(non_nulls).most_common(1)[0]
                if looks_like_slot(mode) and freq >= max(2, int(len(rows) * 0.08)):
                    # use mode as new slot name
                    newk = mode
                    if newk != k:
                        rename_map[k] = newk

        if rename_map:
            changed = True
            for r in rows:
                allowed = r.get("allowed_chords", {})
                for oldk, newk in rename_map.items():
                    if oldk in allowed:
                        # only set new key if not present already
                        if newk not in allowed:
                            allowed[newk] = allowed.get(oldk)
                        # remove old
                        allowed.pop(oldk, None)

    if changed:
        IN_PATH.write_text(json.dumps(
            data, indent=2, ensure_ascii=False), encoding="utf8")
        print(f"Improved headers and wrote updated JSON (backup at {BACKUP})")
    else:
        print("No ambiguous headers detected/changed.")


if __name__ == '__main__':
    improve()
