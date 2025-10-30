import streamlit as st
import docx
import time
import requests
import datetime
import json
from .auth import SaoynxAuthentication
from .doc_export import generate_doc


def inject_css(css_file_path):
    try:
        with open(css_file_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_file_path}")
    except Exception as e:
        st.warning(f"Could not load CSS: {e}")

def render_controls_row(conversation_key):
    controls = st.columns([2, 1, 1, 1, 1, 1])
    with controls[0]:
        if 'processing_mode' not in st.session_state:
            st.session_state.processing_mode = "hybrid"
        processing_mode = st.selectbox(
            "Processing Mode",
            ["hybrid", "local", "ai_preferred"],
            index=["hybrid", "local", "ai_preferred"].index(st.session_state.processing_mode),
            help="Hybrid: Best performance, Local: Maximum privacy, AI: Most sophisticated responses",
            key="mode_select_row"
        )
        st.session_state.processing_mode = processing_mode
    with controls[1]:
        theme_default = 0 if st.session_state.get("theme_select_row", "Light") == "Light" else 1
        st.selectbox("Theme", ["Light", "Dark"], index=theme_default, key="theme_select_row")
    with controls[2]:
        if "show_debug" not in st.session_state:
            st.session_state.show_debug = False
        if st.button("Debug", key="debug_toggle_row"):
            st.session_state.show_debug = not st.session_state.show_debug
            st.rerun()
    with controls[3]:
        if st.button("Clear History", type="secondary", key="clear_history_btn_row"):
            st.session_state[conversation_key] = []
            st.rerun()
    with controls[4]:
        if st.button("Download My Data", type="secondary", key="download_btn_row"):
            user_data = {
                "user_id": st.session_state.user_id,
                "username": st.session_state.username,
                "conversations": st.session_state[conversation_key],
                "export_date": datetime.datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON",
                json.dumps(user_data, indent=2),
                file_name=f"emotional_os_data_{st.session_state.username}_{datetime.datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    with controls[5]:
        if st.button("Start Personal Log", key="start_log_btn"):
            st.session_state.show_personal_log = True
            st.rerun()

# UI rendering functions

def render_splash_interface(auth):
    inject_css("emotional_os/deploy/emotional_os_ui.css")
    st.markdown('<div style="text-align: center; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            st.image("graphics/FirstPerson-Logo.svg", width=200)
        except:
            st.markdown('''
            <div style="font-size: 4rem;">🧠</div>
            <div style="font-size: 2rem; font-weight: 300; letter-spacing: 4px; color: #2E2E2E; margin: 0.5rem 0 0.2rem 0;">FirstPerson</div>
            <div style="font-size: 1rem; color: #666; letter-spacing: 2px; font-weight: 300; text-transform: uppercase;">Personal AI<br>Companion</div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.get('show_login', False):
        auth.render_login_form()
    elif st.session_state.get('show_register', False):
        auth.render_register_form()
    else:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            qcol1, qcol2 = st.columns([1, 1], gap="small")
            with qcol1:
                st.markdown('<div class="auth-question">existing user?</div>', unsafe_allow_html=True)
            with qcol2:
                st.markdown('<div class="auth-question">new user?</div>', unsafe_allow_html=True)
            bcol1, bcol2 = st.columns([1, 1], gap="small")
            with bcol1:
                if st.button("Sign In", key="existing_btn"):
                    st.session_state.show_login = True
                    st.rerun()
            with bcol2:
                if st.button("Register Now", key="new_btn"):
                    st.session_state.show_register = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="quick-access">', unsafe_allow_html=True)
        st.markdown('<div class="quick-title">Quick Access</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⚡ Demo Mode", help="Try the system instantly"):
                auth.quick_login_bypass()
        st.markdown('</div>', unsafe_allow_html=True)

def render_main_app():
    # (Simple chat history example removed; only advanced chat/conversation system remains)
    # Dynamically inject theme CSS
    theme = st.session_state.get("theme_select_row", "Light")
    css_file = "emotional_os/deploy/emotional_os_ui_light.css" if theme == "Light" else "emotional_os/deploy/emotional_os_ui_dark.css"
    inject_css(css_file)
    # Logo switching based on theme
    if theme == "Dark":
        logo_path = "static/graphics/FirstPerson-Logo(invert-cropped_notext).svg"
    else:
        logo_path = "static/graphics/FirstPerson-Logo(black-cropped_notext).svg"
    col1, col2 = st.columns([0.5, 8], gap="small")
    with col1:
        try:
            st.image(logo_path, width=50)
        except:
            st.markdown('<div style="font-size: 2.5rem; margin: 0; line-height: 1;">🧠</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<h1 style="margin: 0; margin-left: -35px; padding-top: 10px; color: #2E2E2E; font-weight: 300; letter-spacing: 2px; font-size: 2.2rem;">FirstPerson - Personal AI Companion</h1>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 0.8rem; color: #999;'>Theme: {theme}</div>", unsafe_allow_html=True)
    st.markdown("*Your private space for emotional processing and growth*")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"Welcome back, **{st.session_state.username}**! 👋")
    with col2:
        pass  # Settings panel now in sidebar expander
    with col3:
        if st.button("Logout", help="Sign out of your account"):
            from .auth import SaoynxAuthentication
            auth = SaoynxAuthentication()
            auth.logout()
    conversation_key = f"conversation_history_{st.session_state.user_id}"
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = []
    # Set processing_mode in session and local variable for use below
    render_controls_row(conversation_key)
    processing_mode = st.session_state.get('processing_mode', 'hybrid')
    chat_container = st.container()
    with chat_container:
        for i, exchange in enumerate(st.session_state[conversation_key]):
            with st.chat_message("user"):
                st.write(exchange["user"])
            with st.chat_message("assistant"):
                st.write(exchange["assistant"])
                if "processing_time" in exchange:
                    st.caption(f"Processed in {exchange['processing_time']} • Mode: {exchange.get('mode', 'unknown')}")
    # 1. Show a single message at the top if a document is uploaded and being processed
    document_analysis = None
    document_title = None
    if "uploaded_text" in st.session_state:
        import spacy
        import nltk
        from nltk.corpus import wordnet as wn
        import json
        from pathlib import Path
        # Load spaCy model
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            st.error("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
            nlp = None
        # Load NLTK WordNet
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        doc_text = st.session_state["uploaded_text"]
        first_line = doc_text.split("\n", 1)[0]
        document_title = "Document" if not first_line else first_line[:60]
        summary = ""
        entities = []
        legal_definitions = {}
        # Summarization (optional, using transformers if available)
        try:
            from transformers import pipeline
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
            summary = summarizer(doc_text[:2000], max_length=120, min_length=30, do_sample=False)[0]['summary_text']
        except ImportError:
            summary = "(Summarization model not available. Install 'transformers' and download a local model for full support.)"
        except Exception:
            summary = "(Summarization failed due to an unexpected error.)"
        # Entity extraction (spaCy)
        if nlp:
            doc = nlp(doc_text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
        # Legal dictionary lookup (custom JSON/CSV)
        legal_dict_path = Path("velonix_lexicon.json")
        if legal_dict_path.exists():
            with open(legal_dict_path, "r", encoding="utf-8") as f:
                legal_dict = json.load(f)
            for word in set(doc_text.split()):
                if word.lower() in legal_dict:
                    legal_definitions[word] = legal_dict[word.lower()]
        # WordNet definitions
        for word in set(doc_text.split()):
            syns = wn.synsets(word)
            if syns:
                definition = getattr(syns[0], "definition", None)
                if callable(definition):
                    legal_definitions[word] = definition()
        with st.expander(f"Document Analysis: {document_title}", expanded=True):
            st.markdown(f"**Summary:**\n{summary}")
            st.markdown("**Entities:**")
            for ent, label in entities:
                st.write(f"- {ent} ({label})")
            if legal_definitions:
                st.markdown("**Legal Definitions / WordNet:**")
                for word, definition in legal_definitions.items():
                    st.write(f"- {word}: {definition}")
    uploaded_file = st.file_uploader("📄 Upload a document", type=["txt", "docx", "pdf"])
    if uploaded_file:
        file_text = None
        if uploaded_file.name.lower().endswith(".txt"):
            file_text = uploaded_file.read().decode("utf-8", errors="ignore")
        elif uploaded_file.name.lower().endswith(".docx"):
            try:
                import docx
                doc = docx.Document(uploaded_file)
                file_text = "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                st.error(f"Error reading Word document: {e}")
        elif uploaded_file.name.lower().endswith(".pdf"):
            try:
                import pdfplumber
                with pdfplumber.open(uploaded_file) as pdf:
                    file_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            except Exception as e:
                st.error(f"Error reading PDF document: {e}")
        if file_text:
            st.session_state["uploaded_text"] = file_text
            st.success("Document uploaded successfully!")

    user_input = st.chat_input("Share what you're feeling...")
    debug_signals = []
    debug_gates = []
    debug_glyphs = []
    debug_sql = ""
    debug_glyph_rows = []
    if user_input:
        # Always set debug info defaults
        debug_signals = []
        debug_gates = []
        debug_glyphs = []
        debug_sql = ""
        debug_glyph_rows = []
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Processing your emotional input..."):
                    start_time = time.time()
                    response = ""
                    if processing_mode == "local":
                        from emotional_os.glyphs.signal_parser import parse_input
                        local_analysis = parse_input(user_input, "emotional_os/parser/signal_lexicon.json", db_path="emotional_os/glyphs/glyphs.db")
                        glyphs = local_analysis.get("glyphs", [])
                        voltage_response = local_analysis.get("voltage_response", "")
                        ritual_prompt = local_analysis.get("ritual_prompt", "")
                        debug_signals = local_analysis.get("signals", [])
                        debug_gates = local_analysis.get("gates", [])
                        debug_glyphs = glyphs
                        debug_sql = local_analysis.get("debug_sql", "")
                        debug_glyph_rows = local_analysis.get("debug_glyph_rows", [])
                        best_glyph = local_analysis.get("best_glyph")
                        glyph_display = best_glyph['glyph_name'] if best_glyph else 'None'
                        response = f"{voltage_response}\n\nResonant Glyph: {glyph_display}"
                    elif processing_mode == "ai_preferred":
                        try:
                            saori_url = st.secrets.get("supabase", {}).get("saori_function_url")
                            supabase_key = st.secrets.get("supabase", {}).get("key")
                            if not saori_url or not supabase_key:
                                response = "AI processing unavailable in demo mode. Your feelings are still valid and important."
                            else:
                                payload = {
                                    "message": user_input,
                                    "mode": processing_mode,
                                    "user_id": st.session_state.user_id
                                }
                                if document_analysis:
                                    glyphs = document_analysis.get("glyphs", [])
                                    voltage_response = document_analysis.get("voltage_response", "")
                                    ritual_prompt = document_analysis.get("ritual_prompt", "")
                                    debug_signals = document_analysis.get("signals", [])
                                    debug_gates = document_analysis.get("gates", [])
                                    debug_glyphs = glyphs
                                    doc_context = "\n".join([
                                        f"Document Insights: {voltage_response}",
                                        f"Activated Glyphs: {', '.join([g['glyph_name'] for g in glyphs])}" if glyphs and isinstance(glyphs, list) else "",
                                        f"Ritual Prompt: {ritual_prompt}" if ritual_prompt else ""
                                    ])
                                    payload["document_context"] = doc_context
                                response_data = requests.post(
                                    saori_url,
                                    headers={
                                        "Authorization": f"Bearer {supabase_key}",
                                        "Content-Type": "application/json"
                                    },
                                    json=payload,
                                    timeout=15
                                )
                                if response_data.status_code == 200:
                                    result = response_data.json()
                                    response = result.get("reply", "I'm here to listen.")
                                else:
                                    response = "I'm experiencing some technical difficulties, but I'm still here for you."
                        except Exception as e:
                            response = "I'm having trouble connecting right now, but your feelings are still valid and important."
                    elif processing_mode == "hybrid":
                        from emotional_os.glyphs.signal_parser import parse_input
                        local_analysis = parse_input(user_input, "emotional_os/parser/signal_lexicon.json", db_path="emotional_os/glyphs/glyphs.db")
                        glyphs = local_analysis.get("glyphs", [])
                        voltage_response = local_analysis.get("voltage_response", "")
                        ritual_prompt = local_analysis.get("ritual_prompt", "")
                        debug_signals = local_analysis.get("signals", [])
                        debug_gates = local_analysis.get("gates", [])
                        debug_glyphs = glyphs
                        debug_sql = local_analysis.get("debug_sql", "")
                        debug_glyph_rows = local_analysis.get("debug_glyph_rows", [])
                        try:
                            saori_url = st.secrets.get("supabase", {}).get("saori_function_url")
                            supabase_key = st.secrets.get("supabase", {}).get("key")
                            if not saori_url or not supabase_key:
                                response = f"Local Analysis: {voltage_response}\nActivated Glyphs: {', '.join([g['glyph_name'] for g in glyphs]) if glyphs else 'None'}\n{ritual_prompt}\n(AI enhancement unavailable in demo mode)"
                            else:
                                payload = {
                                    "message": user_input,
                                    "mode": processing_mode,
                                    "user_id": st.session_state.user_id,
                                    "local_voltage_response": voltage_response,
                                    "local_glyphs": ', '.join([g['glyph_name'] for g in glyphs]) if glyphs else '',
                                    "local_ritual_prompt": ritual_prompt
                                }
                                if document_analysis:
                                    doc_glyphs = document_analysis.get("glyphs", [])
                                    doc_voltage_response = document_analysis.get("voltage_response", "")
                                    doc_ritual_prompt = document_analysis.get("ritual_prompt", "")
                                    debug_signals = document_analysis.get("signals", [])
                                    debug_gates = document_analysis.get("gates", [])
                                    debug_glyphs = doc_glyphs
                                    doc_context = "\n".join([
                                        f"Document Insights: {doc_voltage_response}",
                                        f"Activated Glyphs: {', '.join([g['glyph_name'] for g in doc_glyphs])}" if doc_glyphs and isinstance(doc_glyphs, list) else "",
                                        f"Ritual Prompt: {doc_ritual_prompt}" if doc_ritual_prompt else ""
                                    ])
                                    payload["document_context"] = doc_context
                                response_data = requests.post(
                                    saori_url,
                                    headers={
                                        "Authorization": f"Bearer {supabase_key}",
                                        "Content-Type": "application/json"
                                    },
                                    json=payload,
                                    timeout=15
                                )
                                if response_data.status_code == 200:
                                    result = response_data.json()
                                    response = result.get("reply", "I'm here to listen.")
                                else:
                                    response = "I'm experiencing some technical difficulties, but I'm still here for you."
                        except Exception as e:
                            response = f"Local Analysis: {voltage_response}\nActivated Glyphs: {', '.join([g['glyph_name'] for g in glyphs]) if glyphs else 'None'}\n{ritual_prompt}\nAI error: {e}"
                    else:
                        response = "Unknown processing mode."
                    processing_time = time.time() - start_time
                    st.write(response)
                    st.caption(f"Processed in {processing_time:.2f}s • Mode: {processing_mode}")
        # Always show debug expander if toggled, regardless of mode
        if st.session_state.get("show_debug", False):
            with st.expander("Debug: Emotional OS Activation Details", expanded=True):
                st.write("**Signals Detected:**", debug_signals)
                st.write("**Gates Activated:**", debug_gates)
                st.write("**Glyphs Matched:**", debug_glyphs)
                st.write("**Raw SQL Query:**", debug_sql)
                st.write("**Glyph Rows (Raw):**", debug_glyph_rows)
        st.session_state[conversation_key].append({
            "user": user_input,
            "assistant": response,
            "processing_time": f"{processing_time:.2f}s",
            "mode": processing_mode,
            "timestamp": datetime.datetime.now().isoformat()
        })
        st.rerun()
    if "show_personal_log" not in st.session_state:
        st.session_state.show_personal_log = False
    if st.session_state.show_personal_log:
        import datetime as dt
        st.markdown("### 📘 Journal & Self-Care Center")
        journal_type = st.selectbox(
            "Choose Journal Type",
            [
                "Personal Log",
                "Daily Emotional Check-In",
                "Self-Care Tracker",
                "Micro-Boundary Ritual",
                "Reflective Journal"
            ],
            key="journal_type_select"
        )
        if journal_type == "Personal Log":
            st.markdown("Use this space to record a structured emotional entry. You'll log the date, event, mood, reflections, and insights.")
            date = st.date_input("Date", value=dt.date.today())
            log_time = st.time_input("Time", value=dt.datetime.now().time())
            event = st.text_area("Event", placeholder="What happened?")
            mood = st.text_input("Mood", placeholder="How did it feel?")
            reflections = st.text_area("Reflections", placeholder="What’s emerging emotionally?")
            insights = st.text_area("Insights", placeholder="What truth or clarity surfaced?")
            if st.button("Conclude Log"):
                st.success("Your personal log has been saved.")
                try:
                    st.download_button(
                        label="Download as Word Doc",
                        data=generate_doc(date, log_time, event, mood, reflections, insights),
                        file_name="personal_log.docx"
                    )
                except Exception as e:
                    st.error(f"Error generating Word document: {e}")
        elif journal_type == "Daily Emotional Check-In":
            st.markdown("Log your mood, stress level, and a short reflection for today.")
            checkin_date = st.date_input("Date", value=dt.date.today(), key="checkin_date")
            mood = st.selectbox("Mood", ["Calm", "Stressed", "Sad", "Angry", "Joyful", "Fatigued", "Other"], key="checkin_mood")
            stress = st.slider("Stress Level", 0, 10, 5, key="checkin_stress")
            reflection = st.text_area("Reflection", placeholder="What's on your mind today?", key="checkin_reflection")
            if st.button("Save Check-In"):
                st.success("Your daily check-in has been saved.")
        elif journal_type == "Self-Care Tracker":
            st.markdown("Track your self-care activities and routines.")
            activities = st.multiselect(
                "Self-Care Activities",
                ["Exercise", "Creative Work", "Peer Support", "Rest", "Healthy Meal", "Time Outdoors", "Other"],
                key="selfcare_activities"
            )
            notes = st.text_area("Notes", placeholder="Any details or thoughts about your self-care today?", key="selfcare_notes")
            if st.button("Save Self-Care Entry"):
                st.success("Your self-care entry has been saved.")
        elif journal_type == "Micro-Boundary Ritual":
            st.markdown("Mark a transition between work and personal time.")
            ritual_type = st.selectbox("Ritual Type", ["Change Location", "Wash Hands", "Listen to Music", "Short Walk", "Other"], key="ritual_type")
            ritual_notes = st.text_area("Ritual Notes", placeholder="How did this ritual help you shift gears?", key="ritual_notes")
            if st.button("Log Ritual"):
                st.success("Your boundary ritual has been logged.")
        elif journal_type == "Reflective Journal":
            st.markdown("Write about your own reactions, growth, and challenges. No client details—just your personal journey.")
            journal_date = st.date_input("Date", value=dt.date.today(), key="reflective_date")
            entry = st.text_area("Reflection Entry", placeholder="What's emerging for you emotionally or personally?", key="reflective_entry")
            if st.button("Save Reflection"):
                st.success("Your reflection has been saved.")
        if st.button("Close Journal Center"):
            st.session_state.show_personal_log = False
            st.rerun()
        else:
            st.info("You can continue adding to this log.")
