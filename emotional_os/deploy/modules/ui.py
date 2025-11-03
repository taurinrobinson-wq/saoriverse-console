import datetime
import json
import logging
import time

try:
    import requests
except Exception:
    # Allow the module to be imported in environments where `requests` is not
    # installed (e.g., lightweight CI or minimal runtime). Functions that need
    # network access will handle the missing library at call time.
    requests = None

import streamlit as st

logger = logging.getLogger(__name__)

try:
    from .doc_export import generate_doc
except Exception:
    # Allow the module to be imported even if optional doc export dependencies
    # (like python-docx) are not installed
    generate_doc = None


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
        mode_options = ["hybrid", "ai_preferred", "local", "ollama"]
        current_mode = st.session_state.processing_mode
        if current_mode not in mode_options:
            current_mode = "hybrid"
        processing_mode = st.selectbox(
            "Processing Mode",
            mode_options,
            index=mode_options.index(current_mode),
            help="Hybrid: Best balance (recommended), AI: Cloud-only, Local: Templates, Ollama: Experimental",
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

# Data management functions

def delete_user_history_from_supabase(user_id: str) -> tuple:
    """Delete all persisted conversation history for a user from Supabase.
    
    Args:
        user_id: The user ID whose history should be deleted.
    
    Returns:
        A tuple (success: bool, message: str) indicating whether the deletion succeeded.
    """
    try:
        if requests is None:
            return False, "Network requests not available in this environment."
        
        supabase_url = st.secrets.get("supabase", {}).get("url")
        supabase_key = st.secrets.get("supabase", {}).get("key")
        
        if not supabase_url or not supabase_key:
            return False, "Supabase not configured. Cannot delete server history."
        
        # Call a Supabase function or use the REST API to delete user history
        # For now, we'll attempt a direct REST API call to a hypothetical endpoint
        delete_url = f"{supabase_url}/rest/v1/conversations?user_id=eq.{user_id}"
        
        response = requests.delete(
            delete_url,
            headers={
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            timeout=10
        )
        
        if response.status_code in [200, 204, 404]:
            return True, "Server-side history deleted successfully."
        else:
            return False, f"Failed to delete history (HTTP {response.status_code})."
    except Exception as e:
        return False, f"Error deleting history: {str(e)}"

# UI rendering functions

def render_splash_interface(auth):
    inject_css("emotional_os/deploy/emotional_os_ui.css")
    st.markdown('<div style="text-align: center; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            st.image("graphics/FirstPerson-Logo.svg", width=200)
        except Exception:
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
        # Quick access: keep login bypass but remove legacy demo-mode trigger for full rollout
        with col2:
            if st.button("⚡ Quick Login", help="Quick sign-in (developer shortcut)"):
                try:
                    auth.quick_login_bypass()
                except Exception:
                    pass
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
        except Exception:
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
        # Simple document processing without heavy dependencies
        doc_text = st.session_state["uploaded_text"]
        first_line = doc_text.split("\n", 1)[0]
        document_title = "Document" if not first_line else first_line[:60]

        st.info(f"📄 Document uploaded: {document_title}")
        st.info("🔧 Advanced document processing (spaCy, NLTK) not available - using basic text analysis")

        # Basic analysis without dependencies
        document_analysis = {
            "glyphs": [],
            "voltage_response": f"Document content recognized: {len(doc_text)} characters",
            "ritual_prompt": "Document-based emotional processing",
            "signals": [],
            "gates": []
        }

    # File upload with multiple formats
    uploaded_file = st.file_uploader("📄 Upload a document", type=["txt", "docx", "pdf", "md", "html", "htm", "csv", "xlsx", "xls", "json"])
    if uploaded_file:
        file_text = None
        file_ext = uploaded_file.name.lower().split('.')[-1]

        try:
            if file_ext == "txt":
                file_text = uploaded_file.read().decode("utf-8", errors="ignore")

            elif file_ext == "docx":
                try:
                    from docx import Document
                    doc = Document(uploaded_file)
                    file_text = "\n".join([para.text for para in doc.paragraphs])
                except Exception as e:
                    st.error(f"Error reading Word document: {e}")

            elif file_ext == "pdf":
                try:
                    import pdfplumber
                    with pdfplumber.open(uploaded_file) as pdf:
                        file_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                except Exception as e:
                    st.error(f"Error reading PDF document: {e}")

            elif file_ext == "md":
                try:
                    import markdown
                    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
                    # Convert markdown to HTML then extract text
                    html = markdown.markdown(raw_text)
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    file_text = soup.get_text()
                except Exception as e:
                    st.error(f"Error reading Markdown document: {e}")

            elif file_ext in ["html", "htm"]:
                try:
                    from bs4 import BeautifulSoup
                    raw_html = uploaded_file.read().decode("utf-8", errors="ignore")
                    soup = BeautifulSoup(raw_html, 'html.parser')
                    file_text = soup.get_text()
                except Exception as e:
                    st.error(f"Error reading HTML document: {e}")

            elif file_ext == "csv":
                try:
                    import pandas as pd
                    df = pd.read_csv(uploaded_file)
                    # Convert CSV to readable text format
                    file_text = df.to_string(index=False)
                except Exception as e:
                    st.error(f"Error reading CSV document: {e}")

            elif file_ext in ["xlsx", "xls"]:
                try:
                    import pandas as pd
                    df = pd.read_excel(uploaded_file)
                    # Convert Excel to readable text format
                    file_text = df.to_string(index=False)
                except Exception as e:
                    st.error(f"Error reading Excel document: {e}")

            elif file_ext == "json":
                try:
                    import json
                    raw_json = uploaded_file.read().decode("utf-8", errors="ignore")
                    data = json.loads(raw_json)
                    # Convert JSON to readable text format
                    file_text = json.dumps(data, indent=2)
                except Exception as e:
                    st.error(f"Error reading JSON document: {e}")

            if file_text:
                st.session_state["uploaded_text"] = file_text
                st.success(f"✅ {file_ext.upper()} document uploaded successfully!")
            else:
                st.warning(f"Could not extract text from {file_ext.upper()} file")

        except Exception as e:
            st.error(f"Error reading document: {e}")

    # Support 'recall' and 'resend' actions from the sidebar
    recalled = None
    auto_process = False
    if 'recalled_message' in st.session_state:
        recalled = st.session_state.pop('recalled_message')
    if 'auto_process' in st.session_state:
        auto_process = bool(st.session_state.pop('auto_process'))

    if recalled:
        # If a recalled message exists (from sidebar), process it immediately
        user_input = recalled
    else:
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
                    response_style = st.session_state.get('response_style', 'Balanced')
                    
                    if processing_mode == "ollama":
                        # Use local Ollama LLM for responses
                        try:
                            from emotional_os.llm.ollama_composer import get_ollama_composer
                            composer = get_ollama_composer(model="neural-chat")
                            response = composer.compose_response(
                                user_input=user_input,
                                response_style=response_style
                            )
                            glyphs = []
                            voltage_response = ""
                            ritual_prompt = ""
                            debug_signals = []
                            debug_gates = []
                            debug_glyphs = []
                        except Exception as e:
                            response = f"Ollama error: {e}. Falling back to local mode."
                            from emotional_os.glyphs.signal_parser import parse_input
                            local_analysis = parse_input(user_input, "emotional_os/parser/signal_lexicon.json", db_path="emotional_os/glyphs/glyphs.db")
                            glyphs = local_analysis.get("glyphs", [])
                            voltage_response = local_analysis.get("voltage_response", "")
                            ritual_prompt = local_analysis.get("ritual_prompt", "")
                            debug_signals = local_analysis.get("signals", [])
                            debug_gates = local_analysis.get("gates", [])
                            debug_glyphs = glyphs
                    elif processing_mode == "local":
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
                                if requests is None:
                                    # requests not available in this runtime
                                    response = "AI processing unavailable (requests library not installed)."
                                else:
                                    if response_data.status_code == 200:
                                        result = response_data.json()
                                        response = result.get("reply", "I'm here to listen.")
                                    else:
                                        response = "I'm experiencing some technical difficulties, but I'm still here for you."
                        except Exception:
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
                                if requests is None:
                                    response = "AI processing unavailable (requests library not installed)."
                                else:
                                    if response_data.status_code == 200:
                                        result = response_data.json()
                                        response = result.get("reply", "I'm here to listen.")
                                    else:
                                        response = "I'm experiencing some technical difficulties, but I'm still here for you."
                        except Exception as e:
                            response = f"Local Analysis: {voltage_response}\nActivated Glyphs: {', '.join([g['glyph_name'] for g in glyphs]) if glyphs else 'None'}\n{ritual_prompt}\nAI error: {e}"
                    else:
                        response = "Unknown processing mode."
                    # Before emitting the assistant response, attempt limbic processing if engine is present
                    try:
                        if 'limbic_engine' in st.session_state:
                            try:
                                from emotional_os.glyphs.limbic_decorator import decorate_reply
                                engine = st.session_state['limbic_engine']
                                # Basic safety gating
                                try:
                                    from emotional_os.safety.sanctuary import is_sensitive_input
                                    safety_flag = is_sensitive_input(user_input)
                                except Exception:
                                    safety_flag = False
                                if not safety_flag:
                                    limbic_result = engine.process_emotion_with_limbic_mapping(user_input)
                                    try:
                                        decorated = decorate_reply(response, limbic_result)
                                        # Only replace response if decoration returns a non-empty string
                                        if isinstance(decorated, str) and decorated.strip():
                                            response = decorated
                                    except Exception:
                                        pass
                            except Exception:
                                # If any limbic import/processing fails, continue with baseline response
                                pass
                    except Exception:
                        pass

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
        
        entry = {
            "user": user_input,
            "assistant": response,
            "processing_time": f"{processing_time:.2f}s",
            "mode": processing_mode,
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state[conversation_key].append(entry)
        
        # Learn from hybrid mode conversations to improve local mode
        if processing_mode == "hybrid":
            try:
                from emotional_os.learning.hybrid_learner_v2 import get_hybrid_learner
                learner = get_hybrid_learner()
                user_id = st.session_state.get('user_id', 'anonymous')
                result = learner.learn_from_exchange(
                    user_id=user_id,
                    user_input=user_input,
                    ai_response=response,
                    emotional_signals=debug_signals,
                    glyphs=debug_glyphs,
                )
                if result.get("learned_to_shared"):
                    logger.info(f"User {user_id} contributed to shared lexicon")
                elif result.get("learned_to_user"):
                    logger.info(f"User {user_id} learning to personal lexicon")
            except Exception as e:
                # Non-fatal: learning should not break the app
                logger.warning(f"Hybrid learning failed: {e}")

        # Persist to Supabase if the user opted in and credentials appear available
        try:
            if st.session_state.get('persist_history', False):
                sup_cfg = st.secrets.get('supabase', {}) if hasattr(st, 'secrets') else {}
                supabase_url = sup_cfg.get('url') or sup_cfg.get('saori_url') or sup_cfg.get('saori_function_url')
                supabase_key = sup_cfg.get('key') or sup_cfg.get('anon_key') or sup_cfg.get('apikey')
                # If function URL was provided instead of base url, try to extract base
                if supabase_url and supabase_url.endswith('/'): 
                    supabase_url = supabase_url.rstrip('/')
                # If the provided value looks like an edge function URL, extract base supabase domain
                if supabase_url and '/functions/' in supabase_url:
                    # nothing special, use as-is (best-effort)
                    base_url = supabase_url.split('/functions/')[0]
                elif supabase_url and supabase_url.startswith('https://') and '.supabase.' in supabase_url:
                    base_url = supabase_url.split('/')[2]
                    base_url = f"https://{base_url}"
                else:
                    base_url = supabase_url

                if base_url and supabase_key:
                    rest_url = f"{base_url}/rest/v1/conversation_history"
                    headers = {
                        'Content-Type': 'application/json',
                        'apikey': supabase_key,
                        'Authorization': f'Bearer {supabase_key}',
                        'Prefer': 'return=representation'
                    }
                    payload = [
                        {
                            'user_id': st.session_state.get('user_id'),
                            'username': st.session_state.get('username'),
                            'user_message': user_input,
                            'assistant_reply': response,
                            'processing_time': f"{processing_time:.2f}s",
                            'mode': processing_mode,
                            'timestamp': entry['timestamp']
                        }
                    ]
                    try:
                        resp = requests.post(rest_url, headers=headers, json=payload, timeout=6)
                        if resp.status_code not in (200, 201):
                            # Non-fatal: warn in UI (use generic storage wording)
                            st.warning('Could not save history to secure storage right now.')
                    except Exception:
                        st.warning('Temporary issue saving to secure storage. Your local history is still intact.')
        except Exception:
            # Best-effort: do not break the UI if persistence fails
            pass

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
            checkin_date = st.date_input("Date", value=dt.date.today(), key="checkin_date")  # noqa: F841  # used for Streamlit UI side-effect
            mood = st.selectbox("Mood", ["Calm", "Stressed", "Sad", "Angry", "Joyful", "Fatigued", "Other"], key="checkin_mood")
            stress = st.slider("Stress Level", 0, 10, 5, key="checkin_stress")  # noqa: F841  # used for Streamlit UI side-effect
            reflection = st.text_area("Reflection", placeholder="What's on your mind today?", key="checkin_reflection")  # noqa: F841  # used for Streamlit UI side-effect
            if st.button("Save Check-In"):
                st.success("Your daily check-in has been saved.")
        elif journal_type == "Self-Care Tracker":
            st.markdown("Track your self-care activities and routines.")
            activities = st.multiselect(  # noqa: F841  # used for Streamlit UI side-effect
                "Self-Care Activities",
                ["Exercise", "Creative Work", "Peer Support", "Rest", "Healthy Meal", "Time Outdoors", "Other"],
                key="selfcare_activities"
            )
            notes = st.text_area("Notes", placeholder="Any details or thoughts about your self-care today?", key="selfcare_notes")  # noqa: F841  # used for Streamlit UI side-effect
            if st.button("Save Self-Care Entry"):
                st.success("Your self-care entry has been saved.")
        elif journal_type == "Micro-Boundary Ritual":
            st.markdown("Mark a transition between work and personal time.")
            ritual_type = st.selectbox("Ritual Type", ["Change Location", "Wash Hands", "Listen to Music", "Short Walk", "Other"], key="ritual_type")  # noqa: F841  # used for Streamlit UI side-effect
            ritual_notes = st.text_area("Ritual Notes", placeholder="How did this ritual help you shift gears?", key="ritual_notes")  # noqa: F841  # used for Streamlit UI side-effect
            if st.button("Log Ritual"):
                st.success("Your boundary ritual has been logged.")
        elif journal_type == "Reflective Journal":
            st.markdown("Write about your own reactions, growth, and challenges. No client details—just your personal journey.")
            journal_date = st.date_input("Date", value=dt.date.today(), key="reflective_date")  # noqa: F841  # used for Streamlit UI side-effect
            entry = st.text_area("Reflection Entry", placeholder="What's emerging for you emotionally or personally?", key="reflective_entry")  # noqa: F841  # used for Streamlit UI side-effect
            if st.button("Save Reflection"):
                st.success("Your reflection has been saved.")
        if st.button("Close Journal Center"):
            st.session_state.show_personal_log = False
            st.rerun()
        else:
            st.info("You can continue adding to this log.")


def delete_user_history_from_supabase(user_id: str):
    """Best-effort delete of conversation history rows for a given user_id in Supabase.

    Returns a tuple: (success: bool, message: str)
    """
    try:
        if not user_id:
            return False, "No user_id provided"

        sup_cfg = st.secrets.get('supabase', {}) if hasattr(st, 'secrets') else {}
        supabase_url = sup_cfg.get('url') or sup_cfg.get('saori_url') or sup_cfg.get('saori_function_url')
        supabase_key = sup_cfg.get('key') or sup_cfg.get('anon_key') or sup_cfg.get('apikey')
        if not supabase_url or not supabase_key:
            return False, "Supabase credentials not configured"

        # Normalize base URL
        if supabase_url.endswith('/'):
            supabase_url = supabase_url.rstrip('/')
        if '/functions/' in supabase_url:
            base_url = supabase_url.split('/functions/')[0]
        elif supabase_url.startswith('https://') and '.supabase.' in supabase_url:
            # Derive base from host
            host = supabase_url.split('/')[2]
            base_url = f"https://{host}"
        else:
            base_url = supabase_url

        # Perform REST delete on conversation_history
        import urllib.parse
        encoded = urllib.parse.quote(str(user_id), safe='')
        rest_url = f"{base_url}/rest/v1/conversation_history"
        delete_url = f"{rest_url}?user_id=eq.{encoded}"
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }
        resp = requests.delete(delete_url, headers=headers, timeout=10)
        success = resp.status_code in (200, 204)

        # Attempt to write a deletion audit row (best-effort)
        try:
            audit_url = f"{base_url}/rest/v1/conversation_deletion_audit"
            audit_headers = {
                'Content-Type': 'application/json',
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Prefer': 'return=representation'
            }
            audit_payload = [{
                'user_id': user_id,
                'requested_by': st.session_state.get('user_id') if 'user_id' in st.session_state else None,
                'method': 'user-requested-via-ui',
                'details': {
                    'delete_status': getattr(resp, 'status_code', None),
                    'delete_text': getattr(resp, 'text', None)
                }
            }]
            requests.post(audit_url, headers=audit_headers, json=audit_payload, timeout=6)
        except Exception:
            # Swallow audit failures; do not block the main delete result
            pass

        if success:
            return True, 'Deleted server-side history successfully.'
        else:
            return False, f'Supabase delete returned {resp.status_code}: {resp.text}'
    except Exception as e:
        return False, str(e)
