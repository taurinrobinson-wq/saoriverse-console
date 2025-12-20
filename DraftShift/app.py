"""
DraftShift Streamlit Application - Interactive Tone Shifter for Legal Correspondence
"""

# -------------------------------------------------------------------
# ✅ PATH SETUP — MUST HAPPEN BEFORE ANY OTHER IMPORTS
# -------------------------------------------------------------------
import sys
import os
from pathlib import Path

# Safely resolve repo root (DraftShift/ is the folder containing this file)
try:
    current_file = Path(__file__).resolve()
    repo_root = current_file.parent.parent  # parent of DraftShift/
except Exception:
    # Streamlit Cloud sometimes strips __file__
    repo_root = Path.cwd()

# Add repo root to sys.path
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Debug mode
DEBUG_MODE = os.environ.get("DEBUG_DRAFTSHIFT", "").lower() in ("true", "1", "yes")

if DEBUG_MODE:
    print("=" * 80)
    print("DraftShift Startup - Path Configuration")
    print("=" * 80)
    print(f"Current working directory: {os.getcwd()}")
    print(f"Repo root: {repo_root}")
    print(f"Python path (first 5 entries):")
    for i, p in enumerate(sys.path[:5], 1):
        print(f"  {i}. {p}")
    print("=" * 80)

# -------------------------------------------------------------------
# ✅ STREAMLIT MUST BE IMPORTED AFTER PATH SETUP
# -------------------------------------------------------------------
import streamlit as st

# ✅ FIRST STREAMLIT CALL — MUST COME BEFORE ANY OTHER st.* CALLS
logo_path = Path(__file__).parent / "logo.svg"
st.set_page_config(
    page_title="DraftShift",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Interactive Tone Shifter for Legal Correspondence"},
)

# -------------------------------------------------------------------
# ✅ ENVIRONMENT VARIABLES
# -------------------------------------------------------------------
from dotenv import load_dotenv

env_path = repo_root / "LiToneCheck.env"
if not env_path.exists():
    env_path = Path.cwd() / "LiToneCheck.env"

load_dotenv(dotenv_path=str(env_path))

if DEBUG_MODE:
    print(f".env loaded from: {env_path if env_path.exists() else 'NOT FOUND'}")

# -------------------------------------------------------------------
# ✅ ERROR DISPLAY HELPER
# -------------------------------------------------------------------
def show_error_details(error_type: str, error_message: str) -> None:
    st.error(f"**Error details:** {error_type}: {error_message}")

# -------------------------------------------------------------------
# ✅ IMPORT DRAFTSHIFT MODULES
# -------------------------------------------------------------------
try:
    from DraftShift.core import (
        split_sentences,
        detect_tone,
        shift_tone,
        map_slider_to_tone,
        TONES,
        classify_sentence_structure,
        assess_overall_message,
        get_active_tools,
        get_tool_status,
    )

    from DraftShift.llm_transformer import get_transformer
    from DraftShift.civility_scorer import get_scorer
    from DraftShift.risk_alerts import get_alert_generator

except ImportError as e:
    st.error("❌ Failed to import DraftShift modules")
    show_error_details(type(e).__name__, str(e))

    st.subheader("🔍 Diagnostic Information")
    st.code(
        f"Working directory: {os.getcwd()}\n"
        f"Repo root: {repo_root}\n"
        f"sys.path (first 5):\n" +
        "\n".join(f"  {i}. {p}" for i, p in enumerate(sys.path[:5], 1)),
        language="text",
    )

    st.stop()

except Exception as e:
    st.error("❌ Unexpected error during import")
    show_error_details(type(e).__name__, str(e))
    st.stop()

# -------------------------------------------------------------------
# ✅ OPTIONAL: SIGNAL PARSER
# -------------------------------------------------------------------
HAS_PARSE_INPUT = False
parse_input = None
parse_error = None
parse_error_details = []

try:
    from src.emotional_os.core.signal_parser import parse_input as _parse_input
    parse_input = _parse_input
    HAS_PARSE_INPUT = True
