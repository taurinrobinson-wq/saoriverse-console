import streamlit as st

from emotional_os.deploy.modules.auth import SaoynxAuthentication
from emotional_os.deploy.modules.ui import render_main_app, render_splash_interface, delete_user_history_from_supabase

# Optional limbic integration (safe import)
try:
    from emotional_os.glyphs.limbic_integration import LimbicIntegrationEngine
    HAS_LIMBIC = True
except Exception:
    LimbicIntegrationEngine = None
    HAS_LIMBIC = False

# Page configuration
st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon="static/graphics/FirstPerson-Logo(black-cropped_notext).svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
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
        status_on = bool(st.session_state.get('persist_history', False) and st.session_state.get('persist_confirmed', False))
        status_chip = "🟢 On" if status_on else "⚪ Off"
        st.markdown(f"**Status:** {status_chip}")

        enable_toggle = st.checkbox(
            "Securely save my chats",
            value=status_on,
            help="When enabled, new messages will be saved to your private account storage (optional, you control it)."
        )

        if enable_toggle and not st.session_state.get('persist_confirmed', False):
            st.info("To enable storage, please confirm that you're okay with saving your chats to your private account storage.")
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("I consent"):
                    st.session_state['persist_confirmed'] = True
                    st.session_state['persist_history'] = True
                    st.rerun()
            with c2:
                if st.button("Not now"):
                    st.session_state['persist_confirmed'] = False
                    st.session_state['persist_history'] = False
                    st.rerun()
        else:
            st.session_state['persist_history'] = bool(enable_toggle and st.session_state.get('persist_confirmed', False))

        st.caption("Stored fields: user_id, username, your message, assistant reply, processing time, mode, timestamp.")

        # Group server-side deletion under the same expander
        if st.session_state.get('persist_confirmed', False) and st.session_state.get('user_id'):
            if not st.session_state.get('clear_server_history_pending'):
                if st.button('Delete my server history'):
                    st.session_state['clear_server_history_pending'] = True
                    st.rerun()
            else:
                st.warning('This will permanently delete your persisted messages for your account.')
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button('Confirm delete'):
                        success, msg = delete_user_history_from_supabase(str(st.session_state.get('user_id', '')))
                        if success:
                            st.success('Server-side history deleted.')
                        else:
                            st.error('Failed to delete server history. Please try again later.')
                        st.session_state['clear_server_history_pending'] = False
                        st.rerun()
                with col_b:
                    if st.button('Cancel'):
                        st.session_state['clear_server_history_pending'] = False
                        st.rerun()
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
            st.sidebar.download_button('Download JSON', _json.dumps(st.session_state[conversation_key], indent=2), file_name=f'history_{st.session_state.get("user_id","anon")}.json')
        except Exception:
            st.sidebar.error('Failed to prepare history download')
    # Check if user is authenticated
    if st.session_state.get('authenticated', False):
        render_main_app()
    else:
        render_splash_interface(auth)

if __name__ == "__main__":
    main()
