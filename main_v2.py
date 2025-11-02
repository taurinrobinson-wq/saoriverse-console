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
    page_icon="graphics/FirstPerson-Logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Sidebar controls for integrations
    st.sidebar.markdown("## Integrations")
    enable_limbic = st.sidebar.checkbox("Enable Limbic-Adjacent Integration", value=st.session_state.get('enable_limbic', False))
    st.session_state['enable_limbic'] = enable_limbic

    # Initialize limbic engine if requested and available
    if enable_limbic and HAS_LIMBIC and 'limbic_engine' not in st.session_state:
        try:
            st.session_state['limbic_engine'] = LimbicIntegrationEngine()
            st.sidebar.success("Limbic engine initialized")
        except Exception as e:
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

    # A/B test opt-in
    participate_ab = st.sidebar.checkbox("Participate in Limbic A/B test", value=st.session_state.get('ab_participate', False))
    st.session_state['ab_participate'] = participate_ab

    # Sidebar: Conversation history (replace demo panel)
    st.sidebar.markdown("---")
    # Optional persistence toggle (opt-in)
    persist_history = st.sidebar.checkbox(
        "Persist history to Supabase (opt-in)",
        value=st.session_state.get('persist_history', False),
        help="When enabled, new messages will be stored in your Supabase project's `conversation_history` table."
    )

    # Consent flow: require explicit confirmation
    if persist_history and not st.session_state.get('persist_confirmed', False):
        st.sidebar.markdown("**Confirm consent**: Persisting messages off-device stores your message content on your Supabase project. Do you consent to this for this account?")
        if st.sidebar.button("Confirm persist"):
            st.session_state['persist_confirmed'] = True
            st.session_state['persist_history'] = True
            st.experimental_rerun()
        if st.sidebar.button("Cancel"):
            st.session_state['persist_confirmed'] = False
            st.session_state['persist_history'] = False
            st.experimental_rerun()
    else:
        st.session_state['persist_history'] = bool(persist_history and st.session_state.get('persist_confirmed', False))

    # Provide a short explanation and quick link/details for data stored and how to delete it
    with st.sidebar.expander("What is stored & how to delete it", expanded=False):
        st.markdown(
            "When you opt in to persist conversation history, the following fields are stored in your Supabase project under the `conversation_history` table:\n\n" \
            "• user_id — your local identifier (text)\n" \
            "• username — your display name (text)\n" \
            "• user_message — the message you submitted (text)\n" \
            "• assistant_reply — the model's response (text)\n" \
            "• processing_time — how long the message took to process (text)\n" \
            "• mode — processing mode used (e.g. hybrid/local/ai_preferred)\n" \
            "• timestamp — server timestamp when the row was created\n\n"
        )
        st.markdown("To delete your stored messages from the server: enable the persistence consent, then use the 'Clear Server History' button in the sidebar. This performs a best-effort delete via the Supabase REST API and will remove rows matching your `user_id`.")
        st.markdown("I've also included an example SQL DDL in `sql/create_conversation_history_tables.sql` that shows a recommended table schema plus a `conversation_deletion_audit` table to record deletion requests.")
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
                st.experimental_rerun()
        with cols[1]:
            if st.button("Resend", key=f"resend_{orig_idx}"):
                # Mark for auto-processing and set recalled text
                st.session_state['recalled_message'] = exch.get('user', '')
                st.session_state['auto_process'] = True
                st.experimental_rerun()

    # Compact controls for history export/clear
    st.sidebar.markdown('---')
    if st.sidebar.button('Clear Local History'):
        st.session_state[conversation_key] = []
        st.experimental_rerun()
    if st.sidebar.button('Download History'):
        try:
            import json as _json
            st.sidebar.download_button('Download JSON', _json.dumps(st.session_state[conversation_key], indent=2), file_name=f'history_{st.session_state.get("user_id","anon")}.json')
        except Exception:
            st.sidebar.error('Failed to prepare history download')
    # Allow the user to declare which emotional states they'd like the system to actively capture
    default_emotions = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"]
    captured = st.sidebar.multiselect(
        "Capture emotional states (rollout)",
        default_emotions,
        default=st.session_state.get('captured_emotions', default_emotions),
        help="Select the emotional states you want the limbic system to actively capture and map."
    )
    st.session_state['captured_emotions'] = captured
    # Server-side clear (consent required)
    if st.session_state.get('persist_confirmed', False) and st.session_state.get('user_id'):
        if st.sidebar.button('Clear Server History'):
            st.session_state['clear_server_history_pending'] = True
            st.experimental_rerun()

        if st.session_state.get('clear_server_history_pending'):
            st.sidebar.markdown('**Confirm server-side deletion of your persisted conversation history**')
            if st.sidebar.button('Confirm Delete Server History'):
                success, msg = delete_user_history_from_supabase(st.session_state.get('user_id'))
                if success:
                    st.sidebar.success('Server-side history deleted.')
                else:
                    st.sidebar.error(f'Failed to delete server history: {msg}')
                st.session_state['clear_server_history_pending'] = False
                st.experimental_rerun()
            if st.sidebar.button('Cancel Delete'):
                st.session_state['clear_server_history_pending'] = False
                st.experimental_rerun()
    # Check if user is authenticated
    if st.session_state.get('authenticated', False):
        render_main_app()
    else:
        render_splash_interface(auth)

if __name__ == "__main__":
    main()
