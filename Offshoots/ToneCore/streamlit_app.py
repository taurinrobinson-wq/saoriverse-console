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
import sys as _sys
from pathlib import Path
import subprocess
import shlex
import sys
import urllib.request
import json
import shutil
import os
import hashlib
from urllib.parse import urlparse
import streamlit as st
import logging
import time
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

# Ensure the repository root is on sys.path so imports like
# `from emotional_os.core.signal_parser import parse_input` work when
# Streamlit runs the script from an isolated working directory.
if str(ROOT) not in _sys.path:
    _sys.path.insert(0, str(ROOT))


# Configure a lightweight logger for debugging long-running requests
LOG_FILE = OUT / 'tonecore_debug.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('tonecore')

# Fallback download URL for a small General MIDI soundfont (TimGM6mb - ~6MB)
FALLBACK_SF2_URL = 'https://github.com/urish/sf2/raw/master/TimGM6mb.sf2'

# Optional environment variable to point to a hosted SF2 (CDN or GitHub release)
# Example: export TONECORE_SF2_URL="https://cdn.example.com/FluidR3_GM.sf2"
SF2_ENV_URL = os.environ.get('TONECORE_SF2_URL')


def is_valid_sf2(path: Path) -> bool:
    """Quick check whether a file looks like a SoundFont (RIFF header).

    It's a lightweight validation used before attempting to call fluidsynth.
    """
    try:
        with open(path, 'rb') as fh:
            hdr = fh.read(4)
            return hdr == b'RIFF'
    except Exception:
        return False


def download_sf2(url: str, dest: Path) -> bool:
    """Download an SF2 from `url` to `dest`. Returns True on success."""
    tmp = dest.with_suffix('.tmp')
    try:
        with urllib.request.urlopen(url, timeout=30) as resp, open(tmp, 'wb') as out:
            shutil.copyfileobj(resp, out)

        # If a SHA256 is provided, validate the download before moving into place
        expected_hash = os.getenv('TONECORE_SF2_SHA256')
        if expected_hash:
            h = hashlib.sha256()
            with open(tmp, 'rb') as fh:
                for chunk in iter(lambda: fh.read(8192), b''):
                    h.update(chunk)
            actual_hash = h.hexdigest()
            if actual_hash.lower() != expected_hash.lower():
                logger.warning(
                    'SF2 hash mismatch: expected %s, got %s', expected_hash, actual_hash)
                try:
                    tmp.unlink()
                except Exception:
                    pass
                return False

        # quick validation
        if not is_valid_sf2(tmp):
            logger.warning(
                'Downloaded file does not appear to be a valid SF2: %s', tmp)
            try:
                tmp.unlink()
            except Exception:
                pass
            return False

        # move into place atomically
        tmp.replace(dest)
        logger.info('Downloaded and stored SF2 at %s', dest)
        return True
    except Exception as e:
        logger.exception('Failed to download SF2 from %s: %s', url, e)
        try:
            tmp.unlink()
        except Exception:
            pass
        return False


