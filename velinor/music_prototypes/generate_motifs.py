"""Generate two simple MIDI prototypes for Velinor and Saori motifs.

Usage:
  pip install -r requirements.txt
  python generate_motifs.py

This writes `velinor_motif.mid` and `saori_motif.mid` into this folder.
"""
from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage

TICKS_PER_BEAT = 480
TEMPO = bpm2tempo(60)

def write_midi(filename, events):
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)
    # default tempo meta (can be overridden by events if needed)
    track.append(MetaMessage('set_tempo', tempo=TEMPO, time=0))
    for msg, dt in events:
        m = msg.copy(time=dt)
        track.append(m)
    mid.save(filename)
    print(f"Wrote {filename}")

# Velinor motif: single D (D3 = 50) and upper D (D4 = 62)
# Pressure states simulate muted->full by velocity and note length.
def velinor_events():
    lower_d = 50
    upper_d = 62
    events = []
    # pressure states: (velocity, duration_ticks)
    states = [ (24, 60), (40, 90), (64, 150), (90, 240), (110, 360) ]
    # Repeat a two-note figure per state (lower D then broken upper D)
    for vel, dur in states:
        # lower D (octave pair)
        events.append((Message('note_on', note=lower_d, velocity=vel), 0))
        events.append((Message('note_on', note=upper_d, velocity=vel//2), 0))
        events.append((Message('note_off', note=lower_d, velocity=0), dur))
        events.append((Message('note_off', note=upper_d, velocity=0), 0))
        # short silence between iterations
        events.append((Message('program_change', program=0), int(TICKS_PER_BEAT * 0.1)))
    return events

# Saori motif: D octaves <-> F-A dyads in D minor (slow pendulum)
def saori_events():
    lower_d = 50  # D3
    upper_d = 62  # D4
    f = 53       # F3
    a = 57       # A3
    events = []
    # half-note = 2 beats -> 2 * TICKS_PER_BEAT
    half_note = 2 * TICKS_PER_BEAT
    pattern = [
        # D octaves (heavy, sustained half-note)
        ([(lower_d, 96), (upper_d, 96)], half_note),
        # F-A dyad (heavy, unresolved half-note)
        ([(f, 90), (a, 90)], half_note),
    ]
    # repeat pattern to create a slow, measured loop
    for i in range(8):
        for notes, dur in pattern:
            for note, vel in notes:
                events.append((Message('note_on', note=note, velocity=vel), 0))
            events.append((Message('note_off', note=notes[0][0], velocity=0), dur))
            # note_off for other notes (at same time offset)
            events.append((Message('note_off', note=notes[1][0], velocity=0), 0))
            events.append((Message('program_change', program=0), int(TICKS_PER_BEAT * 0.1)))
    return events

if __name__ == '__main__':
    write_midi('velinor_motif.mid', velinor_events())
    # write saori at 70 BPM (lento) by inserting explicit tempo meta before saving
    # create saori midi with track tempo set to 70 BPM
    # we adjust global TEMPO temporarily
    old_tempo = TEMPO
    TEMPO = bpm2tempo(70)
    write_midi('saori_motif.mid', saori_events())
    TEMPO = old_tempo
