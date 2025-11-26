"""Normalize `Offshoots/chord_pivot.json` into canonical fields.

Outputs `Offshoots/chord_pivot_normalized.json` where each entry is:
{
  "key": "C",
  "base_chord": {"name":"C","function":"I","notes":["c","e","g"]},
  "transitions": [ {"to":"Am","function":"vi","shared_notes":["a","c","e"]}, ... ]
}

This script is robust to markdown wrappers (code fences) and will coerce
string note lists like "c, e, g" into arrays, and convert null/None/"Nope"
to proper `null` (`None` in Python).
"""

from pathlib import Path
import json
import re


IN = Path("Offshoots/chord_pivot.json")
# Write normalized canonical pivot into the ToneCore project so the full
# dataset lives with the ToneCore offshoot (portable, self-contained).
OUT = Path("Offshoots/ToneCore/chord_pivot_normalized.json")


def load_raw(path: Path):
    text = path.read_text(encoding="utf8")
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found in pivot file")
    core = text[start:end+1]
    return json.loads(core)


def split_notes(val):
    if val is None:
        return []
    if isinstance(val, list):
        return [str(v).strip().lower() for v in val if v is not None]
    s = str(val).strip()
    if not s:
        return []
    # split on commas and spaces
    parts = re.split(r"[,/]+", s)
    out = []
    for p in parts:
        for tok in p.split():
            t = tok.strip().lower()
            if t:
                out.append(t)
    return out


def normalize_entry(e):
    out = {}
    out["key"] = e.get("key")
    bc = e.get("base_chord", {})
    bname = bc.get("name") or bc.get("chord") or bc.get("root")
    bfunc = bc.get("function")
    bnotes = split_notes(bc.get("notes"))
    out["base_chord"] = {"name": bname, "function": bfunc, "notes": bnotes}
    trans = []
    for t in e.get("transitions", []) or []:
        to = t.get("to")
        func = t.get("function")
        shared = t.get("shared_notes")
        shared_norm = split_notes(shared)
        # 'to' may be a chord name string; we'll resolve it later using chord_lookup
        trans.append({"to": to, "function": func, "shared_notes": shared_norm})
    out["transitions"] = trans
    return out


def main():
    raw = load_raw(IN)

    # Build a chord lookup from base_chord names -> notes (normalized)
    chord_lookup = {}
    for e in raw:
        bc = e.get("base_chord", {})
        name = bc.get("name")
        notes = split_notes(bc.get("notes"))
        if name:
            chord_lookup[str(name)] = notes

    # Normalize entries first (keeps 'to' as name for now)
    prelim = [normalize_entry(e) for e in raw]

    # Resolve transitions 'to' into full chord objects {name, notes}
    resolved = []
    for e in prelim:
        newt = []
        for t in e.get("transitions", []):
            to_name = t.get("to")
            notes = chord_lookup.get(to_name) or []
            to_obj = {"name": to_name, "notes": notes}
            newt.append({"to": to_obj, "function": t.get("function"),
                        "shared_notes": t.get("shared_notes", [])})
        e["transitions"] = newt
        # also ensure base_chord.notes are present in normalized form
        if not e.get("base_chord", {}).get("notes"):
            bname = e.get("base_chord", {}).get("name")
            e["base_chord"]["notes"] = chord_lookup.get(bname, [])
        resolved.append(e)

    OUT.write_text(json.dumps(resolved, indent=2,
                   ensure_ascii=False), encoding="utf8")
    print(
        f"Wrote {len(resolved)} normalized entries (with full chord objects) to {OUT}")


if __name__ == '__main__':
    main()