def run_cmd(cmd):
    """Run a command and capture output; log start/end and returncode."""
    try:
        cmd_display = ' '.join(cmd)
    except Exception:
        cmd_display = str(cmd)
    st.write('> ' + cmd_display)
    logger.info('run_cmd start: %s', cmd_display)
    start = time.time()
    try:
        # Allow a configurable timeout to avoid long-running/hung commands
        default_timeout = int(os.getenv('TONECORE_CMD_TIMEOUT', '30'))
        res = subprocess.run(cmd, cwd=str(
            ROOT), capture_output=True, text=True, timeout=default_timeout)
        duration = time.time() - start
        logger.info('run_cmd end: %s rc=%s dur=%.2fs',
                    cmd_display, res.returncode, duration)
        if res.stdout:
            logger.debug('stdout: %s', res.stdout[:400])
        if res.stderr:
            logger.debug('stderr: %s', res.stderr[:800])
        return res.returncode
    except subprocess.TimeoutExpired as e:
        duration = time.time() - start
        logger.warning('run_cmd timeout after %.2fs: %s',
                       duration, cmd_display)
        try:
            # best-effort: kill the process group if any
            if hasattr(e, 'pid') and e.pid:
                import psutil
                try:
                    p = psutil.Process(e.pid)
                    for child in p.children(recursive=True):
                        child.kill()
                    p.kill()
                except Exception:
                    pass
        except Exception:
            pass
        return 124
    except Exception as e:
        logger.exception('run_cmd exception: %s', e)
        return 255


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
        # Prefer an explicit CDN/release URL if provided via env
        preferred = SF2_ENV_URL or FALLBACK_SF2_URL
        dest = SF2

        # If a valid SF2 already exists at the destination, return it
        if dest.exists() and is_valid_sf2(dest):
            logger.info('Existing SF2 found and valid at %s', dest)
            return dest

        # Try to download from preferred URL
        st.info(f'Downloading fallback soundfont to {dest}...')
        ok = download_sf2(preferred, dest)
        if ok:
            return dest

        # If preferred failed and it wasn't the fallback URL, try the fallback
        if preferred != FALLBACK_SF2_URL:
            logger.info('Preferred SF2 URL failed; trying fallback URL')
            ok2 = download_sf2(FALLBACK_SF2_URL, dest)
            if ok2:
                return dest

        return None
    except Exception as e:
        st.warning(f'Could not obtain fallback soundfont: {e}')
        return None


def map_enhanced_to_emotion(parsed: dict, enhanced: dict) -> tuple[str, str]:
    """Map parser signals + enhanced NLP output to a richer emotion label.

    Returns (emotion_label, rationale_string).
    This is heuristic: it combines parser 'tone' tags (e.g., 'love', 'intimacy')
    with NRC counts and TextBlob polarity to pick a user-friendly label such
    as 'longing', 'intimacy', 'joy', or 'sadness'.
    """
    # Defaults
    try:
        tones = set()
        for s in (parsed.get('signals') or []):
            t = s.get('tone')
            if t:
                tones.add(str(t).lower())
    except Exception:
        tones = set()

    nrc = enhanced.get('nrc_emotions') if enhanced else {}
    if not isinstance(nrc, dict):
        nrc = {}
    # pick numeric counts (fall back to 0)

    def n(name):
        try:
            return float(nrc.get(name, 0) or 0)
        except Exception:
            return 0.0

    joy = n('joy')
    sadness = n('sadness')
    trust = n('trust')
    surprise = n('surprise')
    positive = n('positive')
    polarity = 0.0
    try:
        polarity = float((enhanced.get('textblob_sentiment')
                         or {}).get('polarity', 0) or 0)
    except Exception:
        polarity = 0.0

    rationale_parts = []

    # If parser tone explicitly signals intimacy or love, prefer nuanced labels
    if 'intimacy' in tones:
        rationale_parts.append('parser detected "intimacy" tone')
        # if sadness also present -> longing / nostalgia
        if sadness > 0 and joy > 0:
            rationale_parts.append(
                'mixed joy+sadness in NRC -> selecting "longing"')
            return 'longing', '; '.join(rationale_parts)
        return 'intimacy', '; '.join(rationale_parts)

    if 'love' in tones:
        rationale_parts.append('parser detected "love" tone')
        if sadness > 0 and joy > 0:
            rationale_parts.append(
                'mixed joy+sadness in NRC -> selecting "longing"')
            return 'longing', '; '.join(rationale_parts)
        if sadness > joy:
            rationale_parts.append('sadness > joy -> selecting "longing"')
            return 'longing', '; '.join(rationale_parts)
        if joy >= sadness and polarity > 0.2:
            rationale_parts.append(
                'positive polarity with dominant joy -> selecting "joy"')
            return 'joy', '; '.join(rationale_parts)

    # If NRC shows both joy and sadness signals, prefer 'longing' (bittersweet)
    if joy > 0 and sadness > 0:
        rationale_parts.append(
            'NRC includes both joy and sadness -> selecting "longing"')
        return 'longing', '; '.join(rationale_parts)

    # If sadness dominates, pick sadness/nostalgia
    if sadness > max(joy, trust, surprise) and sadness > 0:
        rationale_parts.append('sadness dominates NRC -> selecting "sadness"')
        return 'sadness', '; '.join(rationale_parts)

    # If trust or positive dominates, pick contentment/positive
    if positive >= max(joy, sadness, trust) and positive > 0:
        rationale_parts.append(
            'NRC positive dominates -> selecting "contentment"')
        return 'contentment', '; '.join(rationale_parts)

    # Fall back to enhanced dominant_emotion if present
    dom = (enhanced.get('dominant_emotion') if enhanced else None)
    if dom:
        rationale_parts.append(
            f'falling back to enhanced dominant_emotion: {dom}')
        return str(dom), '; '.join(rationale_parts)

    # Final fallback
    rationale_parts.append('no clear signal; defaulting to "neutral"')
    return 'neutral', '; '.join(rationale_parts)


