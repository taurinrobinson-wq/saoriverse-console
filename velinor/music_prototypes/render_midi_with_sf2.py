"""Render MIDI to WAV using an SF2 soundfont via fluidsynth if available.

Fallback: synthesize simple sine-based WAV (approximate) using numpy.

Usage:
  pip install -r requirements.txt
  python render_midi_with_sf2.py velinor_motif.mid velinor_motif.wav
  python render_midi_with_sf2.py saori_motif.mid saori_motif.wav

If `fluidsynth` is installed and on PATH, it will be used with the provided soundfont.
Otherwise the script will create a basic sine-rendered WAV as a reference.
"""
import sys
import os
import shutil
import subprocess
from mido import MidiFile

SF2_CANDIDATES = [
    os.path.join('Offshoots', 'ToneCore', 'sf2', 'FluidR3_GM.sf2'),
    os.path.join('velinor', 'music_prototypes', 'FluidR3_GM.sf2')
]

def find_soundfont():
    # prefer absolute paths and validate existence
    cwd = os.path.abspath(os.getcwd())
    for p in SF2_CANDIDATES:
        ap = os.path.abspath(os.path.join(cwd, p))
        if os.path.exists(ap):
            return ap
    # as a last resort, check the candidates as absolute already
    for p in SF2_CANDIDATES:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


def validate_sf2(path):
    """Return True if file at path looks like a valid .sf2 SoundFont (RIFF/sfbk header)."""
    try:
        with open(path, 'rb') as f:
            header = f.read(12)
            if len(header) < 12:
                return False
            # RIFF....sfbk
            if header[0:4] != b'RIFF':
                return False
            if header[8:12] != b'sfbk':
                return False
            return True
    except Exception:
        return False


def fluidsynth_render(sf2, midi_in, wav_out, sample_rate=44100):
    # fluidsynth CLI: fluidsynth -ni soundfont.sf2 midi.mid -F out.wav -r 44100
    # ensure absolute paths
    sf2p = os.path.abspath(sf2)
    midp = os.path.abspath(midi_in)
    wavp = os.path.abspath(wav_out)
    # fluidsynth expects options first, then soundfont(s) then MIDI files
    cmd = ["fluidsynth", "-ni", "-F", wavp, "-r", str(sample_rate), sf2p, midp]
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd)


def fallback_render(midi_in, wav_out, sample_rate=44100):
    import numpy as np
    import wave
    from math import sin, pi

    mid = MidiFile(midi_in)
    ticks_per_beat = mid.ticks_per_beat
    tempo = 500000  # default 120bpm fallback
    # find first set_tempo if present
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
    ticks_per_sec = 1e6 / tempo * (1.0 / ticks_per_beat)

    # collect note events per channel/note
    notes = []  # (note, start_sec, end_sec, velocity)
    ongoing = {}
    current_time = 0.0
    for msg in mid:
        current_time += msg.time * (1e-6 * tempo) / ticks_per_beat
        if msg.type == 'note_on' and msg.velocity > 0:
            ongoing.setdefault((msg.channel if hasattr(msg,'channel') else 0, msg.note), []).append((current_time, msg.velocity))
        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            key = (msg.channel if hasattr(msg,'channel') else 0, msg.note)
            if key in ongoing and ongoing[key]:
                start, vel = ongoing[key].pop(0)
                notes.append((msg.note, start, current_time, vel))

    # determine total length
    end_time = 0.0
    for n in notes:
        end_time = max(end_time, n[2])
    total_samples = int((end_time + 1.0) * sample_rate)
    out = np.zeros(total_samples, dtype=np.float32)

    def note_freq(n):
        return 440.0 * (2 ** ((n - 69) / 12.0))

    for note, start, end, vel in notes:
        s0 = int(start * sample_rate)
        s1 = int(end * sample_rate)
        if s1 <= s0:
            s1 = s0 + int(0.05 * sample_rate)
        dur = s1 - s0
        t = np.linspace(0, dur / sample_rate, dur, endpoint=False)
        freq = note_freq(note)
        # simple ADSR
        # compute ADSR segments safely for very short notes
        attack = int(0.02 * sample_rate)
        release = int(0.04 * sample_rate)
        if dur <= 0:
            continue
        attack = min(attack, dur)
        # reserve remaining for release; if not enough, scale release down
        remaining = dur - attack
        release = min(release, remaining)
        sustain_len = remaining - release
        parts = []
        if attack > 0:
            parts.append(np.linspace(0, 1.0, attack, endpoint=False))
        if sustain_len > 0:
            parts.append(np.ones(sustain_len))
        if release > 0:
            parts.append(np.linspace(1.0, 0.0, release))
        env = np.concatenate(parts) if parts else np.ones(dur)
        vel_gain = vel / 127.0
        sine_wave = 0.9 * np.sin(2 * pi * freq * t) * env * vel_gain
        out[s0:s0+dur] += sine_wave

    # normalize
    maxv = np.max(np.abs(out))
    if maxv > 0:
        out = out / maxv * 0.9

    # write WAV (16-bit PCM)
    import wave as _wave
    with _wave.open(wav_out, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        ints = (out * 32767).astype('<i2').tobytes()
        wf.writeframes(ints)
    print('Wrote (fallback) ', wav_out)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python render_midi_with_sf2.py input.mid output.wav')
        sys.exit(1)
    midi_in = sys.argv[1]
    wav_out = sys.argv[2]

    midi_in_path = os.path.abspath(midi_in)
    wav_out_path = os.path.abspath(wav_out)

    sf2 = find_soundfont()
    fs_path = shutil.which('fluidsynth')

    if fs_path and sf2:
        if not validate_sf2(sf2):
            print(f'Found soundfont at {sf2} but header check failed; falling back.')
            sf2 = None

    if fs_path and sf2:
        try:
            fluidsynth_render(sf2, midi_in_path, wav_out_path)
        except subprocess.CalledProcessError as e:
            print('fluidsynth rendering failed:', e)
            print('Falling back to approximate synth.')
            fallback_render(midi_in_path, wav_out_path)
    else:
        if not fs_path:
            print('fluidsynth not found on PATH; using fallback synth.')
        elif not sf2:
            print('No valid soundfont found; using fallback synth.')
        fallback_render(midi_in_path, wav_out_path)
