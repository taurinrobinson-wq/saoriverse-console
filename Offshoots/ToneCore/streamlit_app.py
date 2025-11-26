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
# deferred import of parse_input to avoid startup blocking
import sqlite3

# Enable faulthandler at startup so we can dump Python thread
# backtraces to stderr/logs by sending SIGUSR1 to the process. This
# helps diagnose hangs where the server accepts TCP connections but
# doesn't respond.
import faulthandler
import signal

try:
    faulthandler.enable()
    # Register SIGUSR1 to dump tracebacks to stderr
    faulthandler.register(signal.SIGUSR1)
except Exception:
    # If faulthandler or signal registration isn't available, continue
    pass

# Enhanced processor (NRC + TextBlob + spaCy)
# Deferred import of EnhancedEmotionProcessor to avoid blocking startup
# from parser.enhanced_emotion_processor import EnhancedEmotionProcessor

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

st.markdown("""
Enter text (multi-line). The app will parse the input using the project's
signal parsers and generate a MIDI progression based on the glyphs found.
""")

user_text = st.text_area('Input text', value='', height=160)

if st.button('Generate & Render'):
    if not user_text.strip():
        st.warning('Please enter some text to analyze.')
    else:
        # 1) Run the base parser to find glyphs/signals (helps UI transparency)
        with st.spinner('Parsing input (signal parser)...'):
            try:
                from emotional_os.core.signal_parser import parse_input
                parsed = parse_input(
                    user_text, 'emotional_os/parser/signal_lexicon.json')
            except Exception as e:
                st.error(f'Parsing failed: {e}')
                parsed = None

        if not parsed:
            st.error('Parsing returned no result; cannot continue')
        else:
            # Show parser outputs briefly
            st.subheader('Signal Parser Results')
            st.write('Signals:', parsed.get('signals'))
            st.write('Gates:', parsed.get('gates'))

            # 2) Run enhanced NLP analysis (NRC + TextBlob + spaCy)
            with st.spinner('Running enhanced NLP analysis (NRC + TextBlob + spaCy)...'):
                try:
                    # Import here to avoid heavy imports at top-level
                    from parser.enhanced_emotion_processor import EnhancedEmotionProcessor
                    eproc = EnhancedEmotionProcessor()
                    enhanced = eproc.analyze_emotion_comprehensive(user_text)
                except Exception as e:
                    st.error(f'Enhanced analysis failed: {e}')
                    enhanced = None

            if enhanced:
                st.subheader('Enhanced Analysis')
                st.write('NRC emotions:', enhanced.get('nrc_emotions'))
                st.write('TextBlob sentiment:',
                         enhanced.get('textblob_sentiment'))
                st.write('spaCy syntax:', enhanced.get('spacy_syntax'))
                st.write('Dominant emotion:', enhanced.get(
                    'dominant_emotion'), 'confidence:', enhanced.get('confidence'))
                st.write('Recommended gates:',
                         enhanced.get('recommended_gates'))
                st.write('Enhanced signals:', enhanced.get('enhanced_signals'))

            # Let the user confirm the emotion to use (default to enhanced dominant emotion)
            default_emotion = (enhanced.get(
                'dominant_emotion') if enhanced and enhanced.get('dominant_emotion') else '')
            chosen_emotion = st.text_input(
                'Emotion to use for MIDI generation', value=default_emotion)

            if st.button('Confirm and Generate'):
                if not chosen_emotion:
                    st.warning(
                        'Please enter or choose an emotion to generate.')
                else:
                    # generate files
                    midi_out = OUT / 'parsed_input.mid'
                    wav_out = OUT / 'parsed_input.wav'
                    code = run_cmd([shlex.split(sys.executable)[
                                   0], 'scripts/tonecore_midi.py', '--emotion', chosen_emotion, '--out', str(midi_out)])
                    if code != 0:
                        st.error('MIDI generation failed')
                    else:
                        if not sf2_path:
                            st.error(
                                'Soundfont not found and fallback download failed')
                        else:
                            rc = run_cmd(['fluidsynth', '-ni', str(sf2_path),
                                         str(midi_out), '-F', str(wav_out), '-r', '44100'])
                            if rc == 0 and wav_out.exists():
                                st.audio(str(wav_out))
                            else:
                                st.error('Rendering failed')