def map_signals_to_music(parsed: dict, enhanced: dict, mapped_emotion: str) -> dict:
    """Map parser signals and enhanced output into musical controls.

    Returns a dict with keys:
      - emotion: mapped emotion label
      - velocity_min, velocity_max: ints for MIDI velocity range
      - chord_length_beats: int
      - acc_program, lead_program: optional GM program numbers
      - reverb: int (0-127) to indicate reverb amount
      - rhythm_profile: str (one of 'sparse','moderate','dense')
      - post_reverb: bool (whether to apply ffmpeg reverb)
    """
    controls = {
        'emotion': mapped_emotion or 'neutral',
        'velocity_min': 48,
        'velocity_max': 88,
        'chord_length_beats': 4,
        'acc_program': 0,
        'lead_program': 40,
        'reverb': 48,
        'rhythm_profile': 'moderate',
        'post_reverb': False,
    }

    # Aggregate voltage from parser signals (use mean or max)
    try:
        voltages = []
        for s in (parsed.get('signals') or []):
            v = s.get('voltage')
            if isinstance(v, (int, float)):
                voltages.append(float(v))
            elif isinstance(v, str):
                # map textual voltages to numeric scale if possible
                lv = v.lower()
                if lv == 'low':
                    voltages.append(0.25)
                elif lv == 'medium':
                    voltages.append(0.5)
                elif lv == 'high':
                    voltages.append(0.9)
    except Exception:
        voltages = []

    avg_v = float(sum(voltages) / len(voltages)) if voltages else 0.5

    # Map voltage to velocity range and sustain behavior
    if avg_v < 0.33:
        controls['velocity_min'] = 36
        controls['velocity_max'] = 64
        controls['chord_length_beats'] = 6
    elif avg_v < 0.66:
        controls['velocity_min'] = 54
        controls['velocity_max'] = 88
        controls['chord_length_beats'] = 4
    else:
        controls['velocity_min'] = 84
        controls['velocity_max'] = 110
        controls['chord_length_beats'] = 3

    # Map gates to rhythm profile and harmonic density
    gates = parsed.get('gates') or []
    # default rhythmic density
    density = 'moderate'
    if any(str(g).endswith('4') or str(g).lower().find('grief') != -1 for g in gates):
        density = 'sparse'
    if any(str(g).endswith('6') or str(g).lower().find('urgency') != -1 for g in gates):
        density = 'dense'
    if any(str(g).endswith('9') or str(g).lower().find('reflection') != -1 for g in gates):
        density = 'irregular'
    controls['rhythm_profile'] = density

    # Map mapped_emotion to program numbers & reverb defaults (GM program numbers)
    me = (mapped_emotion or '').lower()
    if me == 'longing':
        # strings / warm pad + choir option
        controls['acc_program'] = 48  # strings ensemble
        controls['lead_program'] = 52  # choir Aahs (ethereal) or 40 cello
        controls['reverb'] = 96
        controls['post_reverb'] = True
        controls['chord_length_beats'] = max(controls['chord_length_beats'], 6)
    elif me == 'intimacy':
        controls['acc_program'] = 0  # piano
        controls['lead_program'] = 40
        controls['reverb'] = 100
        controls['post_reverb'] = True
    elif me == 'joy':
        controls['acc_program'] = 0
        controls['lead_program'] = 24  # acoustic guitar (pluck)
        controls['reverb'] = 36
    elif me == 'sadness':
        controls['acc_program'] = 48
        controls['lead_program'] = 42
        controls['reverb'] = 110
        controls['post_reverb'] = True

    # Respect any strong NRC polarity hints: if polarity strongly positive, bias velocities up
    try:
        polarity = float((enhanced.get('textblob_sentiment')
                         or {}).get('polarity', 0) or 0)
        if polarity > 0.4:
            controls['velocity_min'] = min(controls['velocity_min'] + 6, 127)
            controls['velocity_max'] = min(controls['velocity_max'] + 10, 127)
        elif polarity < -0.3:
            controls['velocity_min'] = max(8, controls['velocity_min'] - 8)
            controls['velocity_max'] = max(16, controls['velocity_max'] - 12)
    except Exception:
        pass

    return controls


