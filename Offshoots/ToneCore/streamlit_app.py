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
