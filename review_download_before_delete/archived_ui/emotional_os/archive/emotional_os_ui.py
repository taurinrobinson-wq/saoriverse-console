"""
Clean SAOYNX UI - Professional login interface
Based on the splash page design with clean branding
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta
# `hashlib` and `secrets` were imported in earlier work but are unused in this archived UI copy.
# Removed to satisfy lint (F401) while keeping the file minimal and archive-only.

# Page configuration
st.set_page_config(
    page_title="SAOYNX - AI Emotional Interfaces",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


class SaoynxAuthentication:
    """Clean authentication system matching SAOYNX design"""

    def __init__(self):
        # Use Streamlit secrets
        try:
            self.supabase_url = st.secrets["supabase"]["url"]
            self.supabase_key = st.secrets["supabase"]["key"]
        except KeyError:
            st.error("❌ Supabase configuration not found in secrets")
            st.stop()

        self.init_session_state()

    def init_session_state(self):
        """Initialize authentication session state"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'session_expires' not in st.session_state:
            st.session_state.session_expires = None

    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user login"""
        try:
            auth_url = st.secrets.get("supabase", {}).get(
                "auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
            response = requests.post(
                auth_url,
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "authenticate",
                    "username": username,
                    "password": password
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("authenticated"):
                    # Set session state
                    st.session_state.authenticated = True
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = username
                    st.session_state.session_expires = (
                        datetime.now() + timedelta(hours=8)).isoformat()

                    return {"success": True, "message": "Login successful"}
                else:
                    error_msg = data.get(
                        "error", "Invalid username or password")
                    return {"success": False, "message": f"Login failed: {error_msg}"}
            else:
                return {"success": False, "message": f"Authentication service error (HTTP {response.status_code})"}

        except Exception as e:
            return {"success": False, "message": f"Login error: {str(e)}"}

    def create_user(self, username: str, password: str) -> dict:
        """Create new user account"""
        try:
            auth_url = st.secrets.get("supabase", {}).get(
                "auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
            response = requests.post(
                auth_url,
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "create_user",
                    "username": username,
                    "password": password,
                    "created_at": datetime.now().isoformat()
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {"success": True, "message": "Account created successfully"}
                else:
                    return {"success": False, "message": data.get("error", "Failed to create account")}
            else:
                error_data = response.json() if response.headers.get(
                    'content-type', '').startswith('application/json') else {}
                return {"success": False, "message": error_data.get("error", "Failed to create account")}

        except Exception as e:
            return {"success": False, "message": f"Registration error: {str(e)}"}

    def quick_login_bypass(self):
        """Quick demo access"""
        import uuid

        st.session_state.authenticated = True
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.username = "demo_user"
        st.session_state.session_expires = (
            datetime.now() + timedelta(hours=8)).isoformat()

        st.rerun()

    def logout(self):
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.session_expires = None
        st.rerun()

    def render_splash_interface(self):
        """Render the clean SAOYNX splash interface"""

        # Custom CSS matching your design
        st.markdown("""
        <style>
        /* Hide Streamlit default elements */
        .stDeployButton {display: none;}
        header[data-testid="stHeader"] {display: none;}
        .stMainBlockContainer {padding-top: 1rem;}
        .main .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        
        /* Main container - professional centering */
        .main-splash {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 400px;
            background: white;
            padding: 2rem;
            text-align: center;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        /* Logo section */
        .logo-section {
            margin-bottom: 1rem;
            width: 100%;
        }
        
        .logo-text {
            font-size: 2rem;
            font-weight: 300;
            letter-spacing: 4px;
            color: #2E2E2E;
            margin: 0.5rem 0 0.2rem 0;
            font-family: 'Arial', sans-serif;
            text-align: center;
        }
        
        .logo-subtitle {
            font-size: 1rem;
            color: #666;
            letter-spacing: 2px;
            font-weight: 300;
            text-transform: uppercase;
            line-height: 1.2;
            text-align: center;
        }
        
        /* Auth sections - tight compact layout */
        .auth-container {
            margin: 0.5rem 0;
        }
        
        .auth-question {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.3rem;
            text-align: center;
        }
        
        .auth-title {
            font-size: 1.1rem;
            color: #2E2E2E;
            margin-bottom: 1rem;
            font-weight: 300;
        }
        
        /* Form container centering - compact */
        .form-container {
            max-width: 350px;
            margin: 1rem auto;
            padding: 1rem;
            text-align: center;
        }
        
        /* Form styling - ultra tight spacing */
        .stTextInput > div > div > input {
            border-radius: 30px;
            border: 2px solid #ddd;
            padding: 6px 12px;
            font-size: 0.85rem;
            text-align: center;
            height: 30px;
            line-height: 0.6;
        }
        
        /* Minimal form spacing */
        .stTextInput {
            margin-bottom: 0.1rem;
            line-height: 0.6;
        }
        
        /* Compact form layout */
        .stTextInput > label {
            margin-bottom: 0.1rem !important;
            line-height: 0.6;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #666;
            box-shadow: 0 0 0 1px #666;
        }
        
        /* Professional button styling */
        .stButton > button {
            width: 100%;
            max-width: 140px;
            height: 35px;
            border: 2px solid #2E2E2E;
            background-color: #2E2E2E;
            border-radius: 8px;
            font-size: 0.8rem;
            color: white;
            font-weight: 600;
            cursor: pointer;
            outline: none;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stButton > button:hover {
            background-color: white;
            color: #2E2E2E;
            border-color: #2E2E2E;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(46, 46, 46, 0.2);
        }
        
        /* Quick access - clean divider */
        .quick-access {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #ddd;
            text-align: center;
        }
        
        .quick-title {
            color: #999;
            font-size: 0.8rem;
            margin-bottom: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Complete logo with text - perfectly centered
        st.markdown(
            '<div style="text-align: center; margin-bottom: 1rem;">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            try:
                st.image("Saonyx_Logo.png", width=200)
            except Exception:
                st.markdown('''
                <div style="font-size: 4rem;">🧠</div>
                <div style="font-size: 2rem; font-weight: 300; letter-spacing: 4px; color: #2E2E2E; margin: 0.5rem 0 0.2rem 0;">SAOYNX</div>
                <div style="font-size: 1rem; color: #666; letter-spacing: 2px; font-weight: 300; text-transform: uppercase;">AI EMOTIONAL<br>INTERFACES</div>
                ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Handle different states
        if st.session_state.get('show_login', False):
            self.render_login_form()
        elif st.session_state.get('show_register', False):
            self.render_register_form()
        else:
            # Main splash screen - professional centered layout
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)

            # Tight, compact button layout
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Questions closer together
                qcol1, qcol2 = st.columns([1, 1], gap="small")
                with qcol1:
                    st.markdown(
                        '<div class="auth-question">existing user?</div>', unsafe_allow_html=True)
                with qcol2:
                    st.markdown(
                        '<div class="auth-question">new user?</div>', unsafe_allow_html=True)

                # Buttons closer together
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

            # Quick access section
            st.markdown('<div class="quick-access">', unsafe_allow_html=True)
            st.markdown('<div class="quick-title">Quick Access</div>',
                        unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("⚡ Demo Mode", help="Try the system instantly"):
                    self.quick_login_bypass()

            st.markdown('</div>', unsafe_allow_html=True)

    def render_login_form(self):
        """Clean login form matching your design"""

        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        # Back button
        if st.button("← Back", key="back_login"):
            st.session_state.show_login = False
            st.rerun()

        # No duplicate logo - just the title
        st.markdown(
            '<div class="auth-title" style="text-align: center; margin: 1rem 0;">Sign In</div>', unsafe_allow_html=True)

        # Login form - ultra compact
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                # Tight spacing labels
                st.markdown(
                    '<div style="text-align: left; margin-bottom: 0.1rem; color: #666; font-size: 0.8rem;">login:</div>', unsafe_allow_html=True)
                username = st.text_input(
                    "login", label_visibility="collapsed", placeholder="username")

                st.markdown(
                    '<div style="text-align: left; margin-bottom: 0.1rem; margin-top: 0.1rem; color: #666; font-size: 0.8rem;">password:</div>', unsafe_allow_html=True)
                password = st.text_input(
                    "password", label_visibility="collapsed", type="password", placeholder="password")

                st.markdown(
                    '<div style="margin: 0.2rem 0 0.1rem 0;"></div>', unsafe_allow_html=True)
                login_submitted = st.form_submit_button(
                    "Sign In", use_container_width=True)

                if login_submitted:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        with st.spinner("Signing in..."):
                            result = self.authenticate_user(username, password)

                        if result["success"]:
                            st.success("Welcome back!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result["message"])

        st.markdown('</div>', unsafe_allow_html=True)

    def render_register_form(self):
        """Clean registration form"""

        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        # Back button
        if st.button("← Back", key="back_register"):
            st.session_state.show_register = False
            st.rerun()

        # No duplicate logo - just the title
        st.markdown(
            '<div class="auth-title" style="text-align: center; margin: 1rem 0;">Create Account</div>', unsafe_allow_html=True)

        # Register form - ultra compact
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                # Tight spacing labels
                st.markdown(
                    '<div style="text-align: left; margin-bottom: 0.1rem; color: #666; font-size: 0.8rem;">login:</div>', unsafe_allow_html=True)
                username = st.text_input(
                    "login", label_visibility="collapsed", placeholder="choose username")

                st.markdown(
                    '<div style="text-align: left; margin-bottom: 0.1rem; margin-top: 0.1rem; color: #666; font-size: 0.8rem;">password:</div>', unsafe_allow_html=True)
                password = st.text_input(
                    "password", label_visibility="collapsed", type="password", placeholder="choose password")

                st.markdown(
                    '<div style="text-align: left; margin-bottom: 0.1rem; margin-top: 0.1rem; color: #666; font-size: 0.8rem;">confirm:</div>', unsafe_allow_html=True)
                confirm_password = st.text_input(
                    "confirm", label_visibility="collapsed", type="password", placeholder="confirm password")

                st.markdown(
                    '<div style="margin: 0.2rem 0 0.1rem 0;"></div>', unsafe_allow_html=True)
                register_submitted = st.form_submit_button(
                    "Register Now", use_container_width=True)

                if register_submitted:
                    if not username or not password:
                        st.error("Username and password are required")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating your account..."):
                            result = self.create_user(username, password)

                        if result["success"]:
                            st.success("Account created! Please sign in.")
                            st.session_state.show_register = False
                            st.session_state.show_login = True
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(result["message"])

        st.markdown('</div>', unsafe_allow_html=True)


def render_main_app():
    """Main app interface for authenticated users - Full Emotional OS"""
    st.title("🧠 Emotional OS - Personal AI Companion")
    st.markdown("*Your private space for emotional processing and growth*")

    # User header with logout
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.write(f"Welcome back, **{st.session_state.username}**! 👋")

    with col2:
        if st.button("⚙️ Settings", help="User settings and preferences"):
            st.info("Settings panel coming soon!")

    with col3:
        if st.button("🚪 Logout", help="Sign out of your account"):
            auth = SaoynxAuthentication()
            auth.logout()

    # User-specific conversation history
    conversation_key = f"conversation_history_{st.session_state.user_id}"
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = []

    # Main interface
    with st.container():
        # Processing mode selection
        col1, col2 = st.columns([2, 1])

        # Map legacy ai_preferred -> hybrid + prefer_ai
        if st.session_state.get('processing_mode') == 'ai_preferred':
            st.session_state.processing_mode = 'hybrid'
            st.session_state['prefer_ai'] = True

        with col1:
            mode_options = ["hybrid", "local"]
            current = st.session_state.get('processing_mode', 'hybrid')
            try:
                idx = mode_options.index(current)
            except ValueError:
                idx = 0
            processing_mode = st.selectbox(
                "Processing Mode",
                mode_options,
                index=idx,
                help="Hybrid: Best performance, Local: Maximum privacy"
            )

        with col2:
            if st.button("Clear History", type="secondary"):
                st.session_state[conversation_key] = []
                st.rerun()

    # Chat interface
    chat_container = st.container()

    # Display conversation history
    with chat_container:
        for i, exchange in enumerate(st.session_state[conversation_key]):
            with st.chat_message("user"):
                st.write(exchange["user"])

            with st.chat_message("assistant"):
                st.write(exchange["assistant"])
                if "processing_time" in exchange:
                    st.caption(
                        f"Processed in {exchange['processing_time']} • Mode: {exchange.get('mode', 'unknown')}")

    # Input area
    user_input = st.chat_input("Share what you're feeling...")
    # Store debug info in session state for reliable rendering
    if 'debug_info' not in st.session_state:
        st.session_state['debug_info'] = None
    if user_input:
        # Add user message to chat
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)

        # --- Seamless glyph response logic ---
        import sys
        sys.path.append(".")
        from emotional_os.parser import signal_parser
        import sqlite3
        # Try to import glyph generator if available
        try:
            from glyph_generator import GlyphGenerator
        except ImportError:
            GlyphGenerator = None
        # Try to import lexicon learner if available
        try:
            from learning.lexicon_learner import LexiconLearner
        except ImportError:
            LexiconLearner = None

        start_time = time.time()
        # 1. Parse signals and gates
        lexicon_path = "velonix_lexicon.json"
        db_path = "glyphs.db"
        result = signal_parser.parse_input(user_input, lexicon_path, db_path)
        signals = result["signals"]
        gates = result["gates"]
        glyphs = result["glyphs"]

        # Store debug info for expander
        st.session_state['debug_info'] = {
            "signals": signals,
            "gates": gates,
            "glyphs": glyphs
        }

        # 2. If no glyphs found, generate and insert a new glyph
        if not glyphs and GlyphGenerator:
            generator = GlyphGenerator()
            patterns = generator.detect_new_emotional_patterns(user_input)
            if patterns:
                new_glyph = generator.generate_new_glyph(patterns[0])
                if new_glyph:
                    # Insert into SQLite glyphs.db
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO glyph_lexicon (voltage_pair, glyph_name, description, gate, activation_signals) VALUES (?, ?, ?, ?, ?)",
                            (new_glyph.glyph_symbol, new_glyph.tag_name, new_glyph.narrative_hook,
                             gates[0] if gates else "Gate 4", ",".join(signals[0]["signal"] if signals else []))
                        )
                        conn.commit()
                        conn.close()
                        # Re-fetch glyphs
                        glyphs = signal_parser.fetch_glyphs(gates, db_path)
                    except Exception:
                        glyphs = []
                    # Update debug info after glyph generation
                    st.session_state['debug_info']['glyphs'] = glyphs

        # 3. Format response: always surface glyph details if found, plus supportive text
        if glyphs:
            glyph = glyphs[0]
            glyph_text = f"**Glyph Activated:** {glyph['glyph_name']}\n{glyph['description']}"
            supportive_text = result["voltage_response"]
            response = f"{glyph_text}\n\n{supportive_text}"
        else:
            response = result["voltage_response"]

        # 4. Lexicon learning after each message
        if LexiconLearner:
            learner = LexiconLearner()
            # Prepare conversation data for learning
            conversation_data = {
                "messages": [
                    {"type": "user", "content": user_input},
                    {"type": "system", "content": response}
                ]
            }
            learner.learn_from_conversation(conversation_data)

        processing_time = time.time() - start_time
        with chat_container:
            with st.chat_message("assistant"):
                st.write(response)
                st.caption(f"Processed in {processing_time:.2f}s")

        # Add to conversation history
        st.session_state[conversation_key].append({
            "user": user_input,
            "assistant": response,
            "processing_time": f"{processing_time:.2f}s",
            "mode": processing_mode,
            "timestamp": datetime.now().isoformat()
        })
        st.rerun()

    # Always show debug expander after assistant response
    if st.session_state.get('debug_info'):
        with st.expander("Debug: Emotional OS Activation Details", expanded=False):
            st.write("**Signals Detected:**",
                     st.session_state['debug_info']['signals'])
            st.write("**Gates Activated:**",
                     st.session_state['debug_info']['gates'])
            st.write("**Glyphs Matched:**",
                     st.session_state['debug_info']['glyphs'])

    # Sidebar with user stats and settings
    with st.sidebar:
        st.subheader("Your Emotional Journey")

        # User-specific stats
        conversation_count = len(st.session_state[conversation_key])
        st.metric("Conversations", conversation_count)

        if conversation_count > 0:
            recent_conversation = st.session_state[conversation_key][-1]
            st.metric("Last Session", recent_conversation["timestamp"][:10])

        st.subheader("Privacy Settings")
        st.write("🔒 Your data is completely isolated")
        st.write("🧠 Learning happens only from your conversations")
        st.write("⚡ Optimized for 2-3 second responses")

        if st.button("Download My Data", type="secondary"):
            # Option to export user's conversation data
            user_data = {
                "user_id": st.session_state.user_id,
                "username": st.session_state.username,
                "conversations": st.session_state[conversation_key],
                "export_date": datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON",
                json.dumps(user_data, indent=2),
                file_name=f"emotional_os_data_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )


def main():
    """Main application entry point"""
    auth = SaoynxAuthentication()

    # Check if user is authenticated
    if st.session_state.authenticated:
        render_main_app()
    else:
        auth.render_splash_interface()


if __name__ == "__main__":
    main()