st.title('ToneCore Demo Player')

sf2_path = ensure_soundfont()
logger.info('startup: sf2_path=%s', str(sf2_path))

st.markdown("""
Enter text(multi-line). The app will parse the input using the project's
signal parsers and generate a MIDI progression based on the glyphs found.
""")

user_text = st.text_area('Input text', value='', height=160)

# When the user clicks 'Generate & Render' we compute parser + enhanced
# analysis and persist results into `st.session_state` so they survive
# the rerun triggered by clicking 'Confirm and Generate'.
if st.button('Generate & Render'):
    if not user_text.strip():
        st.warning('Please enter some text to analyze.')
    else:
        logger.info('Generate & Render clicked; input_len=%d', len(user_text))
        # 1) Run the base parser to find glyphs/signals
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
            # store parser results in session_state
            st.session_state['tonecore_parsed'] = parsed

            # 2) Run enhanced NLP analysis (NRC + TextBlob + spaCy)
            with st.spinner('Running enhanced NLP analysis (NRC + TextBlob + spaCy)...'):
                logger.info('Starting enhanced NLP analysis')
                try:
                    from parser.enhanced_emotion_processor import EnhancedEmotionProcessor
                    eproc = EnhancedEmotionProcessor()
                    enhanced = eproc.analyze_emotion_comprehensive(user_text)
                except Exception as e:
                    st.error(f'Enhanced analysis failed: {e}')
                    enhanced = None

            st.session_state['tonecore_enhanced'] = enhanced
            # compute a mapped emotion label from parser+enhanced results
            try:
                mapped, rationale = map_enhanced_to_emotion(
                    st.session_state.get('tonecore_parsed', {}), enhanced or {})
                st.session_state['tonecore_mapped_emotion'] = mapped
                st.session_state['tonecore_mapped_rationale'] = rationale
            except Exception:
                st.session_state['tonecore_mapped_emotion'] = None
                st.session_state['tonecore_mapped_rationale'] = None
            # Compute music controls and store them
            try:
                music_controls = map_signals_to_music(st.session_state.get('tonecore_parsed', {
                }), enhanced or {}, st.session_state.get('tonecore_mapped_emotion'))
                st.session_state['tonecore_music_controls'] = music_controls
            except Exception:
                st.session_state['tonecore_music_controls'] = None

