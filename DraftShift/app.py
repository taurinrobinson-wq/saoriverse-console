import streamlit as st
from pathlib import Path
import sys
import os

# Add parent directory to Python path to enable imports
# This allows the app to run from both the repo root and the DraftShift directory
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Debug: Log Python path for troubleshooting
if os.environ.get("DEBUG_DRAFTSHIFT"):
    print(f"DraftShift Debug Info:")
    print(f"  __file__: {__file__}")
    print(f"  repo_root: {repo_root}")
    print(f"  sys.path: {sys.path[:5]}")  # Show first 5 entries

# MUST be first Streamlit call, before all other imports
# Set favicon using the DraftShift logo
logo_path = Path(__file__).parent / "logo.svg"
st.set_page_config(
    page_title="DraftShift", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Interactive Tone Shifter for Legal Correspondence"
    }
)

from dotenv import load_dotenv

# Import DraftShift modules
try:
    from DraftShift.core import (
        split_sentences, detect_tone, shift_tone, map_slider_to_tone, TONES,
        classify_sentence_structure, assess_overall_message, get_active_tools, get_tool_status
    )
    from DraftShift.llm_transformer import get_transformer
    from DraftShift.civility_scorer import get_scorer
    from DraftShift.risk_alerts import get_alert_generator
except ImportError as e:
    st.error(f"❌ Failed to import DraftShift modules: {e}")
    st.error(f"Current working directory: {os.getcwd()}")
    st.error(f"Python path includes: {repo_root}")
    st.info("💡 Make sure you're running this app from the repository root or that all dependencies are installed.")
    st.stop()

# Locate .env at repo root if present, otherwise fallback to cwd
env_path = repo_root / "LiToneCheck.env"
if not env_path.exists():
    env_path = Path.cwd() / "LiToneCheck.env"

# Load environment variables
load_dotenv(dotenv_path=str(env_path))

# Debug: Show .env file status
if os.environ.get("DEBUG_DRAFTSHIFT"):
    if env_path.exists():
        print(f"  .env loaded from: {env_path}")
    else:
        print(f"  .env not found at: {env_path}")
        print(f"  Note: .env file is optional. App will work without it.")

# Display logo and title
col1, col2 = st.columns([1, 10])
with col1:
    if logo_path.exists():
        st.image(str(logo_path), width=60, use_column_width=False)
    else:
        st.write("📋")
with col2:
    st.title("Interactive Tone Shifter for Legal Correspondence")

# Try to import the project's richer signal parser if available (optional dependency)
HAS_PARSE_INPUT = False
parse_input = None
parse_error = None
parse_error_details = []

try:
    from src.emotional_os.core.signal_parser import parse_input as _parse_input
    parse_input = _parse_input
    HAS_PARSE_INPUT = True
except ImportError as e1:
    parse_error_details.append(f"src.emotional_os.core: {str(e1)}")
    try:
        from emotional_os.core.signal_parser import parse_input as _parse_input
        parse_input = _parse_input
        HAS_PARSE_INPUT = True
    except ImportError as e2:
        parse_error_details.append(f"emotional_os.core: {str(e2)}")
        # signal_parser is optional - the app will work without it
        parse_error = "Signal parser module is not available (optional feature)"
        HAS_PARSE_INPUT = False
except Exception as e:
    parse_error = f"Unexpected error loading signal parser: {type(e).__name__}: {str(e)}"
    HAS_PARSE_INPUT = False

