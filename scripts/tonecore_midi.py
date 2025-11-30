"""
Tonecore Prototype – MIDI Generator
-----------------------------------
Loads `Offshoots/tonecore_chord_pivot.json`, maps emotion tokens to chord
progressions, and outputs a short MIDI file using `mido`.

Run:
  /workspaces/saoriverse-console/.venv/bin/python scripts/tonecore_midi.py --emotion longing

This script is safety-first: it does not require any secrets and only reads
the checked-in pivot JSON created from your Excel file.
"""

import argparse
import json
import random
import re
from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack

PIVOT_PATH = Path("Offshoots/chord_pivot.json")


def load_pivot(path: Path):
    """Load the cleaned pivot JSON (robust to markdown wrappers).

    Returns a dict: key -> entry where entry contains 'base_chord' and 'transitions'.
    """
    if not path.exists():
        raise FileNotFoundError(f"Pivot JSON not found at {path}")
    text = path.read_text(encoding="utf8")
    # Heuristic: locate first '[' to skip markdown/code fences or prose
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found in pivot file")
    core = text[start : end + 1]
    data = json.loads(core)
    mapping = {}
    for entry in data:
        k = entry.get("key")
        if not k:
            continue
        mapping[str(k)] = entry
    return mapping


NOTE_TO_MIDI = {
    "C": 60,
    "D": 62,
    "E": 64,
    "F": 65,
    "G": 67,
    "A": 69,
    "B": 71,
}


def chord_str_to_notes(chord: str, octave: int = 4):
    """Convert a simple chord token (e.g., C, C#, Cm, F#m7) into MIDI note numbers.

    Rules (simple, pragmatic):
    - Root is first char A-G plus optional #/b.
    - If token contains 'm' (lowercase) or 'min' treat as minor triad (root, +3, +7 semitones).
    - Else treat as major triad (root, +4, +7).
    - If token contains '7' add the minor 7th (+10 semitones) after the triad.
    """
    if not chord:
        return []
    m = re.match(r"^([A-Ga-g])([#b]?)(.*)$", chord)
    if not m:
        return []
    root_letter = m.group(1).upper()
    accidental = m.group(2) or ""
    suffix = (m.group(3) or "").lower()
    root_name = root_letter + accidental
    base = NOTE_TO_MIDI.get(root_letter, 60)
    # adjust for accidental
    if accidental == "#":
        base += 1
    elif accidental == "b":
        base -= 1

    # choose octave
    base = base + (octave - 4) * 12

    is_minor = "m" in suffix and not "maj" in suffix
    has_seven = "7" in suffix

    if is_minor:
        third = base + 3
    else:
        third = base + 4
    fifth = base + 7
    notes = [base, third, fifth]
    if has_seven:
        notes.append(base + 10)
    return notes


def get_progression_for_emotion(emotion: str, pivot_map: dict, emotion_map: dict, length: int = 4):
    """Select a short progression based on emotion using the pivot mapping.

    Strategy:
    - If emotion_map defines a `key`, use that key's base_chord and transitions.
    - Else if emotion_map defines a `function`, pick any key whose base_chord.function
      matches that function (case-insensitive), then use its transitions.
    - Build a progression starting from the base chord then sampling transitions.
    """
    cfg = emotion_map.get(emotion, {})
    target_key = cfg.get("key")
    target_function = cfg.get("function")

    entry = None
    if target_key:
        entry = pivot_map.get(target_key)
    if not entry and target_function:
        tf = str(target_function).lower()
        for k, e in pivot_map.items():
            bf = str(e.get("base_chord", {}).get("function", "")).lower()
            if bf == tf:
                entry = e
                break
    # fallback: pick C if available, else any entry
    if not entry:
        entry = pivot_map.get("C") or next(iter(pivot_map.values()))

    prog = []
    # start with base chord
    base = entry.get("base_chord", {}).get("name")
    if base:
        prog.append(base)

    transitions = entry.get("transitions", [])
    if transitions:
        # sample next chords from transitions (avoid repeats when possible)
        choices = [t.get("to") for t in transitions if t.get("to")]
        for _ in range(max(0, length - len(prog))):
            if not choices:
                break
            pick = random.choice(choices)
            prog.append(pick)

    # ensure length
    while len(prog) < length:
        # append base again as filler
        if base:
            prog.append(base)
        else:
            prog.append("C")
    return prog


def chords_to_midi(chords, filename="tonecore_output.mid", tempo=500000):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    # tempo meta
    track.append(MetaMessage("set_tempo", tempo=tempo))
    # program change to a simple piano patch (0)
    track.append(Message("program_change", program=0, time=0))

    ticks_per_beat = mid.ticks_per_beat
    # Duration: hold each chord for 1 bar (4 beats)
    chord_ticks = ticks_per_beat * 4

    for chord in chords:
        notes = chord_str_to_notes(chord)
        if not notes:
            continue
        # note_on for each
        for n in notes:
            track.append(Message("note_on", note=n, velocity=64, time=0))
        # note_off after chord_ticks
        # we off the first note with time=chord_ticks, then subsequent offs with time=0
        track.append(Message("note_off", note=notes[0], velocity=64, time=chord_ticks))
        for n in notes[1:]:
            track.append(Message("note_off", note=n, velocity=64, time=0))

    mid.save(filename)
    print(f"Saved MIDI progression to {filename}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emotion", default="longing")
    parser.add_argument("--out", default="tonecore_output.mid")
    args = parser.parse_args()

    chords_by_key = load_pivot(PIVOT_PATH)

    # default emotion map — extend as needed
    emotion_map = {
        "longing": {"key": "C", "scale": "minor"},
        "stress": {"key": "D", "scale": "dorian"},
        "calm": {"key": "G", "scale": "major"},
        "joy": {"key": "A", "scale": "major"},
    }

    prog = get_progression_for_emotion(args.emotion, chords_by_key, emotion_map)
    print(f"Emotion '{args.emotion}' mapped to progression: {prog}")
    chords_to_midi(prog, filename=args.out)


if __name__ == "__main__":
    main()