# If we have analysis results in session_state, display them and allow
# the user to confirm the emotion and trigger generation.
if st.session_state.get('tonecore_parsed'):
    parsed = st.session_state.get('tonecore_parsed')
    st.subheader('Signal Parser Results')
    st.write('Signals:', parsed.get('signals'))
    st.write('Gates:', parsed.get('gates'))

    enhanced = st.session_state.get('tonecore_enhanced')
    if enhanced:
        st.subheader('Enhanced Analysis')
        st.write('NRC emotions:', enhanced.get('nrc_emotions'))
        st.write('TextBlob sentiment:', enhanced.get('textblob_sentiment'))
        st.write('spaCy syntax:', enhanced.get('spacy_syntax'))
        st.write('Dominant emotion:', enhanced.get('dominant_emotion'),
                 'confidence:', enhanced.get('confidence'))
        st.write('Recommended gates:', enhanced.get('recommended_gates'))
        st.write('Enhanced signals:', enhanced.get('enhanced_signals'))

    # Let the user confirm the emotion to use (default to mapped emotion)
    default_emotion = ''
    if st.session_state.get('tonecore_mapped_emotion'):
        default_emotion = st.session_state.get('tonecore_mapped_emotion')
        # show the rationale to the user
        rationale = st.session_state.get('tonecore_mapped_rationale')
        if rationale:
            st.caption(f'Emotion mapping rationale: {rationale}')
    elif enhanced and enhanced.get('dominant_emotion'):
        default_emotion = enhanced.get('dominant_emotion')

    # Use a session_state-backed text_input so the value survives reruns
    chosen_emotion = st.text_input(
        'Emotion to use for MIDI generation', value=default_emotion, key='tonecore_chosen_emotion')

    if st.button('Confirm and Generate', key='confirm_generate'):
        chosen_emotion = st.session_state.get(
            'tonecore_chosen_emotion', '').strip()
        logger.info(
            'Confirm and Generate clicked; chosen_emotion=%s', chosen_emotion)
        if not chosen_emotion:
            st.warning('Please enter or choose an emotion to generate.')
        else:
            # generate files
            midi_out = OUT / 'parsed_input.mid'
            wav_out = OUT / 'parsed_input.wav'

            # If music controls are available, write them to a JSON and pass to the MIDI generator
            controls_path = None
            if st.session_state.get('tonecore_music_controls'):
                try:
                    controls_path = OUT / 'tonecore_controls.json'
                    controls_path.write_text(json.dumps(
                        st.session_state['tonecore_music_controls']), encoding='utf8')
                except Exception:
                    controls_path = None

            cmd = [shlex.split(sys.executable)[0], 'scripts/tonecore_midi.py',
                   '--emotion', chosen_emotion, '--out', str(midi_out)]
            if controls_path:
                cmd += ['--controls', str(controls_path)]

            code = run_cmd(cmd)
            if code != 0:
                st.error('MIDI generation failed')
            else:
                if not sf2_path:
                    st.error('Soundfont not found and fallback download failed')
                else:
                    rc = run_cmd(['fluidsynth', '-ni', str(sf2_path),
                                 str(midi_out), '-F', str(wav_out), '-r', '44100'])
                    if rc == 0 and wav_out.exists():
                        final_wav = wav_out
                        # Optional post-processing: apply a subtle reverb using ffmpeg if requested
                        controls = st.session_state.get(
                            'tonecore_music_controls') or {}
                        if controls.get('post_reverb') and shutil.which('ffmpeg'):
                            try:
                                reverb_amt = int(controls.get('reverb', 48))
                                # map reverb_amt (0-127) to aecho params
                                in_wav = str(wav_out)
                                out_wav = str(OUT / 'parsed_input_reverb.wav')
                                # aecho parameters: in_gain:out_gain:delays:decays
                                # use delay proportional to reverb_amt
                                delay = max(200, int(reverb_amt * 8))
                                decay = min(0.9, 0.3 + (reverb_amt / 512.0))
                                ff_cmd = ['ffmpeg', '-y', '-i', in_wav, '-af',
                                          f"aecho=0.8:0.9:{delay}:{decay}", out_wav]
                                run_cmd(ff_cmd)
                                if Path(out_wav).exists():
                                    final_wav = Path(out_wav)
                            except Exception:
                                final_wav = wav_out

                        st.audio(str(final_wav))
                    else:
                        st.error('Rendering failed')
