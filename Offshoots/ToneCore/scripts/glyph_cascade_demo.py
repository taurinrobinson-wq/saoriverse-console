"""Glyph cascade demo (project-local ToneCore version).

Reads `Offshoots/ToneCore/emotion_map.json` and `Offshoots/ToneCore/chord_pivot_normalized.json`.
"""

import json
import argparse
from pathlib import Path
from mido import Message, MidiFile, MidiTrack

# glyph_map kept local for demo
glyph_map = {
    "🌙": "longing",
    "🔥": "stress",
    "💧": "calm",
    "🌞": "joy",
    "🌱": "hope",
    "🌀": "melancholy",
    "⭐": "wonder",
    "🪨": "resolve"
}

BASE = Path(__file__).resolve().parents[1]
EMOTION_MAP_PATH = BASE / 'emotion_map.json'
PIVOT_PATH = BASE / 'chord_pivot_normalized.json'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf8'))


def emotion_to_function(emotion, emotion_map):
    return emotion_map.get(emotion, {}).get('function')


def find_best_transition(function, pivot, prev_notes=None):
    candidates = []
    for entry in pivot:
        base_func = entry.get('base_chord', {}).get('function')
        if str(base_func).lower() != str(function).lower():
            continue
        for t in entry.get('transitions', []) or []:
            shared = t.get('shared_notes') or []
            strength = len(shared)
            if prev_notes:
                strength += len(set(shared) & set(prev_notes))
            candidates.append((strength, t.get('to'), shared))
    if not candidates:
        return None, []
    candidates.sort(key=lambda x: x[0], reverse=True)
    best = candidates[0]
    return best[1], best[2]


NOTE_MAP = {
    "c": 60, "c#": 61, "db": 61, "d": 62, "d#": 63, "eb": 63,
    "e": 64, "fb": 64, "e#": 65, "f": 65, "f#": 66, "gb": 66,
    "g": 67, "g#": 68, "ab": 68, "a": 69, "a#": 70, "bb": 70,
    "b": 71, "cb": 71
}


def chords_to_midi(chord_note_lists, filename='glyph_demo.mid'):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message('program_change', program=0, time=0))
    ticks_per_beat = mid.ticks_per_beat
    chord_ticks = ticks_per_beat * 4
    for notes in chord_note_lists:
        if not notes:
            continue
        for n in notes:
            midi_note = NOTE_MAP.get(n.lower(), 60)
            track.append(
                Message('note_on', note=midi_note, velocity=64, time=0))
        track.append(Message('note_off', note=NOTE_MAP.get(
            notes[0].lower(), 60), velocity=64, time=chord_ticks))
        for n in notes[1:]:
            track.append(Message('note_off', note=NOTE_MAP.get(
                n.lower(), 60), velocity=64, time=0))
    mid.save(filename)
    print(f"Saved MIDI progression to {filename}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--glyphs', nargs='+', help='Sequence of glyphs')
    parser.add_argument('--out', default='glyph_demo.mid')
    args = parser.parse_args()

    emotion_map = load_json(EMOTION_MAP_PATH)
    pivot = load_json(PIVOT_PATH)

    chords = []
    prev_notes = None
    for glyph in args.glyphs:
        emotion = glyph_map.get(glyph)
        if not emotion:
            print(f'No emotion mapping for glyph {glyph}')
            continue
        function = emotion_to_function(emotion, emotion_map)
        if not function:
            print(f'No function mapping for emotion {emotion}')
            continue
        to_chord, shared = find_best_transition(function, pivot, prev_notes)
        if to_chord:
            notes = shared if shared else []
            print(
                f'Glyph {glyph} -> Emotion {emotion} -> Function {function} -> Chord {to_chord} (shared {notes})')
            if notes:
                chords.append(notes)
                prev_notes = notes
            else:
                # find base notes
                found = None
                for e in pivot:
                    if e.get('base_chord', {}).get('name') == to_chord:
                        found = e.get('base_chord', {}).get('notes', [])
                        break
                if found:
                    chords.append(found)
                    prev_notes = found
                else:
                    chords.append([])
                    prev_notes = None

    if chords:
        chords_to_midi(chords, filename=args.out)


if __name__ == '__main__':
    main()
