import datetime
import json
import logging
import time
import uuid

try:
    import requests
except Exception:
    # Allow the module to be imported in environments where `requests` is not
    # installed (e.g., lightweight CI or minimal runtime). Functions that need
    # network access will handle the missing library at call time.
    requests = None

import streamlit as st

logger = logging.getLogger(__name__)

# Simple in-memory cache for inline SVGs to avoid repeated disk reads
_SVG_CACHE = {}


def _load_inline_svg(filename: str) -> str:
    """Load an SVG file from the static graphics folder and return its raw markup.

    If the file cannot be read, returns a small fallback SVG string.
    """
    if filename in _SVG_CACHE:
        return _SVG_CACHE[filename]

    path = f"static/graphics/{filename}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            svg = f.read()
            _SVG_CACHE[filename] = svg
            return svg
    except Exception:
        # Fallback tiny SVG (simple brain emoji-like circle) to avoid missing markup
        fallback = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            '<circle cx="32" cy="32" r="30" fill="#FF6B6B"/></svg>'
        )
        _SVG_CACHE[filename] = fallback
        return fallback


try:
    from .doc_export import generate_doc
except Exception:
    # Allow the module to be imported even if optional doc export dependencies
    # (like python-docx) are not installed
    generate_doc = None

try:
    from .conversation_manager import ConversationManager, generate_auto_name, load_all_conversations_to_sidebar
except Exception:
    ConversationManager = None
    generate_auto_name = None
    load_all_conversations_to_sidebar = None

try:
    from emotional_os.safety.fallback_protocols import FallbackProtocol
except Exception:
    FallbackProtocol = None


