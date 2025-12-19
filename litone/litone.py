import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from draftshift.core import split_sentences, detect_tone, shift_tone, map_slider_to_tone, TONES

# Locate .env at repo root if present, otherwise fallback to cwd
repo_root = Path(__file__).resolve().parents[1]
env_path = repo_root / "LiToneCheck.env"
if not env_path.exists():
    env_path = Path.cwd() / "LiToneCheck.env"
load_dotenv(dotenv_path=str(env_path))

st.set_page_config(title="LiToneCheck", layout="wide")

st.title("DraftShift — interactive sentence tone inspector")

# Try to import the project's richer signal parser if available
HAS_PARSE_INPUT = False
parse_input = None
try:
    # Preferred import path used in the repo
    from src.emotional_os.core.signal_parser import parse_input as _parse_input
    parse_input = _parse_input
    HAS_PARSE_INPUT = True
except Exception:
    try:
        from emotional_os.core.signal_parser import parse_input as _parse_input
        parse_input = _parse_input
        HAS_PARSE_INPUT = True
    except Exception:
        HAS_PARSE_INPUT = False

with st.sidebar:
    st.header("Settings")
    tone_idx = st.slider("Target tone", 0, len(TONES) - 1, 2)
    target_tone = map_slider_to_tone(tone_idx)
    use_api = bool(os.environ.get("SAPLING_API_KEY"))
    st.write("Sapling API configured:" , "Yes" if use_api else "No")
    st.write("Signal parser available:", "Yes" if HAS_PARSE_INPUT else "No")

text = st.text_area("Enter text to analyze", height=250)

if not text.strip():
    st.info("Paste or type text above to analyze sentence tones and shift tone via the slider.")
    st.stop()

sentences = split_sentences(text)

st.subheader("Detected sentence tones and transformations")
for i, s in enumerate(sentences):
    tone = detect_tone(s)
    transformed = shift_tone(s, target_tone)
    cols = st.columns([7, 1, 4, 3])
    cols[0].write(s)
    cols[1].markdown(f"**{tone}**")
    cols[2].write(transformed)

    # If we have a richer parser, show signals/glyphs for each sentence
    if HAS_PARSE_INPUT:
        try:
            parsed = parse_input(s, lexicon_path="emotional_os/parser/signal_lexicon.json")
            signals = parsed.get("signals") or []
            glyphs = parsed.get("glyphs") or []
            cols[3].write(f"Signals: {', '.join([str(x.get('signal') or x.get('keyword') or '') for x in signals])}")
        except Exception:
            cols[3].write("Parser error")

st.subheader("Full transformed text")
transformed_full = " ".join(shift_tone(s, target_tone) for s in sentences)
st.text_area("Transformed output", value=transformed_full, height=200)

st.markdown("---")
st.markdown("**Notes:** This app uses a lightweight heuristic fallback for tone detection and transformation. It can optionally use the repo's `parse_input` signal parser if available, and will use `SAPLING_API_KEY`/`SAPLING_API_URL` for Sapling calls when configured.")