except ImportError as e1:
    parse_error_details.append(f"src.emotional_os.core: {e1}")
    try:
        from emotional_os.core.signal_parser import parse_input as _parse_input
        parse_input = _parse_input
        HAS_PARSE_INPUT = True
    except ImportError as e2:
        parse_error_details.append(f"emotional_os.core: {e2}")
        parse_error = "Signal parser unavailable (optional)"
        HAS_PARSE_INPUT = False

# -------------------------------------------------------------------
# ✅ HEADER
# -------------------------------------------------------------------
col1, col2 = st.columns([1, 10])
with col1:
    if logo_path.exists():
        st.image(str(logo_path), width=140)
    else:
        st.write("📋")
with col2:
    # Smaller, subtler title to fit the header while keeping logo prominent
    st.markdown(
        "<h1 style='font-size:22px;margin:0;padding:0'>Interactive Tone Shifter for Legal Correspondence</h1>",
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# ✅ SIDEBAR
# -------------------------------------------------------------------
tool_status = get_tool_status()

with st.sidebar:
    st.header("⚙️ Settings & Tools")

    st.subheader("Target Tone")
    tone_names_display = {
        0: "Very Formal 📋",
        1: "Formal 📝",
        2: "Neutral ➖",
        3: "Friendly 😊",
        4: "Empathetic 🤝",
    }

    tone_idx = st.radio(
        "Select target tone:",
        options=[0, 1, 2, 3, 4],
        format_func=lambda x: tone_names_display[x],
    )
    target_tone = map_slider_to_tone(tone_idx)
    st.write(f"**Selected:** {target_tone}")

    st.subheader("🛠️ Tools & APIs")
    use_sapling = bool(os.environ.get("SAPLING_API_KEY"))
    if use_sapling:
        st.write("**Sapling API:** ✅ Configured")
    st.write(f"**Signal Parser:** {'✅ Available' if HAS_PARSE_INPUT else '⚠️ Not available'}")

    st.subheader("📊 NLP Engines")
    col1, col2, col3 = st.columns(3)
    col1.write(f"**NRC:** {'✅' if tool_status['nrc']['loaded'] else '❌'}")
    col2.write(f"**spaCy:** {'✅' if tool_status['spacy']['loaded'] else '❌'}")
    col3.write(f"**TextBlob:** {'✅' if tool_status['textblob']['loaded'] else '❌'}")

# -------------------------------------------------------------------
# ✅ MAIN INPUT
# -------------------------------------------------------------------
text = st.text_area("📄 Paste or type your legal correspondence:", height=200)

col1, col2 = st.columns([3, 1])
with col2:
    submit_button = st.button("🔄 Analyze & Transform", type="primary")

if not text.strip():
    st.info("👉 Enter your correspondence above and click Analyze.")
    st.stop()

if not submit_button:
    st.stop()

# -------------------------------------------------------------------
# ✅ ANALYSIS
# -------------------------------------------------------------------
sentences = split_sentences(text)
tones = [detect_tone(s) for s in sentences]
structures = [classify_sentence_structure(s) for s in sentences]
overall_assessment = assess_overall_message(sentences, tones)
active_tools = get_active_tools()

# Civility scoring
scorer = get_scorer()
civility_assessment = scorer.score_document(sentences, tones, structures=structures)

# Risk alerts
alert_generator = get_alert_generator()
risk_report = alert_generator.scan_document(sentences, tones)

# -------------------------------------------------------------------
# ✅ TRANSFORMED TEXT
# -------------------------------------------------------------------
st.subheader("✨ Transformed Text")
transformed_sentences = [shift_tone(s, target_tone) for s in sentences]
transformed_full = " ".join(transformed_sentences)

st.text_area("Output:", value=transformed_full, height=200, disabled=True)

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    st.download_button(
        label="📋 Copy to Clipboard",
        data=str(transformed_full),
        file_name="transformed_text.txt",
        mime="text/plain",
    )

# -------------------------------------------------------------------
# ✅ OVERALL ASSESSMENT
# -------------------------------------------------------------------
st.subheader(f"📊 Overall Message Assessment: **{overall_assessment}**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Sentences", len(sentences))
with col2:
    tone_distribution = {}
    for t in tones:
        tone_distribution[t] = tone_distribution.get(t, 0) + 1
    dominant_tone = max(tone_distribution, key=tone_distribution.get)
    st.metric("Dominant Tone", dominant_tone)
with col3:
    st.metric("Target Tone", target_tone)
with col4:
    civility_score = civility_assessment["score"]
    if civility_score >= 85:
        color = "🟢"
    elif civility_score >= 70:
        color = "🟡"
    elif civility_score >= 55:
        color = "🟠"
    else:
        color = "🔴"
    st.metric("Civility Score", f"{color} {civility_score}/100")

# -------------------------------------------------------------------
# ✅ RISK ALERTS
# -------------------------------------------------------------------
if risk_report["alerts_total"] > 0:
    st.divider()
    st.subheader("⚠️ Civility Alerts")

    recommendation_text = risk_report["overall_recommendation"]
    if "DO NOT SEND" in recommendation_text:
        st.error(recommendation_text)
    elif "HIGH RISK" in recommendation_text:
        st.warning(recommendation_text)
    elif "MODERATE" in recommendation_text:
        st.warning(recommendation_text)
    else:
        st.success(recommendation_text)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if risk_report["critical_count"] > 0:
            st.metric("🔴 Critical", risk_report["critical_count"])
    with col2:
        if risk_report["high_count"] > 0:
            st.metric("🟠 High", risk_report["high_count"])
    with col3:
        medium_count = len(risk_report["alerts_by_severity"]["medium"])
        if medium_count > 0:
            st.metric("🟡 Medium", medium_count)
    with col4:
        st.metric("Total Alerts", risk_report["alerts_total"])

    if risk_report["alerts_by_severity"]["critical"]:
        st.subheader("Critical Issues")
        for alert in risk_report["alerts_by_severity"]["critical"]:
            with st.container(border=True):
                st.error(f"**{alert['message']}**")
                if alert["snippet"]:
                    st.code(alert["snippet"], language="text")
                if alert["suggestion"]:
                    st.write(f"💡 {alert['suggestion']}")

    if risk_report["alerts_by_severity"]["high"] or risk_report["alerts_by_severity"]["medium"]:
        with st.expander("View High & Medium Priority Alerts"):
            for alert in risk_report["alerts_by_severity"]["high"]:
                with st.container(border=True):
                    st.warning(f"**{alert['message']}**")
                    if alert["snippet"]:
                        st.code(alert["snippet"], language="text")
                    if alert["suggestion"]:
                        st.write(f"💡 {alert['suggestion']}")

            for alert in risk_report["alerts_by_severity"]["medium"]:
                with st.container(border=True):
                    st.info(f"**{alert['message']}**")
                    if alert["snippet"]:
                        st.code(alert["snippet"], language="text")
                    if alert["suggestion"]:
                        st.write(f"💡 {alert['suggestion']}")
else:
    st.divider()
    st.success("✅ No civility alerts detected.")

# -------------------------------------------------------------------
# ✅ DETAILED ANALYSIS
# -------------------------------------------------------------------
with st.expander("🔍 Sentence Tone & Structural Analysis"):
    st.subheader("Sentence-by-Sentence Breakdown")

    for i, (original, tone, structure, transformed) in enumerate(
        zip(sentences, tones, structures, transformed_sentences), 1
    ):
        with st.container(border=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**Sentence {i}**")
                st.write(f"📍 **Structure:** {structure}")
                st.write(f"🎯 **Detected Tone:** {tone}")
            with col2:
                st.write("**Original:**")
                st.write(original)

            st.write(f"**Transformed to {target_tone}:**")
            st.write(transformed)

    st.divider()
    st.subheader("🛠️ NLP Tools Used")
    col1, col2, col3 = st.columns(3)
    col1.write(f"**NRC:** {'✅ Used' if active_tools['nrc'] else '❌'}")
    col2.write(f"**spaCy:** {'✅ Used' if active_tools['spacy'] else '❌'}")
    col3.write(f"**TextBlob:** {'✅ Used' if active_tools['textblob'] else '❌'}")

st.divider()
st.caption("💡 DraftShift helps you adapt your legal correspondence to different audiences.")
