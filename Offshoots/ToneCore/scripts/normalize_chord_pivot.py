"""Normalize chord pivot (project-local version).

Reads from `Offshoots/ToneCore/chord_pivot.json` (if present) or falls back
to the repo root `Offshoots/chord_pivot.json` and writes normalized output
into the ToneCore folder.
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
IN = BASE / "chord_pivot.json"
FALLBACK_IN = Path(__file__).resolve().parents[3] / "Offshoots" / "chord_pivot.json"
OUT = BASE / "chord_pivot_normalized.json"


def load_raw(path: Path):
    text = path.read_text(encoding="utf8")
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found in pivot file")
    core = text[start : end + 1]
    return json.loads(core)


def split_notes(val):
    if val is None:
        return []
    if isinstance(val, list):
        return [str(v).strip().lower() for v in val if v is not None]
    s = str(val).strip()
    if not s:
        return []
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
        trans.append({"to": to, "function": func, "shared_notes": shared_norm})
    out["transitions"] = trans
    return out


def main():
    src = IN if IN.exists() else FALLBACK_IN
    raw = load_raw(src)
    chord_lookup = {}
    for e in raw:
        bc = e.get("base_chord", {})
        name = bc.get("name")
        notes = split_notes(bc.get("notes"))
        if name:
            chord_lookup[str(name)] = notes

    prelim = [normalize_entry(e) for e in raw]

    resolved = []
    for e in prelim:
        newt = []
        for t in e.get("transitions", []):
            to_name = t.get("to")
            notes = chord_lookup.get(to_name) or []
            to_obj = {"name": to_name, "notes": notes}
            newt.append({"to": to_obj, "function": t.get("function"), "shared_notes": t.get("shared_notes", [])})
        e["transitions"] = newt
        if not e.get("base_chord", {}).get("notes"):
            bname = e.get("base_chord", {}).get("name")
            e["base_chord"]["notes"] = chord_lookup.get(bname, [])
        resolved.append(e)

    OUT.write_text(json.dumps(resolved, indent=2, ensure_ascii=False), encoding="utf8")
    print(f"Wrote {len(resolved)} normalized entries (with full chord objects) to {OUT}")


if __name__ == "__main__":
    main()
