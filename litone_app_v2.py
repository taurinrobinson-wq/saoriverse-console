import streamlit as st

# MUST be first Streamlit call, before all other imports
st.set_page_config(page_title="LiToneCheck", layout="wide")

import os
from dotenv import load_dotenv
from litone.core import (
    split_sentences, detect_tone, shift_tone, map_slider_to_tone, TONES,
    classify_sentence_structure, assess_overall_message, get_active_tools
)

load_dotenv(dotenv_path="LiToneCheck.env")

st.title("LiToneCheck — Interactive Tone Shifter for Legal Correspondence")

# Try to import the project's richer signal parser if available
HAS_PARSE_INPUT = False
parse_input = None
try:
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

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings & Tools")
    
    # Tone selector with labels
    st.subheader("Target Tone")
    tone_names_display = {
        0: "Very Formal 📋",
        1: "Formal 📝",
        2: "Neutral ➖",
        3: "Friendly 😊",
        4: "Empathetic 🤝",
    }
    tone_idx = st.radio(
        "Select target tone for transformation:",
        options=[0, 1, 2, 3, 4],
        format_func=lambda x: tone_names_display[x],
        horizontal=False,
    )
    target_tone = map_slider_to_tone(tone_idx)
    st.write(f"**Selected:** {target_tone}")
    
    # API/Tool Status
    st.subheader("🛠️ Tools & APIs")
    use_sapling = bool(os.environ.get("SAPLING_API_KEY"))
    st.write(f"**Sapling API:** {'✅ Configured' if use_sapling else '❌ Not configured'}")
    st.write(f"**Signal Parser:** {'✅ Available' if HAS_PARSE_INPUT else '❌ Not available'}")
    
    # Show which NLP tools are active (will update after analysis)
    st.subheader("📊 NLP Engines")
    col1, col2, col3 = st.columns(3)
    col1.write("**NRC**")
    col2.write("**spaCy**")
    col3.write("**TextBlob**")

# Main text input
text = st.text_area("📄 Paste or type your legal correspondence:", height=200, key="main_text")

# Submit button
col1, col2 = st.columns([3, 1])
with col2:
    submit_button = st.button("🔄 Analyze & Transform", type="primary")

if not text.strip():
    st.info("👉 Enter your correspondence above and click 'Analyze & Transform' to begin.")
    st.stop()

if not submit_button:
    st.stop()

# ============ ANALYSIS ============
sentences = split_sentences(text)
tones = [detect_tone(s) for s in sentences]
structures = [classify_sentence_structure(s) for s in sentences]
overall_assessment = assess_overall_message(sentences, tones)

# Get which tools were actually used
active_tools = get_active_tools()

# ============ TRANSFORMED TEXT SECTION (FIRST) ============
st.subheader("✨ Transformed Text")
transformed_sentences = [shift_tone(s, target_tone) for s in sentences]
transformed_full = " ".join(transformed_sentences)
st.text_area("Output:", value=transformed_full, height=200, disabled=True, key="output_text")

# Copy button
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    st.download_button(
        label="📋 Copy to Clipboard",
        data=transformed_full,
        file_name="transformed_text.txt",
        mime="text/plain",
    )

# ============ OVERALL ASSESSMENT ============
st.subheader(f"📊 Overall Message Assessment: **{overall_assessment}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Sentences", len(sentences))
with col2:
    tone_distribution = {}
    for tone in tones:
        tone_distribution[tone] = tone_distribution.get(tone, 0) + 1
    dominant_tone = max(tone_distribution, key=tone_distribution.get)
    st.metric("Dominant Tone", dominant_tone)
with col3:
    st.metric("Target Tone", target_tone)

# ============ DETAILED ANALYSIS (IN EXPANDER) ============
with st.expander("🔍 Sentence Tone & Structural Analysis"):
    st.subheader("Sentence-by-Sentence Breakdown")
    
    analysis_data = []
    for i, (original, tone, structure, transformed) in enumerate(
        zip(sentences, tones, structures, transformed_sentences), 1
    ):
        analysis_data.append({
            "Sentence": i,
            "Original": original,
            "Detected Tone": tone,
            "Structure": structure,
            "Transformed": transformed,
        })
    
    for row in analysis_data:
        with st.container(border=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write(f"**Sentence {row['Sentence']}**")
                st.write(f"📍 **Structure:** {row['Structure']}")
                st.write(f"🎯 **Detected Tone:** {row['Detected Tone']}")
            
            with col2:
                st.write(f"**Original:**")
                st.write(row['Original'])
            
            st.write(f"**Transformed to {target_tone}:**")
            st.write(row['Transformed'])
    
    # NLP Tools used
    st.divider()
    st.subheader("🛠️ NLP Tools Used in This Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**NRC Lexicon:** {'✅ Used' if active_tools['nrc'] else '❌ Not used'}")
    with col2:
        st.write(f"**spaCy:** {'✅ Used' if active_tools['spacy'] else '❌ Not used'}")
    with col3:
        st.write(f"**TextBlob:** {'✅ Used' if active_tools['textblob'] else '❌ Not used'}")

st.divider()
st.caption("💡 **LiToneCheck** helps you adapt your legal correspondence to different audiences. Experiment with different target tones to find the right voice for your recipient.")