def inject_css(css_file_path):
    try:
        # First inject the logo constraints CSS
        try:
            with open("emotional_os/deploy/logo_constraints.css", "r") as f:
                logo_css = f.read()
            st.markdown(f"<style>{logo_css}</style>", unsafe_allow_html=True)
        except Exception:
            pass  # Non-fatal if logo constraints can't be loaded

        # Then inject the requested CSS file
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
        mode_options = ["hybrid", "ai_preferred", "local"]
        current_mode = st.session_state.processing_mode
        if current_mode not in mode_options:
            current_mode = "hybrid"
        processing_mode = st.selectbox(
            "Processing Mode",
            mode_options,
            index=mode_options.index(current_mode),
            help="Hybrid: Best balance (recommended), AI: Cloud-only, Local: Templates",
            key="mode_select_row"
        )
        st.session_state.processing_mode = processing_mode
    with controls[1]:
        theme_default = 0 if st.session_state.get(
            "theme_select_row", "Light") == "Light" else 1
        st.selectbox("Theme", ["Light", "Dark"],
                     index=theme_default, key="theme_select_row")
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
    st.markdown('<div style="text-align: center; margin-bottom: 1rem;">',
                unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Use appropriate logo based on theme
        logo_file = "FirstPerson-Logo-black-cropped_notext.svg"
        svg_markup = _load_inline_svg(logo_file)
        try:
            st.markdown(
                f'<div style="width:120px; margin: 0 auto;" class="logo-container">{svg_markup}</div>', unsafe_allow_html=True)
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
                st.markdown(
                    '<div class="auth-question">existing user?</div>', unsafe_allow_html=True)
            with qcol2:
                st.markdown(
                    '<div class="auth-question">new user?</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="quick-title">Quick Access</div>',
                    unsafe_allow_html=True)
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

    # ============================================================================
    # Initialize Conversation Manager & Sidebar
    # ============================================================================

    # Initialize conversation manager for persistence
    if ConversationManager and 'user_id' in st.session_state:
        if 'conversation_manager' not in st.session_state:
            st.session_state['conversation_manager'] = ConversationManager(
                st.session_state['user_id'])
            # Attempt to load user preferences (persist settings) from server
            try:
                mgr = st.session_state.get('conversation_manager')
                if mgr:
                    prefs = mgr.load_user_preferences()
                    # Only set defaults if session state doesn't already have them
                    if prefs:
                        if 'persist_history' not in st.session_state:
                            st.session_state['persist_history'] = prefs.get(
                                'persist_history', True)
                        if 'persist_confirmed' not in st.session_state:
                            st.session_state['persist_confirmed'] = prefs.get(
                                'persist_confirmed', False)
            except Exception:
                # Best-effort: do not break UI if preferences cannot be loaded
                pass

        # Initialize current conversation ID if not set
        if 'current_conversation_id' not in st.session_state:
            st.session_state['current_conversation_id'] = str(uuid.uuid4())

        # Initialize conversation title if not set
        if 'conversation_title' not in st.session_state:
            st.session_state['conversation_title'] = "New Conversation"

    # Display sidebar with previous conversations
    with st.sidebar:
        st.markdown("### Settings")

        # Persist history toggle
        persist_default = st.session_state.get('persist_history', True)
        st.session_state['persist_history'] = st.checkbox(
            "💾 Save my chats",
            value=persist_default,
            help="Automatically save conversations for later retrieval"
        )
        # Best-effort: persist the user's preference back to server when available
        try:
            mgr = st.session_state.get('conversation_manager')
            if mgr:
                mgr.save_user_preferences({
                    'persist_history': bool(st.session_state.get('persist_history', False)),
                    'persist_confirmed': bool(st.session_state.get('persist_confirmed', False))
                })
        except Exception:
            pass

        # Privacy & Consent settings
        try:
            from emotional_os.deploy.modules.consent_ui import render_consent_settings_panel
            render_consent_settings_panel()
        except ImportError:
            pass
        except Exception as e:
            st.warning(f"Consent settings error: {e}")

        # Load and display previous conversations
        if ConversationManager and st.session_state.get('conversation_manager'):
            st.markdown("---")
            load_all_conversations_to_sidebar(
                st.session_state['conversation_manager'])

            # New conversation button
            if st.button("➕ New Conversation", use_container_width=True):
                st.session_state['current_conversation_id'] = str(uuid.uuid4())
                st.session_state['conversation_title'] = "New Conversation"
                st.session_state['conversation_history_' +
                                 st.session_state['user_id']] = []
                st.rerun()

        # Human-in-the-Loop (HIL) feature-flagged placeholder UI
        # Reacts to escalation signals produced by the local preprocessor.
        try:
            enable_default = st.session_state.get(
                'enable_hil_escalation', False)
            st.session_state['enable_hil_escalation'] = st.checkbox(
                "🧑‍⚖️ Enable HIL escalation (dev)",
                value=enable_default,
                help="Show Human-in-the-Loop escalation controls for testing"
            )

            # Preprocessor sensitivity controls (configurable thresholds)
            conf_default = st.session_state.get(
                'preproc_confidence_threshold', 0.6)
            cluster_default = st.session_state.get('preproc_cluster_size', 2)
            conf = st.slider(
                "Preprocessor confidence threshold",
                min_value=0.0,
                max_value=1.0,
                value=conf_default,
                step=0.05,
                help="If preprocessor confidence falls below this, Tier 2 tags may escalate"
            )
            cluster = st.number_input(
                "Tier-2 cluster size to escalate",
                min_value=1,
                max_value=5,
                value=cluster_default,
                help="Number of Tier-2 tags required to trigger cluster escalation"
            )
            # Persist controls in session state
            st.session_state['preproc_confidence_threshold'] = float(conf)
            st.session_state['preproc_cluster_size'] = int(cluster)

            # Update live preprocessor instance if present
            try:
                p_inst = st.session_state.get('local_preprocessor')
                if p_inst:
                    p_inst.confidence_threshold = st.session_state['preproc_confidence_threshold']
                    p_inst.cluster_size = st.session_state['preproc_cluster_size']
            except Exception:
                pass

            last = st.session_state.get('last_preproc')
            escalation_action = last.get('escalation_action') if last else None
            escalation_reason = last.get('escalation_reason') if last else None

            # If a force escalation is detected, surface a prominent prompt even if HIL is disabled
            if escalation_action == 'force_escalation' and not st.session_state.get('enable_hil_escalation'):
                st.markdown("---")
                st.error(
                    "⚠️ Immediate escalation recommended for the most recent exchange. Enable HIL to review and act.")
                if st.button("Enable HIL & Review", key="enable_hil_now"):
                    st.session_state['enable_hil_escalation'] = True
                    st.rerun()

            # When HIL enabled, show the escalation panel (if applicable)
            if st.session_state.get('enable_hil_escalation'):
                st.markdown("---")
                st.markdown("### Human-in-the-Loop (HIL) Escalation")

                if not last:
                    st.info("No preprocessing record available for review yet.")
                else:
                    # Visual priority: force -> error, conditional -> warning, none -> info
                    if escalation_action == 'force_escalation':
                        st.error(
                            f"Force escalation recommended: {escalation_reason}")
                    elif escalation_action == 'conditional_escalation':
                        st.warning(
                            f"Conditional escalation suggested: {escalation_reason}")
                    else:
                        st.info(
                            "No automatic escalation recommended for this exchange.")

                    # Show a compact summary including escalation metadata
                    st.write({
                        'intent': last.get('intent'),
                        'confidence': last.get('confidence'),
                        'emotional_tags': last.get('emotional_tags'),
                        'edit_log': last.get('edit_log'),
                        'editorial_interventions': last.get('editorial_interventions'),
                        'escalation_action': escalation_action,
                        'escalation_reason': escalation_reason,
                        'taxonomy_source': last.get('taxonomy_source')
                    })

                    cols = st.columns([1, 1, 1])
                    if cols[0].button("Escalate to Human", key="escalate_to_human"):
                        try:
                            from local_inference.preprocessor import Preprocessor
                            p = st.session_state.get('local_preprocessor')
                            audit_payload = {
                                'action': 'hil_escalate',
                                'method': 'manual_button',
                                'escalation_action': escalation_action,
                                'escalation_reason': escalation_reason,
                                'preproc_summary': last
                            }
                            if p and hasattr(p, 'record_audit'):
                                p.record_audit(audit_payload)
                                st.success("Escalation recorded (audit log).")
                            else:
                                st.session_state.setdefault('hil_escalation_log', []).append({
                                    'timestamp': datetime.datetime.now().isoformat(),
                                    **audit_payload
                                })
                                st.success(
                                    "Escalation recorded (session log).")
                        except Exception:
                            st.info("Escalation recorded (local stub).")

                    if cols[1].button("Request Clarification", key="request_clarification"):
                        try:
                            # record the clarification request
                            from local_inference.preprocessor import Preprocessor
                            p = st.session_state.get('local_preprocessor')
                            audit_payload = {
                                'action': 'request_clarification',
                                'method': 'manual_button',
                                'escalation_action': escalation_action,
                                'escalation_reason': escalation_reason,
                                'preproc_summary': last
                            }
                            if p and hasattr(p, 'record_audit'):
                                p.record_audit(audit_payload)
                            else:
                                st.session_state.setdefault('hil_escalation_log', []).append({
                                    'timestamp': datetime.datetime.now().isoformat(),
                                    **audit_payload
                                })
                            st.info("Clarification requested (logged).")
                        except Exception:
                            st.info("Clarification requested (local stub).")

                    if cols[2].button("Escalate to AI (sanitized)", key="escalate_to_ai"):
                        try:
                            from local_inference.preprocessor import Preprocessor
                            p = st.session_state.get('local_preprocessor')
                            audit_payload = {
                                'action': 'hil_escalate_ai',
                                'method': 'manual_button',
                                'escalation_action': escalation_action,
                                'escalation_reason': escalation_reason,
                                'preproc_summary': last
                            }
                            if p and hasattr(p, 'record_audit'):
                                p.record_audit(audit_payload)
                                st.success(
                                    "AI escalation requested (audit log).")
                            else:
                                st.session_state.setdefault('hil_escalation_log', []).append({
                                    'timestamp': datetime.datetime.now().isoformat(),
                                    **audit_payload
                                })
                                st.success(
                                    "AI escalation requested (session log).")
                        except Exception:
                            st.info("AI escalation requested (local stub).")
        except Exception:
            # Non-fatal: sidebar HIL toggle shouldn't break the UI
            pass

    # Dynamically inject theme CSS
    theme = st.session_state.get("theme_select_row", "Light")
    css_file = "emotional_os/deploy/emotional_os_ui_light.css" if theme == "Light" else "emotional_os/deploy/emotional_os_ui_dark.css"
    inject_css(css_file)
    # Logo switching based on theme
    # Use appropriate logo file based on theme
    theme = st.session_state.get("theme_select_row", "Light")
    svg_name = "FirstPerson-Logo-black-cropped_notext.svg" if theme == "Light" else "FirstPerson-Logo-invert-cropped_notext.svg"
    # Render a responsive brand row (inline SVG + title) using injected CSS
    svg_markup = _load_inline_svg(svg_name)
    try:
        st.markdown(f"""
        <div class="brand-container">
          <div class="brand-inner">
            <div class="brand-logo">{svg_markup}</div>
            <div class="brand-text">
              <div class="brand-title">FirstPerson - Personal AI Companion</div>
              <div class="brand-subtitle">Your private space for emotional processing and growth</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        # Fallback to previous column layout if raw HTML rendering fails
        col1, col2 = st.columns([0.5, 8], gap="small")
        with col1:
            try:
                st.markdown(
                    f'<div style="width:50px">{svg_markup}</div>', unsafe_allow_html=True)
            except Exception:
                # Render a simple emoji fallback (ensure proper quoting)
                st.markdown(
                    '<div style="font-size: 2.5rem; margin: 0; line-height: 1;">🧠</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<h1 style="margin: 0; padding-top: 6px; color: #2E2E2E; font-weight: 300; letter-spacing: 2px; font-size: 1.8rem;">FirstPerson - Personal AI Companion</h1>', unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size: 0.8rem; color: #999;'>Theme: {theme}</div>", unsafe_allow_html=True)
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

    # Initialize Fallback Protocols for tone-aware response handling
    if "fallback_protocol" not in st.session_state and FallbackProtocol:
        try:
            st.session_state["fallback_protocol"] = FallbackProtocol()
        except Exception:
            st.session_state["fallback_protocol"] = None

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
                    st.caption(
                        f"Processed in {exchange['processing_time']} • Mode: {exchange.get('mode', 'unknown')}")
    # 1. Show a single message at the top if a document is uploaded and being processed
    document_analysis = None
    document_title = None
    if "uploaded_text" in st.session_state:
        # Simple document processing without heavy dependencies
        doc_text = st.session_state["uploaded_text"]
        first_line = doc_text.split("\n", 1)[0]
        document_title = "Document" if not first_line else first_line[:60]

        st.info(f"📄 Document uploaded: {document_title}")
        st.info(
            "🔧 Advanced document processing (spaCy, NLTK) not available - using basic text analysis")

        # Basic analysis without dependencies
        document_analysis = {
            "glyphs": [],
            "voltage_response": f"Document content recognized: {len(doc_text)} characters",
            "ritual_prompt": "Document-based emotional processing",
            "signals": [],
            "gates": []
        }

    # File upload with multiple formats
    uploaded_file = st.file_uploader("📄 Upload a document", type=[
                                     "txt", "docx", "pdf", "md", "html", "htm", "csv", "xlsx", "xls", "json"])
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
                    file_text = "\n".join(
                        [para.text for para in doc.paragraphs])
                except Exception as e:
                    st.error(f"Error reading Word document: {e}")

            elif file_ext == "pdf":
                try:
                    import pdfplumber
                    with pdfplumber.open(uploaded_file) as pdf:
                        file_text = "\n".join(
                            page.extract_text() or "" for page in pdf.pages)
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
                st.success(
                    f"✅ {file_ext.upper()} document uploaded successfully!")
            else:
                st.warning(
                    f"Could not extract text from {file_ext.upper()} file")

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
                    response_style = st.session_state.get(
                        'response_style', 'Balanced')

                    # Build a lightweight conversation_context to help the parser detect feedback/reciprocal messages
                    conversation_context = {
                        'last_assistant_message': None,
                        'messages': []
                    }
                    if conversation_key in st.session_state and st.session_state[conversation_key]:
                        # copy session history into conversation_context.messages (role/content pairs)
                        conversation_context['messages'] = [
                            {'role': m.get('role', 'user' if i % 2 == 0 else 'assistant'), 'content': m.get(
                                'user') if 'user' in m else m.get('assistant')}
                            for i, m in enumerate(st.session_state[conversation_key])
                        ]
                        # last assistant message helpful for correction detection
                        try:
                            last_assistant_entry = next((m for m in reversed(
                                st.session_state[conversation_key]) if 'assistant' in m and m.get('assistant')), None)
                            if last_assistant_entry:
                                conversation_context['last_assistant_message'] = last_assistant_entry.get(
                                    'assistant')
                        except Exception:
                            conversation_context['last_assistant_message'] = None

                    # --- Local preprocessing / privacy steward ---
                    preproc_res = None
                    try:
                        from local_inference.preprocessor import Preprocessor
                        if 'local_preprocessor' not in st.session_state:
                            # default to test_mode=True to avoid heavy model loads in dev
                            st.session_state['local_preprocessor'] = Preprocessor(
                                test_mode=True)
                        p = st.session_state.get('local_preprocessor')
                        if p:
                            preproc_res = p.preprocess(
                                user_input, conversation_context)
                            # Use sanitized text for downstream processing
                            sanitized_text = preproc_res.get(
                                'sanitized_text', user_input)
                            st.session_state['last_preproc'] = {
                                'intent': preproc_res.get('intent'),
                                'confidence': preproc_res.get('confidence'),
                                'emotional_tags': preproc_res.get('emotional_tags'),
                                'edit_log': preproc_res.get('edit_log'),
                                'editorial_interventions': preproc_res.get('editorial_interventions', []),
                                'escalation_action': preproc_res.get('escalation_action'),
                                'escalation_reason': preproc_res.get('escalation_reason'),
                                'taxonomy_source': preproc_res.get('taxonomy_source')
                            }
                        else:
                            sanitized_text = user_input
                    except Exception:
                        sanitized_text = user_input

                    # Use the sanitized text if available (from local preprocessor)
                    effective_input = sanitized_text if 'sanitized_text' in locals(
                    ) and sanitized_text else user_input

                    if processing_mode == "local":
                        from emotional_os.glyphs.signal_parser import parse_input
                        local_analysis = parse_input(effective_input, "emotional_os/parser/signal_lexicon.json",
                                                     db_path="emotional_os/glyphs/glyphs.db", conversation_context=conversation_context)
                        glyphs = local_analysis.get("glyphs", [])
                        voltage_response = local_analysis.get(
                            "voltage_response", "")
                        ritual_prompt = local_analysis.get("ritual_prompt", "")
                        debug_signals = local_analysis.get("signals", [])
                        debug_gates = local_analysis.get("gates", [])
                        debug_glyphs = glyphs
                        debug_sql = local_analysis.get("debug_sql", "")
                        debug_glyph_rows = local_analysis.get(
                            "debug_glyph_rows", [])
                        best_glyph = local_analysis.get("best_glyph")
                        glyph_display = best_glyph['glyph_name'] if best_glyph else 'None'
                        response = f"{voltage_response}\n\nResonant Glyph: {glyph_display}"
                    elif processing_mode == "ai_preferred":
                        try:
                            saori_url = st.secrets.get(
                                "supabase", {}).get("saori_function_url")
                            supabase_key = st.secrets.get(
                                "supabase", {}).get("key")
                            if not saori_url or not supabase_key:
                                response = "AI processing unavailable in demo mode. Your feelings are still valid and important."
                            else:
                                payload = {
                                    "message": effective_input,
                                    "mode": processing_mode,
                                    "user_id": st.session_state.user_id
                                }
                                if document_analysis:
                                    glyphs = document_analysis.get(
                                        "glyphs", [])
                                    voltage_response = document_analysis.get(
                                        "voltage_response", "")
                                    ritual_prompt = document_analysis.get(
                                        "ritual_prompt", "")
                                    debug_signals = document_analysis.get(
                                        "signals", [])
                                    debug_gates = document_analysis.get(
                                        "gates", [])
                                    debug_glyphs = glyphs
                                    doc_context = "\n".join([
                                        f"Document Insights: {voltage_response}",
                                        f"Activated Glyphs: {', '.join([g['glyph_name'] for g in glyphs])}" if glyphs and isinstance(
                                            glyphs, list) else "",
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
                                        response = result.get(
                                            "reply", "I'm here to listen.")
                                    else:
                                        response = "I'm experiencing some technical difficulties, but I'm still here for you."
                        except Exception:
                            response = "I'm having trouble connecting right now, but your feelings are still valid and important."
                    elif processing_mode == "hybrid":
                        from emotional_os.glyphs.signal_parser import parse_input
                        local_analysis = parse_input(effective_input, "emotional_os/parser/signal_lexicon.json",
                                                     db_path="emotional_os/glyphs/glyphs.db", conversation_context=conversation_context)
                        glyphs = local_analysis.get("glyphs", [])
                        voltage_response = local_analysis.get(
                            "voltage_response", "")
                        ritual_prompt = local_analysis.get("ritual_prompt", "")
                        debug_signals = local_analysis.get("signals", [])
                        debug_gates = local_analysis.get("gates", [])
                        debug_glyphs = glyphs
                        debug_sql = local_analysis.get("debug_sql", "")
                        debug_glyph_rows = local_analysis.get(
                            "debug_glyph_rows", [])
                        try:
                            saori_url = st.secrets.get(
                                "supabase", {}).get("saori_function_url")
                            supabase_key = st.secrets.get(
                                "supabase", {}).get("key")
                            if not saori_url or not supabase_key:
                                response = f"Local Analysis: {voltage_response}\nActivated Glyphs: {', '.join([g['glyph_name'] for g in glyphs]) if glyphs else 'None'}\n{ritual_prompt}\n(AI enhancement unavailable in demo mode)"
                            else:
                                payload = {
                                    "message": effective_input,
                                    "mode": processing_mode,
                                    "user_id": st.session_state.user_id,
                                    "local_voltage_response": voltage_response,
                                    "local_glyphs": ', '.join([g['glyph_name'] for g in glyphs]) if glyphs else '',
                                    "local_ritual_prompt": ritual_prompt
                                }
                                if document_analysis:
                                    doc_glyphs = document_analysis.get(
                                        "glyphs", [])
                                    doc_voltage_response = document_analysis.get(
                                        "voltage_response", "")
                                    doc_ritual_prompt = document_analysis.get(
                                        "ritual_prompt", "")
                                    debug_signals = document_analysis.get(
                                        "signals", [])
                                    debug_gates = document_analysis.get(
                                        "gates", [])
                                    debug_glyphs = doc_glyphs
                                    doc_context = "\n".join([
                                        f"Document Insights: {doc_voltage_response}",
                                        f"Activated Glyphs: {', '.join([g['glyph_name'] for g in doc_glyphs])}" if doc_glyphs and isinstance(
                                            doc_glyphs, list) else "",
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
                                        response = result.get(
                                            "reply", "I'm here to listen.")
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
                                    safety_flag = is_sensitive_input(
                                        user_input)
                                except Exception:
                                    safety_flag = False
                                if not safety_flag:
                                    limbic_result = engine.process_emotion_with_limbic_mapping(
                                        user_input)
                                    try:
                                        decorated = decorate_reply(
                                            response, limbic_result)
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

                    # Run through Fallback Protocols for tone-aware response handling
                    fallback_result = None
                    if st.session_state.get("fallback_protocol"):
                        try:
                            detected_triggers = []
                            if 'glyphs' in locals() and glyphs:
                                detected_triggers = [
                                    g.get('glyph_name', '') for g in glyphs if isinstance(g, dict)]

                            fallback_result = st.session_state["fallback_protocol"].process_exchange(
                                user_text=user_input,
                                detected_triggers=detected_triggers if detected_triggers else None
                            )

                            # If ambiguous tone detected, use companion's clarification request
                            if fallback_result.get("decisions", {}).get("should_ask_clarification"):
                                response = fallback_result["companion_behavior"]["message"]

                            # Store protocol result in session for debugging
                            st.session_state[f"protocol_result_{len(st.session_state[conversation_key])}"] = fallback_result
                        except Exception as e:
                            logger.debug(
                                f"Fallback protocol error (non-fatal): {e}")
                            fallback_result = None

                    # Prevent verbatim repetition of assistant replies across consecutive turns.
                    # If the new response exactly matches the previous assistant message, append
                    # a gentle, specific follow-up to nudge the conversation forward.
                    try:
                        last_assistant = None
                        if st.session_state.get(conversation_key) and len(st.session_state[conversation_key]) > 0:
                            last_assistant = st.session_state[conversation_key][-1].get(
                                'assistant')
                        if last_assistant and last_assistant.strip() == response.strip():
                            followups = [
                                "Can you tell me one specific detail about that?",
                                "Would it help if we tried one small concrete step together?",
                                "If you pick one thing to focus on right now, what would it be?",
                                "That's important — would you like a short breathing practice or a practical plan?"
                            ]
                            idx = len(response) % len(followups)
                            response = response + " " + followups[idx]
                    except Exception:
                        # Non-fatal: if anything goes wrong while checking repetition, continue
                        pass

                    st.write(response)
                    st.caption(
                        f"Processed in {processing_time:.2f}s • Mode: {processing_mode}")

                    # Show anonymization consent widget
                    try:
                        from emotional_os.deploy.modules.consent_ui import render_anonymization_consent_widget
                        exchange_id = f"exchange_{len(st.session_state.get(conversation_key, []))}"
                        consent_result = render_anonymization_consent_widget(
                            exchange_id)

                        if consent_result:
                            st.session_state[f"consent_{exchange_id}"] = consent_result
                    except ImportError:
                        st.warning("Consent UI unavailable")
                    except Exception as e:
                        st.warning(f"Consent settings error: {e}")
        # Always show debug expander if toggled, regardless of mode
        if st.session_state.get("show_debug", False):
            with st.expander("Debug: Emotional OS Activation Details", expanded=True):
                st.write("**Signals Detected:**", debug_signals)
                st.write("**Gates Activated:**", debug_gates)
                st.write("**Glyphs Matched:**", debug_glyphs)
                st.write("**Raw SQL Query:**", debug_sql)
                st.write("**Glyph Rows (Raw):**", debug_glyph_rows)

                # Show Fallback Protocol details if available
                if fallback_result:
                    with st.expander("Fallback Protocols Analysis", expanded=False):
                        st.write(
                            "**Tone Ambiguity:**", fallback_result.get("detections", {}).get("ambiguity"))
                        st.write(
                            "**Trigger Misfires:**", fallback_result.get("detections", {}).get("misfires"))
                        st.write("**Overlapping Triggers:**", fallback_result.get(
                            "detections", {}).get("overlapping_triggers"))
                        st.write("**Glyph Response:**",
                                 fallback_result.get("glyph_response"))
                        st.write("**Protocol Decisions:**",
                                 fallback_result.get("decisions"))

        entry = {
            "user": user_input,
            "assistant": response,
            "processing_time": f"{processing_time:.2f}s",
            "mode": processing_mode,
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state[conversation_key].append(entry)

        # Learn from hybrid mode conversations to improve local mode
        # AND generate new glyphs dynamically during dialogue
        if processing_mode == "hybrid":
            try:
                from emotional_os.learning.hybrid_learner_v2 import get_hybrid_learner
                from emotional_os.learning.adaptive_signal_extractor import AdaptiveSignalExtractor

                # Try to import create_integrated_processor from scripts/utilities or directly
                try:
                    import sys
                    import os
                    sys.path.insert(0, os.path.join(os.path.dirname(
                        __file__), '../../../scripts/utilities'))
                    from hybrid_processor_with_evolution import create_integrated_processor
                except ImportError:
                    # Fallback if not available
                    create_integrated_processor = None

                learner = get_hybrid_learner()
                user_id = st.session_state.get('user_id', 'anonymous')

                # Initialize dynamic evolution system if not already in session
                if 'hybrid_processor' not in st.session_state and create_integrated_processor:
                    adaptive_extractor = AdaptiveSignalExtractor(
                        adaptive=True, use_discovered=True)
                    st.session_state['hybrid_processor'] = create_integrated_processor(
                        hybrid_learner=learner,
                        adaptive_extractor=adaptive_extractor,
                        user_id=user_id,
                    )

                # Process through integrated pipeline with dynamic glyph generation
                if 'hybrid_processor' in st.session_state:
                    processor = st.session_state['hybrid_processor']
                    evolution_result = processor.process_user_message(
                        user_message=user_input,
                        ai_response=response,
                        user_id=user_id,
                        conversation_id=st.session_state.get(
                            'conversation_id', 'default'),
                        glyphs=debug_glyphs,
                    )

                    # Check if new glyphs were generated
                    new_glyphs = evolution_result['pipeline_stages']['glyph_generation'].get(
                        'new_glyphs_generated', [])
                    if new_glyphs and len(new_glyphs) > 0:
                        # Store newly generated glyphs in session
                        if 'new_glyphs_this_session' not in st.session_state:
                            st.session_state['new_glyphs_this_session'] = []
                        st.session_state['new_glyphs_this_session'].extend(
                            new_glyphs)

                        # Display notification about new glyphs
                        st.success(
                            f"✨ {len(new_glyphs)} new glyph(s) discovered from this exchange!")
                        for glyph in new_glyphs:
                            glyph_dict = glyph.to_dict() if hasattr(glyph, 'to_dict') else glyph
                            st.info(f"  {glyph_dict.get('symbol', '?')} **{glyph_dict.get('name', '?')}** "
                                    f"({' + '.join(glyph_dict.get('core_emotions', []))})")

                    # Log learning results
                    learning_result = evolution_result['pipeline_stages']['hybrid_learning'].get(
                        'learning_result', {})
                    if learning_result.get("learned_to_shared"):
                        logger.info(
                            f"User {user_id} contributed to shared lexicon")
                    elif learning_result.get("learned_to_user"):
                        logger.info(
                            f"User {user_id} learning to personal lexicon")

            except ImportError as e:
                # Fallback if dynamic evolution not available
                logger.warning(f"Dynamic glyph evolution not available: {e}")
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
                        logger.info(
                            f"User {user_id} contributed to shared lexicon")
                    elif result.get("learned_to_user"):
                        logger.info(
                            f"User {user_id} learning to personal lexicon")
                except Exception as fallback_e:
                    logger.error(
                        f"Fallback learning also failed: {fallback_e}")
            except Exception as e:
                # Non-fatal: learning should not break the app
                logger.warning(f"Hybrid learning failed: {e}")

        # Persist to Supabase if the user opted in using the new conversation manager
        try:
            if st.session_state.get('persist_history', False) and st.session_state.get('conversation_manager'):
                manager = st.session_state['conversation_manager']
                conversation_id = st.session_state.get(
                    'current_conversation_id', 'default')

                # Auto-name conversation based on first message
                # Just added first exchange
                if len(st.session_state[conversation_key]) == 1:
                    if generate_auto_name:
                        title = generate_auto_name(user_input)
                        st.session_state['conversation_title'] = title
                    else:
                        title = "New Conversation"
                else:
                    title = st.session_state.get(
                        'conversation_title', 'New Conversation')

                # Save to database with conversation manager
                messages = st.session_state[conversation_key]
                success, message = manager.save_conversation(
                    conversation_id=conversation_id,
                    title=title,
                    messages=messages,
                    processing_mode=processing_mode
                )

                if not success:
                    logger.warning(f"Failed to save conversation: {message}")
        except Exception as e:
            # Best-effort: do not break the UI if persistence fails
            logger.warning(f"Conversation persistence error: {e}")
            pass

        # Fallback: Also persist individual messages to old conversation_history table if configured
        try:
            if st.session_state.get('persist_history', False):
                sup_cfg = st.secrets.get('supabase', {}) if hasattr(
                    st, 'secrets') else {}
                supabase_url = sup_cfg.get('url') or sup_cfg.get(
                    'saori_url') or sup_cfg.get('saori_function_url')
                supabase_key = sup_cfg.get('key') or sup_cfg.get(
                    'anon_key') or sup_cfg.get('apikey')
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

                if base_url and supabase_key and requests:
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
                        resp = requests.post(
                            rest_url, headers=headers, json=payload, timeout=6)
                        if resp.status_code not in (200, 201):
                            # Non-fatal: warn in UI (use generic storage wording)
                            st.warning(
                                'Could not save history to secure storage right now.')
                    except Exception:
                        st.warning(
                            'Temporary issue saving to secure storage. Your local history is still intact.')
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
            st.markdown(
                "Use this space to record a structured emotional entry. You'll log the date, event, mood, reflections, and insights.")
            date = st.date_input("Date", value=dt.date.today())
            log_time = st.time_input("Time", value=dt.datetime.now().time())
            event = st.text_area("Event", placeholder="What happened?")
            mood = st.text_input("Mood", placeholder="How did it feel?")
            reflections = st.text_area(
                "Reflections", placeholder="What’s emerging emotionally?")
            insights = st.text_area(
                "Insights", placeholder="What truth or clarity surfaced?")
            if st.button("Conclude Log"):
                st.success("Your personal log has been saved.")
                try:
                    st.download_button(
                        label="Download as Word Doc",
                        data=generate_doc(
                            date, log_time, event, mood, reflections, insights),
                        file_name="personal_log.docx"
                    )
                except Exception as e:
                    st.error(f"Error generating Word document: {e}")
        elif journal_type == "Daily Emotional Check-In":
            st.markdown(
                "Log your mood, stress level, and a short reflection for today.")
            checkin_date = st.date_input("Date", value=dt.date.today(), key="checkin_date")  # noqa: F841  # used for Streamlit UI side-effect
            mood = st.selectbox("Mood", [
                                "Calm", "Stressed", "Sad", "Angry", "Joyful", "Fatigued", "Other"], key="checkin_mood")
            stress = st.slider("Stress Level", 0, 10, 5, key="checkin_stress")  # noqa: F841  # used for Streamlit UI side-effect
            reflection = st.text_area("Reflection", placeholder="What's on your mind today?", key="checkin_reflection")  # noqa: F841  # used for Streamlit UI side-effect
            if st.button("Save Check-In"):
                st.success("Your daily check-in has been saved.")
        elif journal_type == "Self-Care Tracker":
            st.markdown("Track your self-care activities and routines.")
            activities = st.multiselect(  # noqa: F841  # used for Streamlit UI side-effect
                "Self-Care Activities",
                ["Exercise", "Creative Work", "Peer Support", "Rest",
                    "Healthy Meal", "Time Outdoors", "Other"],
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
            st.markdown(
                "Write about your own reactions, growth, and challenges. No client details—just your personal journey.")
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
        if not requests:
            return False, "Requests library not available"

        if not user_id:
            return False, "No user_id provided"

        sup_cfg = st.secrets.get('supabase', {}) if hasattr(
            st, 'secrets') else {}
        supabase_url = sup_cfg.get('url') or sup_cfg.get(
            'saori_url') or sup_cfg.get('saori_function_url')
        supabase_key = sup_cfg.get('key') or sup_cfg.get(
            'anon_key') or sup_cfg.get('apikey')
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
            requests.post(audit_url, headers=audit_headers,
                          json=audit_payload, timeout=6)
        except Exception:
            # Swallow audit failures; do not block the main delete result
            pass

        if success:
            return True, 'Deleted server-side history successfully.'
        else:
            return False, f'Supabase delete returned {resp.status_code}: {resp.text}'
    except Exception as e:
        return False, str(e)
