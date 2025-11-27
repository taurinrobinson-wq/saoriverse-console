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

from mido import Message, MidiFile, MidiTrack, MetaMessage
from mido import bpm2tempo


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
    core = text[start: end + 1]
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


def chords_to_midi(chords, filename="tonecore_output.mid", tempo_bpm=90, seed=None, emotion: str = 'neutral'):
    """Write a richer MIDI file with two tracks (accompaniment + melody).

    Features:
    - emotion-driven program changes
    - chord accompaniment with velocity dynamics
    - simple arpeggiated melody derived from chord tones
    - small timing humanization
    - CC91 (reverb send) set according to mood
    """
    random.seed(seed or 0)
    mid = MidiFile()

    # Track 0: tempo / global
    meta = MidiTrack()
    mid.tracks.append(meta)
    tempo = bpm2tempo(tempo_bpm)
    meta.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    # Track 1: accompaniment (chords)
    acc = MidiTrack()
    mid.tracks.append(acc)

    # Track 2: melody / lead
    lead = MidiTrack()
    mid.tracks.append(lead)

    # Emotion → instrument/tempo/reverb defaults
    emotion_map = {
        'longing': {'tempo': 70, 'acc_program': 48, 'lead_program': 40, 'reverb': 96},
        'intimacy': {'tempo': 60, 'acc_program': 0, 'lead_program': 40, 'reverb': 100},
        'joy': {'tempo': 100, 'acc_program': 0, 'lead_program': 24, 'reverb': 36},
        'sadness': {'tempo': 65, 'acc_program': 48, 'lead_program': 42, 'reverb': 110},
        'contentment': {'tempo': 85, 'acc_program': 0, 'lead_program': 40, 'reverb': 48},
        'neutral': {'tempo': tempo_bpm, 'acc_program': 0, 'lead_program': 40, 'reverb': 48},
    }

    cfg = emotion_map.get(str(emotion).lower(), emotion_map['neutral'])
    # override tempo if emotion mapping supplies one
    tempo_bpm = cfg.get('tempo', tempo_bpm)

    # Default programs (General MIDI numbers, 0-based)
    acc_program = cfg.get('acc_program', 0)
    lead_program = cfg.get('lead_program', 40)

    # Set program changes at track start
    acc.append(Message('program_change', program=acc_program, time=0))
    lead.append(Message('program_change', program=lead_program, time=0))

    # Reverb cc (General MIDI uses CC91)
    reverb_val = int(cfg.get('reverb', 48))
    acc.append(Message('control_change', control=91, value=reverb_val, time=0))
    lead.append(Message('control_change', control=91,
                value=reverb_val, time=0))

    # Add expression and sustain for more expressive playback (CC11, CC64)
    acc.append(Message('control_change', control=11, value=80, time=0))
    acc.append(Message('control_change', control=64, value=127, time=0))

    ticks_per_beat = mid.ticks_per_beat
    # Duration: hold each chord for a number of beats — extend for 'longing'
    chord_length_beats = 4
    if str(emotion).lower() == 'longing':
        chord_length_beats = 6
    chord_ticks = ticks_per_beat * chord_length_beats

    # We'll offset the lead slightly so arpeggio feels natural
    for idx, chord in enumerate(chords):
        notes = chord_str_to_notes(chord, octave=4)
        if not notes:
            continue

        # accompaniment: choose sparser voicing for certain emotions
        if str(emotion).lower() == 'longing':
            # pick root and fifth, and optionally lower the root an octave
            acc_notes = []
            acc_notes.append(notes[0])
            if len(notes) >= 3:
                acc_notes.append(notes[2])
            # move accompaniment down an octave for warmth
            acc_notes = [n - 12 if n - 12 >= 0 else n for n in acc_notes]
            base_vel = random.randint(40, 60)
        else:
            acc_notes = notes
            base_vel = random.randint(48, 78)

        for i, n in enumerate(acc_notes):
            vel = max(8, base_vel - i * 6 + random.randint(-3, 3))
            acc.append(Message('note_on', note=n, velocity=vel, time=0))

        # Keep chord sounding for the chord length, then turn off
        acc.append(
            Message('note_off', note=acc_notes[0], velocity=0, time=chord_ticks))
        for n in acc_notes[1:]:
            acc.append(Message('note_off', note=n, velocity=0, time=0))

        # lead: simple arpeggio across chord tones and neighboring passing tone
        arpeggio = notes + [notes[0] + 12]
        # small offset after chord
        lead_start_offset = int(ticks_per_beat * 0.1)
        # make arpeggio timing depend on chord length; slow it for 'longing'
        base_time_per_note = max(1, int(chord_ticks / max(1, len(arpeggio))))
        if str(emotion).lower() == 'longing':
            base_time_per_note = int(base_time_per_note * 1.5)

        # add small humanization jitter and overlap notes slightly for legato
        for i, n in enumerate(arpeggio):
            jitter = random.randint(-6, 6)
            vel = random.randint(56, 86) if str(
                emotion).lower() != 'longing' else random.randint(48, 70)
            note_on_time = lead_start_offset if i == 0 else max(
                0, base_time_per_note + jitter)
            # note_on
            lead.append(Message('note_on', note=n,
                        velocity=vel, time=note_on_time))
            # schedule note_off to slightly overlap next note for legato feel
            off_delay = max(1, int(base_time_per_note * 0.9))
            lead.append(Message('note_off', note=n,
                        velocity=0, time=off_delay))

    mid.save(filename)
    print(f"Saved MIDI progression to {filename}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emotion', default='longing')
    parser.add_argument('--controls', default=None,
                        help='Path to JSON file containing musical controls')
    parser.add_argument('--out', default='tonecore_output.mid')
    args = parser.parse_args()

    chords_by_key = load_pivot(PIVOT_PATH)

    # default emotion map — extend as needed
    emotion_map = {
        "longing": {"key": "C", "scale": "minor"},
        "stress": {"key": "D", "scale": "dorian"},
        "calm": {"key": "G", "scale": "major"},
        "joy": {"key": "A", "scale": "major"},
    }

    prog = get_progression_for_emotion(
        args.emotion, chords_by_key, emotion_map)
    print(f"Emotion '{args.emotion}' mapped to progression: {prog}")

    # If controls JSON provided, load it and pass into chords_to_midi
    controls = None
    if args.controls:
        try:
            with open(args.controls, 'r', encoding='utf8') as fh:
                controls = json.load(fh)
        except Exception:
            controls = None

    if controls:
        # allow controls to override tempo and emotion
        tempo_bpm = controls.get('tempo') or 90
        chords_to_midi(prog, filename=args.out,
                       tempo_bpm=tempo_bpm, seed=None, emotion=args.emotion)
    else:
        chords_to_midi(prog, filename=args.out, emotion=args.emotion)


if __name__ == '__main__':
    main()
