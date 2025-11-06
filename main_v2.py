treamlit as st
import streamlit as st
from pathlib import Path
import base64

from emotional_os.deploy.modules.auth import SaoynxAuthentication
from emotional_os.deploy.modules.ui import render_main_app, render_splash_interface, delete_user_history_from_supabase

# Optional local preprocessor (privacy-first steward)
try:
    from local_inference.preprocessor import Preprocessor
    PREPROCESSOR_AVAILABLE = True
except Exception:
    Preprocessor = None
    PREPROCESSOR_AVAILABLE = False

# Optional limbic integration (safe import)
try:
    from emotional_os.glyphs.limbic_integration import LimbicIntegrationEngine
    HAS_LIMBIC = True
except Exception:
    LimbicIntegrationEngine = None
    HAS_LIMBIC = False

# Simple page configuration


def get_page_icon():
    try:
        logo_path = Path(
            "static/graphics/FirstPerson-Logo-black-cropped_notext.svg")
        if logo_path.exists():
            return str(logo_path)
    except Exception:
        pass
    return None


# Initialize theme in session state if not set
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Light'

# Must be first Streamlit command
st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon=get_page_icon(),
    layout="wide",
    initial_sidebar_state="expanded")

# Apply theme-specific styles
if st.session_state.get('theme') == 'Dark':
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stButton>button {
            background-color: #262730;
            color: #FAFAFA;
            border: 1px solid #555;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #FFFFFF;
            color: #31333F;
        }
        .stButton>button {
            background-color: #F0F2F6;
            color: #31333F;
            border: 1px solid #E0E0E0;
        }
        </style>
    """, unsafe_allow_html=True)

# Basic theme compatibility
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {color: inherit;}
    .stMarkdown {color: inherit;}
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)


def render_header():
    """Render the app header with logo and title. Should only be called once."""
    if st.session_state.get('header_rendered'):
        return

    header_left, header_right = st.columns([1, 5])

    with header_left:
        try:
            logo_path = Path(
                "static/graphics/FirstPerson-Logo-black-cropped_notext.svg")
            if logo_path.exists():
                st.image(str(logo_path), width=50)
        except Exception:
            pass

    with header_right:
        st.header("FirstPerson – Personal AI Companion")

    st.session_state['header_rendered'] = True


def main():
    # Render header once at the start
    render_header()

    # Initialize local preprocessor if available. Use test_mode=True by default so
    # it won't attempt large model loads in environments without GPU. Change to
    # test_mode=False in production with a GPU-backed host.
    if PREPROCESSOR_AVAILABLE and 'local_preprocessor' not in st.session_state:
        try:
            st.session_state['local_preprocessor'] = Preprocessor(
                test_mode=True)
        except Exception:
            st.session_state['local_preprocessor'] = None

    def run_local_preprocessor(user_text, conversation_context=None):
        """Helper: run the local preprocessor if present; safe fallback otherwise."""
        p = st.session_state.get('local_preprocessor')
        if not p:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'sanitized_text': user_text,
                'short_reply': None,
                'emotional_tags': ['neutral'],
                'edit_log': []
            }
        try:
            return p.preprocess(user_text, conversation_context)
        except Exception:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'sanitized_text': user_text,
                'short_reply': None,
                'emotional_tags': ['neutral'],
                'edit_log': ['preprocessor_failed']
            }

    # Initialize limbic engine if available — now enabled by default and not user-toggled
    st.session_state['enable_limbic'] = True
    if HAS_LIMBIC and LimbicIntegrationEngine is not None and 'limbic_engine' not in st.session_state:
        try:
            st.session_state['limbic_engine'] = LimbicIntegrationEngine()
            # note: we intentionally do not expose a toggle to the user
        except Exception as e:
            # non-fatal: record error in sidebar for visibility
            st.sidebar.error(f"Failed to initialize limbic engine: {e}")

    # Initialize authentication
    auth = SaoynxAuthentication()

    # --- Limbic demo controls and telemetry ---
    try:
        from emotional_os.glyphs.limbic_telemetry import (
            fetch_recent,
            init_db,
            record_event,
        )
    except Exception:
        # fallback to local import if running from root
        try:
            from emotional_os.glyphs.limbic_telemetry import (
                fetch_recent,
                init_db,
                record_event,
            )
        except Exception:
            record_event = None
            fetch_recent = None
            init_db = None

    # Sidebar: Privacy & Storage (friendlier UX)
    st.sidebar.markdown("---")
    with st.sidebar.expander("Privacy & Storage", expanded=False):
        status_on = bool(st.session_state.get('persist_history', False)
                         and st.session_state.get('persist_confirmed', False))
        status_chip = "🟢 On" if status_on else "⚪ Off"
        st.markdown(f"**Status:** {status_chip}")

        # Response style setting
        st.markdown("**Response Style:**")
        response_style = st.radio(
            "How detailed should responses be?",
            ["Brief", "Balanced", "Thoughtful"],
            index=1,
            label_visibility="collapsed",
            horizontal=True
        )
        st.session_state['response_style'] = response_style

        enable_toggle = st.checkbox(
            "Save my chats",
            value=status_on,
            help="Optional: save new messages to your secure account storage. You can turn this off anytime."
        )

        if enable_toggle and not st.session_state.get('persist_confirmed', False):
            st.info(
                "To enable storage, please confirm that you're okay with saving your chats.")
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("I consent"):
                    st.session_state['persist_confirmed'] = True
                    st.session_state['persist_history'] = True
                    # Persist preference to server if conversation manager available
                    try:
                        mgr = st.session_state.get('conversation_manager')
                        if not mgr:
                            try:
                                from emotional_os.deploy.modules.conversation_manager import ConversationManager
                                if 'user_id' in st.session_state:
                                    mgr = ConversationManager(
                                        st.session_state['user_id'])
                            except Exception:
                                mgr = None
                        if mgr:
                            mgr.save_user_preferences({
                                'persist_history': True,
                                'persist_confirmed': True
                            })
                    except Exception:
                        pass
                    st.rerun()
            with c2:
                if st.button("Not now"):
                    st.session_state['persist_confirmed'] = False
                    st.session_state['persist_history'] = False
                    try:
                        mgr = st.session_state.get('conversation_manager')
                        if not mgr:
                            try:
                                from emotional_os.deploy.modules.conversation_manager import ConversationManager
                                if 'user_id' in st.session_state:
                                    mgr = ConversationManager(
                                        st.session_state['user_id'])
                            except Exception:
                                mgr = None
                        if mgr:
                            mgr.save_user_preferences({
                                'persist_history': False,
                                'persist_confirmed': False
                            })
                    except Exception:
                        pass
                    st.rerun()
        else:
            st.session_state['persist_history'] = bool(
                enable_toggle and st.session_state.get('persist_confirmed', False))
            # Attempt to save updated preference when toggled from sidebar
            try:
                mgr = st.session_state.get('conversation_manager')
                if not mgr:
                    try:
                        from emotional_os.deploy.modules.conversation_manager import ConversationManager
                        if 'user_id' in st.session_state:
                            mgr = ConversationManager(
                                st.session_state['user_id'])
                    except Exception:
                        mgr = None
                if mgr:
                    mgr.save_user_preferences({
                        'persist_history': bool(st.session_state.get('persist_history', False)),
                        'persist_confirmed': bool(st.session_state.get('persist_confirmed', False))
                    })
            except Exception:
                pass

        st.caption(
            "Stored fields: user_id, username, your message, assistant reply, processing time, mode, timestamp.")

        # Group server-side deletion under the same expander
        if st.session_state.get('persist_confirmed', False) and st.session_state.get('user_id'):
            if not st.session_state.get('clear_server_history_pending'):
                if st.button('Delete my server history'):
                    st.session_state['clear_server_history_pending'] = True
                    st.rerun()
            else:
                st.warning(
                    'This will permanently delete your persisted messages for your account.')
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button('Confirm delete'):
                        success, msg = delete_user_history_from_supabase(
                            str(st.session_state.get('user_id', '')))
                        if success:
                            st.success('Server-side history deleted.')
                        else:
                            st.error(
                                'Failed to delete server history. Please try again later.')
                        st.session_state['clear_server_history_pending'] = False
                        st.rerun()
                with col_b:
                    if st.button('Cancel'):
                        st.session_state['clear_server_history_pending'] = False
                        st.rerun()

    # Learning stats section
    st.sidebar.markdown("---")
    with st.sidebar.expander("📚 Learning Progress", expanded=False):
        try:
            from emotional_os.learning.hybrid_learner_v2 import get_hybrid_learner
            learner = get_hybrid_learner()

            col1, col2 = st.sidebar.columns(2)
            with col1:
                # User-specific stats
                user_stats = learner.get_learning_stats(
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                st.metric("Your Signals", user_stats.get("signals_learned", 0))
                st.metric("Your Trust",
                          f"{user_stats.get('trust_score', 0.5):.1%}")

            with col2:
                # Shared stats
                shared_stats = learner.get_learning_stats()
                st.metric("Community Signals", shared_stats.get(
                    "signals_in_shared_lexicon", 0))
                st.metric("Exchanges", shared_stats.get(
                    "learning_log_entries", 0))

            st.caption(
                "💚 Green checkmark = learning contributed to shared lexicon")
            st.caption("💙 Blue dot = learning only to your personal profile")

        except Exception as e:
            st.caption(f"Learning system not ready: {e}")

    # Dynamic glyph evolution section
    st.sidebar.markdown("---")
    with st.sidebar.expander("✨ Glyphs Discovered This Session", expanded=False):
        try:
            new_glyphs = st.session_state.get('new_glyphs_this_session', [])

            if new_glyphs and len(new_glyphs) > 0:
                st.success(f"🎉 {len(new_glyphs)} new glyph(s) discovered!")

                for i, glyph in enumerate(new_glyphs, 1):
                    glyph_dict = glyph.to_dict() if hasattr(glyph, 'to_dict') else glyph
                    with st.container(border=True):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(
                                f"<div style='font-size: 2em;'>{glyph_dict.get('symbol', '?')}</div>", unsafe_allow_html=True)
                        with col2:
                            st.markdown(
                                f"**{glyph_dict.get('name', 'Unknown')}**")
                            emotions = glyph_dict.get('core_emotions', [])
                            st.caption(f"💭 {' + '.join(emotions)}")
                            keywords = glyph_dict.get(
                                'associated_keywords', [])
                            st.caption(f"🏷️ {', '.join(keywords)}")

                # Option to export
                if st.button("📥 Export Discovered Glyphs"):
                    if 'hybrid_processor' in st.session_state:
                        processor = st.session_state['hybrid_processor']
                        export_file = f"learning/user_{st.session_state.get('user_id', 'anonymous')}_glyphs.json"
                        result = processor.export_session_glyphs(export_file)
                        if result.get("success"):
                            st.success(f"✓ Exported {result['count']} glyphs")
            else:
                st.info(
                    "No new glyphs discovered yet. Keep exploring your emotions!")
                st.caption(
                    "💡 New glyphs are created when the system detects meaningful emotional patterns in your dialogue.")

        except Exception as e:
            st.warning(f"Glyph tracking not available: {e}")

    st.sidebar.markdown("### Conversation History")
    # Use a per-user conversation history key that matches the main UI
    conversation_key = f"conversation_history_{st.session_state.get('user_id', 'anonymous')}"
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = []

    history = st.session_state[conversation_key]
    max_items = 12
    # Show the most recent messages (newest first)
    for i, exch in enumerate(reversed(history[-max_items:])):
        # Compute the original index in the history list
        orig_idx = len(history) - 1 - i
        ts = exch.get('timestamp', '')
        short_ts = ts[11:19] if ts else ''
        st.sidebar.markdown(f"**{short_ts}**")
        st.sidebar.write(f"**You:** {exch.get('user','')[:120]}")
        cols = st.sidebar.columns([1, 1])
        with cols[0]:
            if st.button("Recall", key=f"recall_{orig_idx}"):
                # Set a recalled message which the main UI will pick up and process
                st.session_state['recalled_message'] = exch.get('user', '')
                st.rerun()
        with cols[1]:
            if st.button("Resend", key=f"resend_{orig_idx}"):
                # Mark for auto-processing and set recalled text
                st.session_state['recalled_message'] = exch.get('user', '')
                st.session_state['auto_process'] = True
                st.rerun()

    # Compact controls for history export/clear
    st.sidebar.markdown('---')
    if st.sidebar.button('Clear Local History'):
        st.session_state[conversation_key] = []
        st.rerun()
    if st.sidebar.button('Download History'):
        try:
            import json as _json
            st.sidebar.download_button('Download JSON', _json.dumps(
                st.session_state[conversation_key], indent=2), file_name=f'history_{st.session_state.get("user_id","anon")}.json')
        except Exception:
            st.sidebar.error('Failed to prepare history download')
    # Check if user is authenticated
    if st.session_state.get('authenticated', False):
        render_main_app()
    else:
        render_splash_interface(auth)


if __name__ == "__main__":
    main()
