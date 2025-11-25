"""Minimal Streamlit UI for ToneCore demo

Features:
- Choose emotion or enter glyphs
- Generate MIDI (calls project scripts)
- Render to WAV using fluidsynth and a soundfont
- Play audio directly in the page

Run locally:
  pip install -r Offshoots/ToneCore/requirements.txt
  streamlit run Offshoots/ToneCore/streamlit_app.py
"""
from pathlib import Path
import subprocess
import shlex
import sys
import urllib.request
import shutil
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
TONECORE = ROOT / 'Offshoots' / 'ToneCore'
OUT = ROOT / 'demo_output'
OUT.mkdir(exist_ok=True)
SF2 = TONECORE / 'sf2' / 'FluidR3_GM.sf2'

# Fallback download URL for a small General MIDI soundfont (TimGM6mb - ~6MB)
FALLBACK_SF2_URL = 'https://github.com/urish/sf2/raw/master/TimGM6mb.sf2'


def run_cmd(cmd):
    st.write('> ' + ' '.join(cmd))
    res = subprocess.run(cmd, cwd=str(ROOT))
    return res.returncode


def ensure_soundfont():
    """Return a Path to a usable SF2, or None if unavailable.

    Lookup order:
      1) project-local `Offshoots/ToneCore/sf2/FluidR3_GM.sf2`
      2) common system locations
      3) download a small fallback into the project sf2 dir
    """
    # 1) project-local
    if SF2.exists():
        return SF2

    # 2) common system locations
    candidates = [
        Path('/usr/share/sounds/sf2/FluidR3_GM.sf2'),
        Path('/usr/share/sounds/sf2/TimGM6mb.sf2'),
        Path('/usr/share/sounds/sf2/default-GM.sf2'),
    ]
    for c in candidates:
        if c.exists():
            return c

    # 3) download small fallback
    sf2_dir = SF2.parent
    sf2_dir.mkdir(parents=True, exist_ok=True)
    try:
        dest = sf2_dir / 'TimGM6mb.sf2'
        if not dest.exists():
            st.info(f'Downloading fallback soundfont (~6MB) to {dest}...')
            with urllib.request.urlopen(FALLBACK_SF2_URL, timeout=30) as resp, open(dest, 'wb') as out:
                shutil.copyfileobj(resp, out)
        return dest
    except Exception as e:
        st.warning(f'Could not obtain fallback soundfont: {e}')
        return None


st.title('ToneCore Demo Player')

sf2_path = ensure_soundfont()

tab = st.radio('Mode', ['Emotion', 'Glyphs'])

if tab == 'Emotion':
    emotion = st.selectbox('Emotion', ['joy', 'longing', 'stress', 'calm', 'wonder', 'resolve'])
    if st.button('Generate & Render'):
        midi_out = OUT / f'{emotion}.mid'
        wav_out = OUT / f'{emotion}.wav'
        code = run_cmd([shlex.split(sys.executable)[0], 'scripts/tonecore_midi.py', '--emotion', emotion, '--out', str(midi_out)])
        if code != 0:
            st.error('MIDI generation failed')
        else:
            if not sf2_path:
                st.error('Soundfont not found and fallback download failed')
            else:
                rc = run_cmd(['fluidsynth', '-ni', str(sf2_path), str(midi_out), '-F', str(wav_out), '-r', '44100'])
                if rc == 0 and wav_out.exists():
                    st.audio(str(wav_out))
                else:
                    st.error('Rendering failed')

else:
    glyphs = st.text_input('Glyphs (space-separated)', '🌙 💧 🌞')
    if st.button('Generate & Render Glyph Chain'):
        midi_out = OUT / 'glyph_chain.mid'
        wav_out = OUT / 'glyph_chain.wav'
        parts = glyphs.split()
        cmd = [shlex.split(sys.executable)[0], 'scripts/glyph_cascade_demo.py', '--glyphs'] + parts + ['--out', str(midi_out)]
        code = run_cmd(cmd)
        if code != 0:
            st.error('MIDI generation failed')
        else:
            if not sf2_path:
                st.error('Soundfont not found and fallback download failed')
            else:
                rc = run_cmd(['fluidsynth', '-ni', str(sf2_path), str(midi_out), '-F', str(wav_out), '-r', '44100'])
                if rc == 0 and wav_out.exists():
                    st.audio(str(wav_out))
                else:
                    st.error('Rendering failed')
"""Minimal Streamlit UI for ToneCore demo

Features:
- Choose emotion or enter glyphs
- Generate MIDI (calls project scripts)
- Render to WAV using fluidsynth and the local soundfont
- Play audio directly in the page

Run locally:
  pip install streamlit mido
  streamlit run Offshoots/ToneCore/streamlit_app.py
"""
import subprocess
import shlex
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
TONECORE = ROOT / 'Offshoots' / 'ToneCore'
OUT = ROOT / 'demo_output'
OUT.mkdir(exist_ok=True)
SF2 = TONECORE / 'sf2' / 'FluidR3_GM.sf2'


def run_cmd(cmd):
    st.write('> ' + ' '.join(cmd))
    res = subprocess.run(cmd, cwd=str(ROOT))
    return res.returncode


st.title('ToneCore Demo Player')

tab = st.radio('Mode', ['Emotion', 'Glyphs'])

if tab == 'Emotion':
    emotion = st.selectbox(
        'Emotion', ['joy', 'longing', 'stress', 'calm', 'wonder', 'resolve'])
    if st.button('Generate & Render'):
        midi_out = OUT / f'{emotion}.mid'
        wav_out = OUT / f'{emotion}.wav'
        code = run_cmd([shlex.split('python3')[
                       0], 'scripts/tonecore_midi.py', '--emotion', emotion, '--out', str(midi_out)])
        if code != 0:
            st.error('MIDI generation failed')
        else:
            if not SF2.exists():
                st.error(
                    'Soundfont not found; ensure Offshoots/ToneCore/sf2/FluidR3_GM.sf2 exists')
            else:
                rc = run_cmd(['fluidsynth', '-ni', str(SF2),
                             str(midi_out), '-F', str(wav_out), '-r', '44100'])
                if rc == 0 and wav_out.exists():
                    st.audio(str(wav_out))
                else:
                    st.error('Rendering failed')

else:
    glyphs = st.text_input('Glyphs (space-separated)', '🌙 💧 🌞')
    if st.button('Generate & Render Glyph Chain'):
        midi_out = OUT / 'glyph_chain.mid'
        wav_out = OUT / 'glyph_chain.wav'
        parts = glyphs.split()
        cmd = [shlex.split('python3')[0], 'scripts/glyph_cascade_demo.py',
               '--glyphs'] + parts + ['--out', str(midi_out)]
        code = run_cmd(cmd)
        if code != 0:
            st.error('MIDI generation failed')
        else:
            if not SF2.exists():
                st.error(
                    'Soundfont not found; ensure Offshoots/ToneCore/sf2/FluidR3_GM.sf2 exists')
            else:
                rc = run_cmd(['fluidsynth', '-ni', str(SF2),
                             str(midi_out), '-F', str(wav_out), '-r', '44100'])
                if rc == 0 and wav_out.exists():
                    st.audio(str(wav_out))
                else:
                    st.error('Rendering failed')
