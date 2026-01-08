"""CI smoke test for ToneCore pipeline

This script is intentionally small and has no external test deps.
It runs the two smoke commands used in development and ensures the
expected MIDI outputs are created. Intended to be run from CI.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "demo_output"
OUT_DIR.mkdir(exist_ok=True)


def run(cmd):
    print(">", " ".join(cmd))
    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode != 0:
        print("Command failed:", cmd)
        sys.exit(res.returncode)


def assert_file(path: Path):
    if not path.exists():
        print("Missing expected file:", path)
        sys.exit(2)
    print("OK:", path)


def load_and_assert_pivot(pivot_path: Path):
    if not pivot_path.exists():
        print("Pivot file not found at", pivot_path)
        sys.exit(3)
    data = json.loads(pivot_path.read_text(encoding="utf8"))
    if not isinstance(data, list) or len(data) == 0:
        print("Pivot did not load as a non-empty list")
        sys.exit(4)

    # Assert every entry has expected top-level keys and transitions
    for i, entry in enumerate(data[:1000]):
        if "key" not in entry or "base_chord" not in entry or "transitions" not in entry:
            print(f"Pivot entry {i} missing required fields")
            sys.exit(5)
        if not isinstance(entry.get("transitions"), list):
            print(f"Pivot entry {i} transitions not a list")
            sys.exit(6)

    # Assert at least one base_chord.function equals 'I' (case-insensitive)
    found_I = False
    for entry in data:
        bfunc = entry.get("base_chord", {}).get("function")
        if bfunc and str(bfunc).strip().lower() == "i":
            found_I = True
            break
    if not found_I:
        print("Pivot sanity: no base_chord with function 'I' found")
        sys.exit(7)
    # Also assert presence of common functions and at least one minor tonic
    found_V = False
    found_vi = False
    found_minor = False
    for entry in data:
        # check base_chord.function
        bfunc = entry.get("base_chord", {}).get("function")
        if bfunc:
            bf = str(bfunc).strip().lower()
            if bf == "v":
                found_V = True
            if bf == "vi":
                found_vi = True
            if bf == "i":
                found_minor = True

        # also check transition functions for presence of V/vi
        for t in entry.get("transitions", []) or []:
            tf = t.get("function")
            if not tf:
                continue
            tfn = str(tf).strip().lower()
            if tfn == "v":
                found_V = True
            if tfn == "vi":
                found_vi = True

    if not found_V:
        print("Pivot sanity: no transition or base_chord with function 'V' found")
        sys.exit(8)
    if not found_vi:
        print("Pivot sanity: no transition or base_chord with function 'vi' found")
        sys.exit(9)
    if not found_minor:
        print("Pivot sanity: no base_chord with minor function 'i' found")
        sys.exit(10)

    print("Pivot assertions passed")


def main():
    # pivot assertions (ensure canonical pivot looks sane before running generators)
    pivot_path = ROOT / "Offshoots" / "ToneCore" / "chord_pivot_normalized.json"
    load_and_assert_pivot(pivot_path)

    # 1) emotion-driven midi
    emotion_out = OUT_DIR / "demo_joy.mid"
    run([sys.executable, "scripts/tonecore_midi.py", "--emotion", "joy", "--out", str(emotion_out)])
    assert_file(emotion_out)

    # 2) glyph cascade demo
    glyph_out = OUT_DIR / "demo_chain.mid"
    run([sys.executable, "scripts/glyph_cascade_demo.py", "--glyphs", "🌙", "💧", "🌞", "--out", str(glyph_out)])
    assert_file(glyph_out)

    print("\nSmoke tests passed")


if __name__ == "__main__":
    main()
