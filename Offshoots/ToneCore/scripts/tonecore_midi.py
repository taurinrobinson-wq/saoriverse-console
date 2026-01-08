"""Tonecore MIDI generator (project-local version)

This script lives inside `Offshoots/ToneCore/scripts` and expects pivot files
to be in the parent `Offshoots/ToneCore/` folder.
"""

import argparse
import json
import random
import re
from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack

BASE = Path(__file__).resolve().parents[1]
PIVOT_PATH = BASE / "chord_pivot_normalized.json"
EMOTION_MAP_PATH = BASE / "emotion_map.json"


def load_pivot(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Pivot JSON not found at {path}")
    data = json.loads(path.read_text(encoding="utf8"))
    mapping = {entry.get("key"): entry for entry in data}
    return mapping


def load_emotion_map(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf8"))


def get_progression_for_emotion(emotion: str, pivot_map: dict, emotion_map: dict, length: int = 4):
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
    if not entry:
        entry = pivot_map.get("C") or next(iter(pivot_map.values()))

    prog = []
    base = entry.get("base_chord", {}).get("name")
    if base:
        prog.append(base)

    transitions = entry.get("transitions", [])
    choices = [t.get("to", {}).get("name") for t in transitions if t.get("to")]
    for _ in range(max(0, length - len(prog))):
        if not choices:
            break
        prog.append(random.choice(choices))

    while len(prog) < length:
        prog.append(base or "C")
    return prog


NOTE_MAP = {
    "c": 60,
    "c#": 61,
    "db": 61,
    "d": 62,
    "d#": 63,
    "eb": 63,
    "e": 64,
    "fb": 64,
    "e#": 65,
    "f": 65,
    "f#": 66,
    "gb": 66,
    "g": 67,
    "g#": 68,
    "ab": 68,
    "a": 69,
    "a#": 70,
    "bb": 70,
    "b": 71,
    "cb": 71,
}


def chord_obj_to_notes(chord_obj):
    if not chord_obj:
        return []
    notes = chord_obj.get("notes") or []
    return notes


def chords_to_midi_from_names(names, pivot_map, filename="tonecore_output.mid"):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=500000))
    track.append(Message("program_change", program=0, time=0))

    ticks_per_beat = mid.ticks_per_beat
    chord_ticks = ticks_per_beat * 4

    for n in names:
        # resolve name to chord obj
        chord_obj = None
        for e in pivot_map.values():
            if e.get("base_chord", {}).get("name") == n:
                chord_obj = e.get("base_chord")
                break
        notes = chord_obj_to_notes(chord_obj)
        if not notes:
            continue
        for note in notes:
            midi_note = NOTE_MAP.get(note.lower(), 60)
            track.append(Message("note_on", note=midi_note, velocity=64, time=0))
        track.append(Message("note_off", note=NOTE_MAP.get(notes[0].lower(), 60), velocity=64, time=chord_ticks))
        for note in notes[1:]:
            track.append(Message("note_off", note=NOTE_MAP.get(note.lower(), 60), velocity=64, time=0))

    mid.save(filename)
    print(f"Saved MIDI progression to {filename}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emotion", default="longing")
    parser.add_argument("--out", default="tonecore_output.mid")
    args = parser.parse_args()

    pivot_map = load_pivot(PIVOT_PATH)
    emotion_map = load_emotion_map(EMOTION_MAP_PATH)

    prog = get_progression_for_emotion(args.emotion, pivot_map, emotion_map)
    print(f"Emotion '{args.emotion}' mapped to progression: {prog}")
    chords_to_midi_from_names(prog, pivot_map, filename=args.out)


if __name__ == "__main__":
    main()