# Get tool status for sidebar
tool_status = get_tool_status()

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
    st.write(f"**Signal Parser:** {'✅ Available' if HAS_PARSE_INPUT else '⚠️ Not available (optional)'}")
    if parse_error and os.environ.get("DEBUG_DRAFTSHIFT"):
        with st.expander("Parser Debug Details (optional feature)"):
            st.info(parse_error)
            if parse_error_details:
                st.write("Import attempts:")
                for detail in parse_error_details:
                    st.text(detail)
    
    # Show which NLP tools are active (will update after analysis)
    st.subheader("📊 NLP Engines")
    nrc_status = "✅" if tool_status["nrc"]["loaded"] else "❌"
    spacy_status = "✅" if tool_status["spacy"]["loaded"] else "❌"
    textblob_status = "✅" if tool_status["textblob"]["loaded"] else "❌"
    
    col1, col2, col3 = st.columns(3)
    col1.write(f"**NRC** {nrc_status}")
    col2.write(f"**spaCy** {spacy_status}")
    col3.write(f"**TextBlob** {textblob_status}")
    
    # Show errors if any
    if tool_status["nrc"]["error"] or tool_status["spacy"]["error"] or tool_status["textblob"]["error"]:
        with st.expander("Tool Load Errors"):
            if tool_status["nrc"]["error"]:
                st.error(f"**NRC:** {tool_status['nrc']['error']}")
            if tool_status["spacy"]["error"]:
                st.error(f"**spaCy:** {tool_status['spacy']['error']}")
            if tool_status["textblob"]["error"]:
                st.error(f"**TextBlob:** {tool_status['textblob']['error']}")

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

# ============ CIVILITY SCORING (Phase 1.2) ============
scorer = get_scorer()
civility_assessment = scorer.score_document(sentences, tones, structures=structures)

# ============ RISK ALERTS (Phase 1.3) ============
alert_generator = get_alert_generator()
risk_report = alert_generator.scan_document(sentences, tones)

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

col1, col2, col3, col4 = st.columns(4)
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
with col4:
    # Civility score (0-100)
    civility_score = civility_assessment['score']
    # Color code the civility score
    if civility_score >= 85:
        color = "🟢"
    elif civility_score >= 70:
        color = "🟡"
    elif civility_score >= 55:
        color = "🟠"
    else:
        color = "🔴"
    st.metric("Civility Score", f"{color} {civility_score}/100")

# ============ RISK ALERTS SECTION (Phase 1.3) ============
if risk_report['alerts_total'] > 0:
    st.divider()
    st.subheader("⚠️ Civility Alerts")
    
    # Overall recommendation
    recommendation_text = risk_report['overall_recommendation']
    if "DO NOT SEND" in recommendation_text:
        st.error(recommendation_text)
    elif "HIGH RISK" in recommendation_text:
        st.warning(recommendation_text)
    elif "MODERATE" in recommendation_text:
        st.warning(recommendation_text)
    else:
        st.success(recommendation_text)
    
    # Alert counts
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if risk_report['critical_count'] > 0:
            st.metric("🔴 Critical", risk_report['critical_count'])
    with col2:
        if risk_report['high_count'] > 0:
            st.metric("🟠 High", risk_report['high_count'])
    with col3:
        medium_count = len(risk_report['alerts_by_severity']['medium'])
        if medium_count > 0:
            st.metric("🟡 Medium", medium_count)
    with col4:
        st.metric("Total Alerts", risk_report['alerts_total'])
    
    # Show critical alerts inline
    if risk_report['alerts_by_severity']['critical']:
        st.subsubheader("Critical Issues")
        for alert in risk_report['alerts_by_severity']['critical']:
            with st.container(border=True):
                st.error(f"**{alert['message']}**")
                if alert['snippet']:
                    st.code(alert['snippet'], language="text")
                if alert['suggestion']:
                    st.write(f"💡 {alert['suggestion']}")
    
    # Expandable high/medium alerts
    if risk_report['alerts_by_severity']['high'] or risk_report['alerts_by_severity']['medium']:
        with st.expander("View High & Medium Priority Alerts"):
            for alert in risk_report['alerts_by_severity']['high']:
                with st.container(border=True):
                    st.warning(f"**{alert['message']}**")
                    if alert['snippet']:
                        st.code(alert['snippet'], language="text")
                    if alert['suggestion']:
                        st.write(f"💡 {alert['suggestion']}")
            
            for alert in risk_report['alerts_by_severity']['medium']:
                with st.container(border=True):
                    st.info(f"**{alert['message']}**")
                    if alert['snippet']:
                        st.code(alert['snippet'], language="text")
                    if alert['suggestion']:
                        st.write(f"💡 {alert['suggestion']}")
else:
    st.divider()
    st.success("✅ No civility alerts detected.")

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
st.caption("💡 **DraftShift** helps you adapt your legal correspondence to different audiences. Experiment with different target tones to find the right voice for your recipient.")
