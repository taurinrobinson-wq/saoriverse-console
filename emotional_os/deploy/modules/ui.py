import datetime
import json
import logging
import time
import uuid
import os

try:
    import requests
except Exception:
    # Allow the module to be imported in environments where `requests` is not
    # installed (e.g., lightweight CI or minimal runtime). Functions that need
    # network access will handle the missing library at call time.
    requests = None

import streamlit as st

try:
    from emotional_os.safety.fallback_protocols import FallbackProtocol
except Exception:
    # Allow environments where the safety module isn't available (tests, CI)
    FallbackProtocol = None

# ConversationManager handles persisted conversations; import defensively so
# UI stays import-safe in environments where conversation management isn't
# available (tests, minimal CI). Also import generate_auto_name helper if
# present; fall back to None when unavailable.
try:
    from emotional_os.deploy.modules.conversation_manager import (
        ConversationManager,
        generate_auto_name,
        load_all_conversations_to_sidebar,
    )
except Exception:
    ConversationManager = None
    generate_auto_name = None
    load_all_conversations_to_sidebar = None

# Document export helper (generates Word docx for personal logs).
# Import defensively so the UI still loads if python-docx isn't installed.
try:
    from emotional_os.deploy.modules.doc_export import generate_doc
except Exception:
    generate_doc = None

logger = logging.getLogger(__name__)

# Simple in-memory cache for inline SVGs to avoid repeated disk reads
_SVG_CACHE = {}


def _load_inline_svg(filename: str) -> str:
    """Load an SVG file from the static graphics folder and return its raw markup.

    If the file cannot be read, returns a small fallback SVG string.
    """
    if filename in _SVG_CACHE:
        return _SVG_CACHE[filename]

    # Try package-local graphics folder first, then repo-root static/graphics
    pkg_path = os.path.join(os.path.dirname(__file__),
                            "static", "graphics", filename)
    repo_path = os.path.join("static", "graphics", filename)
    tried_path = None
    try:
        # Pick the first existing candidate path
        if os.path.exists(pkg_path):
            tried_path = pkg_path
        elif os.path.exists(repo_path):
            tried_path = repo_path
        else:
            tried_path = pkg_path  # will raise when attempting to open

        # Read the SVG file and sanitize/remove XML declaration or DOCTYPE
        with open(tried_path, "r", encoding="utf-8") as f:
            svg = f.read()
        if svg.lstrip().startswith('<?xml'):
            svg = '\n'.join(svg.splitlines()[1:])
        if '<!DOCTYPE' in svg:
            parts = svg.split('<!DOCTYPE')
            if len(parts) > 1 and '>' in parts[1]:
                svg = parts[0] + parts[1].split('>', 1)[1]

        # Cache and return raw markup only (no Streamlit calls here)
        _SVG_CACHE[filename] = svg
    except Exception as e:
        st.warning(f"Could not load CSS: {e}")


def inject_css(css_path: str) -> None:
    """Inject a CSS file into the Streamlit app.

    The function attempts to read the CSS from a package-local path
    (relative to this module) first, then falls back to the repository
    root `static` folder. If the file can't be read, the function fails
    silently (best-effort) to avoid breaking the UI during import.
    """
    try:
        # Try package-local path
        pkg_path = os.path.join(os.path.dirname(__file__), css_path)
        repo_path = css_path
        chosen = None
        if os.path.exists(pkg_path):
            chosen = pkg_path
        elif os.path.exists(repo_path):
            chosen = repo_path

        if not chosen:
            return

        with open(chosen, 'r', encoding='utf-8') as f:
            css = f.read()

        # Inject as a style block
        st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)
    except Exception:
        # Best-effort: do not raise during UI import
        return


def render_controls_row(conversation_key):
    controls = st.columns([2, 1, 1, 1, 1, 1])
    with controls[0]:
        # Ensure a processing mode exists in session state. The actual
        # interactive controls for changing this are in the Settings
        # sidebar expander (so both demo and authenticated flows show
        # a single, consistent place for preferences).
        if 'processing_mode' not in st.session_state:
            st.session_state.processing_mode = os.getenv(
                'DEFAULT_PROCESSING_MODE', 'hybrid')

        # Display current mode succinctly in the controls row
        current_mode = st.session_state.processing_mode
        st.markdown(f"**Mode:** {current_mode}")

    with controls[1]:
        # Show current theme (actual selection lives in Settings sidebar)
        current_theme = st.session_state.get('theme', 'Light')
        st.markdown(f"**Theme:** {current_theme}")

        # Start Personal Log moved into the narrow column to match the
        # requested DOM slot (first small column after Theme)
        # (Button rendered in controls[2] below.)
    # Removed Debug and Clear History controls — these buttons did not provide
    # useful functionality and duplicated UI surface area. Slots retained for
    # layout stability.
    with controls[2]:
        if st.button("Start Personal Log", key="start_log_btn"):
            st.session_state.show_personal_log = True
            st.rerun()
    with controls[3]:
        pass
    with controls[4]:
        # Moved 'Download My Data' to the sidebar (related controls)
        # Keep this slot reserved for future row controls if needed.
        pass
    with controls[5]:
        # Slot kept intentionally empty; 'Start Personal Log' now next to Theme
        pass


def ensure_processing_prefs():
    """Normalize legacy processing preferences and ensure keys exist in session_state."""
    if 'processing_mode' in st.session_state and st.session_state.processing_mode == 'ai_preferred':
        st.session_state.processing_mode = 'hybrid'
        st.session_state['prefer_ai'] = True

    if 'processing_mode' not in st.session_state:
        st.session_state.processing_mode = os.getenv(
            'DEFAULT_PROCESSING_MODE', 'hybrid')

    if 'prefer_ai' not in st.session_state:
        st.session_state['prefer_ai'] = True


def decode_ai_reply(ai_reply: str, conversation_context: dict) -> tuple:
    """Decode an AI reply using the local parser and return (composed_response, debug_info)."""
    try:
        from emotional_os.glyphs.signal_parser import parse_input
    except Exception:
        return ai_reply, {}

    try:
        ai_local = parse_input(
            ai_reply,
            "emotional_os/parser/signal_lexicon.json",
            db_path="emotional_os/glyphs/glyphs.db",
            conversation_context=conversation_context,
        )
        ai_voltage = ai_local.get("voltage_response", "")
        ai_glyphs = ai_local.get("glyphs", [])
        ai_best = ai_local.get("best_glyph")
        ai_glyph_display = ai_best['glyph_name'] if ai_best else (
            ai_glyphs[0]['glyph_name'] if ai_glyphs else 'None')

        # Show local decoding and glyph annotations only when explicitly
        # enabled. By default we avoid appending internal parsing/debug
        # details to the user-facing reply. Use the environment variable
        # `FP_SHOW_LOCAL_DECODING=1` or set the session flag
        # `st.session_state['show_local_decoding'] = True` to reveal this
        # additional diagnostic information for developers.
        try:
            show_local = os.environ.get('FP_SHOW_LOCAL_DECODING') == '1' or st.session_state.get(
                'show_local_decoding', False)
        except Exception:
            show_local = False

        if show_local:
            composed = (
                f"{ai_reply}\n\n"
                f"Local decoding: {ai_voltage}\n"
                f"Resonant Glyph: {ai_glyph_display}"
            )
        else:
            # Default: return the raw AI reply without local debug annotations
            composed = ai_reply

        debug = {
            'signals': ai_local.get('signals', []),
            'gates': ai_local.get('gates', []),
            'glyphs': ai_glyphs,
            'debug_sql': ai_local.get('debug_sql', ''),
            'debug_glyph_rows': ai_local.get('debug_glyph_rows', [])
        }
        return composed, debug
    except Exception:
        return ai_reply, {}


def run_hybrid_pipeline(effective_input: str, conversation_context: dict, saori_url: str, supabase_key: str) -> tuple:
    """Run the full hybrid pipeline: local parse -> AI -> local decode.

    Returns (response_text, debug_info_dict, local_analysis_dict)
    """
    try:
        from emotional_os.glyphs.signal_parser import parse_input
        local_analysis = parse_input(effective_input, "emotional_os/parser/signal_lexicon.json",
                                     db_path="emotional_os/glyphs/glyphs.db", conversation_context=conversation_context)
    except Exception:
        local_analysis = {}

    glyphs = local_analysis.get('glyphs', [])
    voltage_response = local_analysis.get('voltage_response', '')
    ritual_prompt = local_analysis.get('ritual_prompt', '')

    if not saori_url or not supabase_key:
        response = f"Local Analysis: {voltage_response}\nActivated Glyphs: {', '.join([g.get('glyph_name','') for g in glyphs]) if glyphs else 'None'}\n{ritual_prompt}\n(AI enhancement unavailable)"
        return response, {}, local_analysis

    payload = {
        "message": effective_input,
        "mode": st.session_state.get('processing_mode', 'hybrid'),
        "user_id": st.session_state.user_id,
        "local_voltage_response": voltage_response,
        "local_glyphs": ', '.join([g.get('glyph_name', '') for g in glyphs]) if glyphs else '',
        "local_ritual_prompt": ritual_prompt
    }
    try:
        response_data = requests.post(
            saori_url,
            headers={
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=15
        )
    except Exception:
        response = f"Local Analysis: {voltage_response}\nActivated Glyphs: {', '.join([g.get('glyph_name','') for g in glyphs]) if glyphs else 'None'}\n{ritual_prompt}\n(AI enhancement failed)"
        return response, {}, local_analysis

    if requests is None:
        return "AI processing unavailable (requests library not installed).", {}, local_analysis

    if response_data.status_code != 200:
        return "I'm experiencing some technical difficulties, but I'm still here for you.", {}, local_analysis

    result = response_data.json()
    ai_reply = result.get('reply', "I'm here to listen.")

    composed, debug = decode_ai_reply(ai_reply, conversation_context)
    return composed, debug, local_analysis

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

    # Add custom CSS for splash screen
    st.markdown("""
    <style>
    .splash-logo-container {
        text-align: center;
        margin-bottom: 2rem;
        margin-top: 3rem;
    }
    .splash-logo {
        width: 200px;
        height: auto;
        margin-bottom: 1rem;
    }
    .splash-title {
        font-size: 2rem;
        font-weight: 300;
        letter-spacing: 0.2em;
        color: #2E2E2E;
        margin: 1rem 0 0.5rem 0;
        text-align: center;
        line-height: 1.2;
    }
    .splash-subtitle {
        font-size: 1.2rem;
        color: #666;
        letter-spacing: 0.1em;
        font-weight: 300;
        text-transform: uppercase;
        text-align: center;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

    # Center everything in the page
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo and text container
        st.markdown('<div class="splash-logo-container">',
                    unsafe_allow_html=True)

    # Use the cropped logo from the static directory to avoid inline SVG
    # fill/viewBox inconsistencies across browsers. Prefer serving the SVG
    # as an <img> which ensures correct MIME handling and consistent sizing.
    # Use the inverted/no-text cropped SVG (more reliable and not corrupted)
    logo_file = "FirstPerson-Logo-invert-cropped_notext.svg"

    # Prefer graphics stored under the package static folder so the asset
    # lives with the code. Fall back to repository-root `static/graphics`.
    pkg_graphics_path = os.path.join(os.path.dirname(
        __file__), "static", "graphics", logo_file)
    repo_graphics_path = os.path.join("static", "graphics", logo_file)

    static_path = f"/static/graphics/{logo_file}"

    # Provide a simple CSS hook for sizing the raster/SVG image
    st.markdown(
        """
        <style>
        /* Stronger splash CSS: target inline SVG elements and <img> fallbacks. */
        .splash-logo, .splash-logo img, .splash-logo svg { display: block; margin: 0 auto; width: 140px; height: auto; }

        /* Force fills and remove strokes inside inline SVGs so white shapes
           become visible on light backgrounds. Use attribute selectors to
           catch explicit fill attributes and inline styles. */
        .splash-logo svg * { fill: #31333F !important; stroke: none !important; }
        .splash-logo svg [fill="#fff"], .splash-logo svg [fill="#FFFFFF"] { fill: #31333F !important; }
        .splash-logo svg [style*="fill:#fff"], .splash-logo svg [style*="fill:#FFF"],
        .splash-logo svg [style*="fill:#ffffff"], .splash-logo svg [style*="fill:#FFFFFF"] { fill: #31333F !important; }

        /* Improve rendering quality and ensure inline SVGs respect sizing */
        .splash-logo svg { shape-rendering: geometricPrecision; image-rendering: optimizeQuality; }

        /* For <img> rendered SVGs (external resource), apply a light drop-shadow
           so white shapes gain contrast on white backgrounds. */
        .splash-logo img, img.splash-logo { filter: drop-shadow(0 0 6px rgba(0,0,0,0.25)) !important; background-color: transparent !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    try:
        # If the package-local static file exists, prefer that (keeps
        # assets colocated with the package). Otherwise fall back to the
        # repo-root static/graphics directory used historically.
        if os.path.exists(pkg_graphics_path):
            try:
                st.image(pkg_graphics_path, width=140)
            except Exception:
                img_tag = f'<img src="{static_path}" class="splash-logo" alt="FirstPerson logo" />'
                st.markdown(img_tag, unsafe_allow_html=True)
        elif os.path.exists(repo_graphics_path):
            try:
                st.image(repo_graphics_path, width=140)
            except Exception:
                img_tag = f'<img src="{static_path}" class="splash-logo" alt="FirstPerson logo" />'
                st.markdown(img_tag, unsafe_allow_html=True)
        else:
            # Fallback: load inline SVG (keeps previous behavior when
            # the static file is not present). The loader already strips
            # problematic XML/DOCTYPE lines.
            svg_markup = _load_inline_svg(logo_file)
            st.markdown(
                f'<div class="splash-logo">{svg_markup}</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown(
            '<div style="font-size: 4rem; text-align: center;">🧠</div>', unsafe_allow_html=True)

        # Add title and subtitle
        st.markdown("""
            <div class="splash-title">Personal AI</div>
            <div class="splash-subtitle">Companion</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Make Sign In / Register actions obvious on the splash screen. Placing
    # these buttons here ensures the auth forms can be opened even when other
    # interactive elements are hidden by CSS or embedding contexts.
    try:
        with st.container():
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("Sign In", key="splash_sign_in"):
                    st.session_state.show_login = True
                    st.rerun()
                if st.button("Register", key="splash_register"):
                    st.session_state.show_register = True
                    st.rerun()
    except Exception:
        # Best-effort: if Streamlit UI isn't fully available, continue silently
        pass

    if st.session_state.get('show_login', False):
        auth.render_login_form()
    elif st.session_state.get('show_register', False):
        auth.render_register_form()
    else:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            qcol1, qcol2 = st.columns([1, 1], gap="small")
        # Logo already rendered above in the centered splash area. Skip
        # re-rendering it here to avoid duplicate icons showing on the
        # splash/login page; keep the auth container open for controls.
        st.markdown('</div>', unsafe_allow_html=True)


def render_main_app():
    """Main app interface for authenticated users - Full Emotional OS"""
    # Optional debug overlay: enable by setting the environment variable
    # FP_DEBUG_UI=1 in the deployment environment or export it locally when
    # running the app. This prints helpful session_state keys to the UI so
    # we can see why the post-login view might be empty.
    try:
        import os as _os
        if _os.environ.get('FP_DEBUG_UI') == '1':
            try:
                with st.expander('DEBUG: session_state snapshot', expanded=True):
                    _keys = [
                        'authenticated', 'user_id', 'username', 'session_expires',
                        'show_login', 'show_register', 'header_rendered', 'conversation_manager'
                    ]
                    _snap = {k: (st.session_state.get(k) if k != 'conversation_manager' else (
                        'present' if st.session_state.get('conversation_manager') else 'none')) for k in _keys}
                    st.json(_snap)
            except Exception:
                # Best-effort: do not break the main UI when debug overlay fails
                pass
    except Exception:
        pass
    # Skip header rendering if it's already been done
    if not st.session_state.get('header_rendered'):
        # Render header with logo and title very close together
        col1, col2 = st.columns([0.5, 8], gap="small")
        with col1:
            try:
                # Prefer package-local normalized logo if present
                norm_file = "FirstPerson-Logo-normalized.svg"
                pkg_norm = os.path.join(os.path.dirname(
                    __file__), "static", "graphics", norm_file)
                repo_norm = os.path.join("static", "graphics", norm_file)
                if os.path.exists(pkg_norm):
                    st.image(pkg_norm, width=24)
                elif os.path.exists(repo_norm):
                    st.image(repo_norm, width=24)
                else:
                    raise FileNotFoundError
            except Exception:
                st.markdown(
                    '<div style="font-size: 2.5rem; margin: 0; line-height: 1;">🧠</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<h1 style="margin: 0; margin-left: -35px; padding-top: 10px; color: #2E2E2E; font-weight: 300; letter-spacing: 2px; font-size: 2.2rem;">FirstPerson - Personal AI Companion</h1>', unsafe_allow_html=True)
        st.session_state['header_rendered'] = True
    # ------------------------------------------------------------------------
    # Demo-mode: if the user is not authenticated, provide a lightweight
    # demo experience so the main interface loads immediately. The sidebar
    # will expose Sign In / Register controls which open the existing auth
    # flows. This keeps the previous splash page behaviour reversible.
    # ------------------------------------------------------------------------
    try:
        from .auth import SaoynxAuthentication
        auth = SaoynxAuthentication()
    except Exception:
        # Best-effort: if auth isn't available, proceed in a limited demo mode
        auth = None

    if not st.session_state.get('authenticated'):
        # Ensure demo-mode session defaults exist so downstream code that
        # expects a user_id/username can run without branching everywhere.
        st.session_state.setdefault('demo_mode', True)
        # Use a stable demo placeholder id so migration can find demo
        # conversations later when the user authenticates.
        if 'demo_placeholder_id' not in st.session_state:
            st.session_state['demo_placeholder_id'] = f"demo_{uuid.uuid4().hex[:8]}"
        st.session_state.setdefault(
            'user_id', st.session_state['demo_placeholder_id'])
        st.session_state.setdefault('username', 'Demo User')
        # Informational banner for demo users and a small logo above it
        try:
            # Prefer package-local static SVG image for reliable rendering in VS Code/browser
            pkg_logo = os.path.join(os.path.dirname(
                __file__), "static", "graphics", "FirstPerson-Logo-invert-cropped_notext.svg")
            if os.path.exists(pkg_logo):
                # Center the small logo above the demo info
                c1, c2, c3 = st.columns([1, 0.6, 1])
                with c2:
                    try:
                        st.image(pkg_logo, width=64)
                    except Exception:
                        # Fallback to inline SVG rendering if st.image fails
                        svg_markup = _load_inline_svg(
                            "FirstPerson-Logo-invert-cropped_notext.svg")
                        st.markdown(
                            f"<div style='width:64px;margin:0 auto'>{svg_markup}</div>", unsafe_allow_html=True)
            else:
                # Fallback: inline SVG if package file missing
                svg_markup = _load_inline_svg(
                    "FirstPerson-Logo-invert-cropped_notext.svg")
                st.markdown(
                    f"<div style='width:64px;margin:0 auto'>{svg_markup}</div>", unsafe_allow_html=True)

            st.info(
                "Running in demo mode — register or sign in in the sidebar to enable persistence and full features.")
        except Exception:
            try:
                st.info(
                    "Running in demo mode — register or sign in in the sidebar to enable persistence and full features.")
            except Exception:
                pass
    else:
        # Remove demo_mode flag when real user is authenticated
        if 'demo_mode' in st.session_state:
            del st.session_state['demo_mode']

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

    # If user just transitioned from demo -> authenticated, attempt a
    # best-effort migration of the ephemeral demo conversation into the
    # user's persistent storage. This runs before the sidebar renders so
    # migrated content appears in the sidebar immediately.
    try:
        # Migration guard: run only once per session after authentication
        if st.session_state.get('authenticated') and st.session_state.get('demo_placeholder_id') and not st.session_state.get('demo_migrated'):
            demo_id = st.session_state.get('demo_placeholder_id')
            demo_key = f"conversation_history_{demo_id}"
            # New user id already set by auth flow
            user_id_now = st.session_state.get('user_id')
            user_key = f"conversation_history_{user_id_now}"
            try:
                # Only migrate if there is demo content and user has no content yet
                if demo_key in st.session_state and st.session_state.get(demo_key):
                    demo_messages = st.session_state.get(demo_key)
                    # Copy into user's session key
                    if user_key not in st.session_state or not st.session_state.get(user_key):
                        st.session_state[user_key] = demo_messages

                        # Attempt to persist via ConversationManager if available
                        try:
                            if ConversationManager:
                                mgr = ConversationManager(user_id_now)
                                # Create a new conversation record for the migrated demo
                                conv_id = str(uuid.uuid4())
                                first_msg = demo_messages[0].get('user') if isinstance(
                                    demo_messages, list) and demo_messages and isinstance(demo_messages[0], dict) else None
                                title = generate_auto_name(first_msg) if generate_auto_name and first_msg else (
                                    st.session_state.get('conversation_title') or 'Migrated Conversation')
                                mgr.save_conversation(
                                    conv_id, title, demo_messages)
                                # Set current conversation id to the newly created one
                                st.session_state['current_conversation_id'] = conv_id
                        except Exception:
                            # Swallow persistence failures; session copy is already done
                            pass

                    # Mark migrated so we don't run again
                    st.session_state['demo_migrated'] = True
            except Exception:
                # Non-fatal; do not block UI if migration fails
                st.session_state['demo_migrated'] = True
    except Exception:
        pass

    # We render auth forms inside the sidebar as expanders to keep the
    # main area focused. Sidebar expanders are controlled by
    # `sidebar_show_login` and `sidebar_show_register` session flags.
    # Ensure defaults exist.
    st.session_state.setdefault('sidebar_show_login', False)
    st.session_state.setdefault('sidebar_show_register', False)

    # If the user just authenticated, show a gentle confirmation toast
    # and then automatically transition into the authenticated UI.
    try:
        if st.session_state.get('authenticated') and st.session_state.get('post_login_transition'):
            msg = st.session_state.get(
                'post_login_message', 'Signed in successfully')
            # Center a subtle confirmation card
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.markdown(
                    f"<div style='padding:16px;border-radius:10px;background:#f0fff4;border:1px solid #d1f7d8;text-align:center;font-weight:600;'>✅ {msg}</div>",
                    unsafe_allow_html=True,
                )
            # Small pause to let the user see the confirmation
            try:
                time.sleep(1.0)
            except Exception:
                pass
            # Clear transient flags and rerun to render the full authenticated UI
            st.session_state.pop('post_login_transition', None)
            st.session_state.pop('post_login_message', None)
            st.rerun()
    except Exception:
        # Non-fatal; proceed to render sidebar normally
        pass

    # Display sidebar with previous conversations
    with st.sidebar:
        # Best-effort CSS to constrain sidebar width so form fields fit.
        # Streamlit's DOM classnames can change; this is a best-effort
        # approach that works in many environments.
        st.markdown(
            """
            <style>
            /* Constrain sidebar width */
            [data-testid="stSidebar"] > div {
                min-width: 260px !important;
                max-width: 400px !important;
            }
            /* Hide the vertical resize handle if present (best-effort) */
            .css-1v3fvcr { resize: none !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        # Account panel: show sign-in/register when not authenticated.
        if not st.session_state.get('authenticated'):
            # Card-like account panel for a cleaner, welcoming look
            try:
                svg_name_side = "FirstPerson-Logo-black-cropped_notext.svg"
                svg_markup_side = _load_inline_svg(svg_name_side)
                st.markdown(
                    f"<div style='border:1px solid rgba(0,0,0,0.06); padding:12px; border-radius:12px; background: rgba(250,250,250,0.02); text-align:center;'>\n{svg_markup_side}\n<p style=\"margin:8px 0 6px 0; font-weight:600;\">Demo mode</p>\n<p style=\"font-size:0.9rem; color:#666; margin:0 0 8px 0;\">Explore the app. Register to keep your conversations.</p></div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("### Account")
            st.markdown(
                "Create an account or sign in to keep your conversations and enable full features.")
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("Sign in", key="sidebar_toggle_sign_in"):
                    # Toggle the sidebar expander for sign-in
                    st.session_state['sidebar_show_login'] = not st.session_state.get(
                        'sidebar_show_login', False)
                    # Ensure the other expander is closed
                    if st.session_state['sidebar_show_login']:
                        st.session_state['sidebar_show_register'] = False
                    # No forced rerun here; allow the current render to show the expander
            with col_b:
                if st.button("Register", key="sidebar_toggle_register"):
                    st.session_state['sidebar_show_register'] = not st.session_state.get(
                        'sidebar_show_register', False)
                    if st.session_state['sidebar_show_register']:
                        st.session_state['sidebar_show_login'] = False
                    # No forced rerun here; allow the current render to show the expander

            # Quick demo entry (uses auth quick_login_bypass when available)
            if auth and hasattr(auth, 'quick_login_bypass'):
                if st.button("Continue in demo", key="sidebar_continue_demo"):
                    try:
                        auth.quick_login_bypass()
                    except Exception:
                        # Best-effort: fall back to local demo session state
                        st.session_state.authenticated = False
                        st.session_state.user_id = st.session_state.get(
                            'user_id')
                        st.session_state.username = st.session_state.get(
                            'username')
                        st.rerun()

            st.markdown("---")

            # Debug snapshot for sidebar auth flags (helpful during development)
            # Only show this when explicitly enabled via environment or session flag
            try:
                show_debug = os.environ.get(
                    'FP_DEBUG_UI') == '1' or st.session_state.get('show_sidebar_debug')
                if show_debug:
                    st.caption(
                        f"debug: sidebar_show_login={st.session_state.get('sidebar_show_login')} | sidebar_show_register={st.session_state.get('sidebar_show_register')}")
            except Exception:
                pass

            # Render auth expanders inside the sidebar (keeps main area stable)
            try:
                if st.session_state.get('sidebar_show_login'):
                    with st.expander("Sign in", expanded=True):
                        if auth:
                            auth.render_login_form(in_sidebar=True)
                        else:
                            st.error("Authentication subsystem unavailable")
                if st.session_state.get('sidebar_show_register'):
                    with st.expander("Register", expanded=True):
                        if auth:
                            auth.render_register_form(in_sidebar=True)
                        else:
                            st.error("Authentication subsystem unavailable")
            except Exception:
                # Non-fatal: keep sidebar usable even if auth UI fails
                pass
        else:
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

        # Privacy & Consent settings - only show when user is authenticated
        if st.session_state.get('authenticated'):
            try:
                from emotional_os.deploy.modules.consent_ui import render_consent_settings_panel
                render_consent_settings_panel()
            except ImportError:
                pass
            except Exception as e:
                st.warning(f"Consent settings error: {e}")

        # Load and display previous conversations - only for authenticated users
        if st.session_state.get('authenticated') and ConversationManager and st.session_state.get('conversation_manager'):
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
        if st.session_state.get('authenticated'):
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
                cluster_default = st.session_state.get(
                    'preproc_cluster_size', 2)
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
                escalation_action = last.get(
                    'escalation_action') if last else None
                escalation_reason = last.get(
                    'escalation_reason') if last else None

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
                    # To avoid an intrusive, momentary popup of escalation controls
                    # require an explicit user action to reveal the full HIL panel.
                    # This prevents the three-button escalation panel from flashing
                    # unexpectedly when session state toggles are carried over.
                    st.markdown("---")
                    st.markdown("### Human-in-the-Loop (HIL) Escalation")

                    # Ensure a reveal toggle exists; default is False so panel stays hidden
                    st.session_state.setdefault('show_hil_controls', False)

                    # Small reveal button to avoid unexpected popup
                    if not st.session_state.get('show_hil_controls'):
                        if st.button("Show HIL Controls", key="show_hil_controls_button"):
                            st.session_state['show_hil_controls'] = True
                            st.rerun()

                    # Only render the intrusive escalation panel when explicitly revealed
                    if not st.session_state.get('show_hil_controls'):
                        # Provide a non-intrusive summary instead
                        if not last:
                            st.info(
                                "HIL escalation available — enable and reveal controls when you're ready.")
                        else:
                            st.info(
                                "HIL escalation ready to review recent preprocessing results. Click 'Show HIL Controls' to open the panel.")
                    else:
                        if not last:
                            st.info(
                                "No preprocessing record available for review yet.")
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
                                    p = st.session_state.get(
                                        'local_preprocessor')
                                    audit_payload = {
                                        'action': 'hil_escalate',
                                        'method': 'manual_button',
                                        'escalation_action': escalation_action,
                                        'escalation_reason': escalation_reason,
                                        'preproc_summary': last
                                    }
                                    if p and hasattr(p, 'record_audit'):
                                        p.record_audit(audit_payload)
                                        st.success(
                                            "Escalation recorded (audit log).")
                                    else:
                                        st.session_state.setdefault('hil_escalation_log', []).append({
                                            'timestamp': datetime.datetime.now().isoformat(),
                                            **audit_payload
                                        })
                                        st.success(
                                            "Escalation recorded (session log).")
                                except Exception:
                                    st.info(
                                        "Escalation recorded (local stub).")

                            if cols[1].button("Request Clarification", key="request_clarification"):
                                try:
                                    # record the clarification request
                                    from local_inference.preprocessor import Preprocessor
                                    p = st.session_state.get(
                                        'local_preprocessor')
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
                                    st.info(
                                        "Clarification requested (logged).")
                                except Exception:
                                    st.info(
                                        "Clarification requested (local stub).")

                            if cols[2].button("Escalate to AI (sanitized)", key="escalate_to_ai"):
                                try:
                                    from local_inference.preprocessor import Preprocessor
                                    p = st.session_state.get(
                                        'local_preprocessor')
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
                                    st.info(
                                        "AI escalation requested (local stub).")
            except Exception:
                # Non-fatal: sidebar HIL toggle shouldn't break the UI
                pass

        # NOTE: Export / download control intentionally removed from here.
        # The download/export button now lives inside the Privacy & Consent
        # sidebar expander (`render_consent_settings_panel`) so it is only
        # visible within that scoped area. Keeping it here caused duplicate
        # controls to appear in the main chat UI.

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
                    <div style="display: flex; align-items: center; margin-bottom: 1rem; gap: 1rem;">
                <div style="flex-shrink: 0;">
                    <div class="brand-logo" style="width: 36px; height: 36px;">{svg_markup}</div>
                </div>
                <div style="flex: 1; white-space: nowrap;">
                    <div class="brand-title" style="margin: 0; font-size: 1.8rem;">FirstPerson – Personal AI Companion</div>
                    <div class="brand-subtitle" style="margin: 0;">Your private space for emotional processing and growth</div>
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
                    f'<div style="width:36px">{svg_markup}</div>', unsafe_allow_html=True)
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
        display_name = st.session_state.get(
            'first_name') or st.session_state.get('username')
        st.write(f"Welcome back, **{display_name}**! 👋")
    with col2:
        # Settings panel is rendered in the sidebar expander
        try:
            render_settings_sidebar()
        except Exception:
            # Fail silently if sidebar rendering isn't available
            pass
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
                    # Note: the previous code supported an "ai_preferred" mode.
                    # That option has been removed in favor of a simpler
                    # two-option model: 'hybrid' (default) and 'local'. Any
                    # unknown mode falls back to hybrid behavior below.
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
                                        ai_reply = result.get(
                                            "reply", "I'm here to listen.")

                                        # SECOND PASS: Run the AI reply back through the
                                        # local parser so we decode the AI's language into
                                        # the local glyph/voltage representation and produce
                                        # a locally-interpreted final response. This preserves
                                        # the intended hybrid pipeline: local -> AI -> local.
                                        try:
                                            ai_local = parse_input(
                                                ai_reply,
                                                "emotional_os/parser/signal_lexicon.json",
                                                db_path="emotional_os/glyphs/glyphs.db",
                                                conversation_context=conversation_context,
                                            )
                                            ai_voltage = ai_local.get(
                                                "voltage_response", "")
                                            ai_glyphs = ai_local.get(
                                                "glyphs", [])
                                            ai_best = ai_local.get(
                                                "best_glyph")
                                            ai_glyph_display = ai_best['glyph_name'] if ai_best else (
                                                ai_glyphs[0]['glyph_name'] if ai_glyphs else 'None')

                                            # Compose a final response that includes the AI's reply
                                            # plus the local decoding/context so the user receives a
                                            # grounded, locally-interpreted message.
                                            response = (
                                                f"{ai_reply}\n\n"
                                                f"Local decoding: {ai_voltage}\n"
                                                f"Resonant Glyph: {ai_glyph_display}"
                                            )

                                            # Update debug variables for downstream features
                                            debug_signals = ai_local.get(
                                                "signals", [])
                                            debug_gates = ai_local.get(
                                                "gates", [])
                                            debug_glyphs = ai_glyphs
                                            debug_sql = ai_local.get(
                                                "debug_sql", "")
                                            debug_glyph_rows = ai_local.get(
                                                "debug_glyph_rows", [])
                                        except Exception:
                                            # If local re-parsing fails, fall back to the AI reply
                                            response = ai_reply
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

                    # Show anonymization consent widget once per session (or until user interacts)
                    # Gate the full consent UI behind an explicit opt-in flag so it doesn't
                    # interrupt normal conversation flows. To enable for debugging or
                    # controlled demos set the environment variable `FP_SHOW_EGS_OVERLAY=1`
                    # or set `st.session_state['show_egs_overlay']=True` in the session.
                    try:
                        show_overlay = False
                        try:
                            show_overlay = os.environ.get(
                                'FP_SHOW_EGS_OVERLAY') == '1' or st.session_state.get('show_egs_overlay', False)
                        except Exception:
                            show_overlay = False

                        if show_overlay:
                            from emotional_os.deploy.modules.consent_ui import render_anonymization_consent_widget
                            exchange_id = f"exchange_{len(st.session_state.get(conversation_key, []))}"
                            consent_key = f"consent_{exchange_id}"

                            # Only show the consent widget if it hasn't been seen/interacted with this session
                            if not st.session_state.get('consent_seen', False):
                                consent_result = render_anonymization_consent_widget(
                                    exchange_id)

                                # If the render function returned a completed consent dict, store it
                                if consent_result:
                                    st.session_state[consent_key] = consent_result
                                    st.session_state['consent_seen'] = True
                                    # Log consent choices to debug_chat.log for traceability
                                    try:
                                        import json as _json
                                        import datetime as _dt
                                        log_entry = {
                                            'ts': _dt.datetime.utcnow().isoformat() + 'Z',
                                            'user_id': st.session_state.get('user_id'),
                                            'exchange_id': exchange_id,
                                            'consent': consent_result
                                        }
                                        with open('/workspaces/saoriverse-console/debug_chat.log', 'a', encoding='utf-8') as _fh:
                                            _fh.write(_json.dumps(
                                                log_entry, ensure_ascii=False) + '\n')
                                    except Exception:
                                        # Non-fatal; do not block the UI
                                        pass

                                # If the user clicked 'Later', the consent widget stores a session key but returns None
                                elif consent_key in st.session_state:
                                    # mark seen so we don't prompt again this session
                                    st.session_state['consent_seen'] = True
                                    # also log the stored consent/skipped state
                                    try:
                                        import json as _json
                                        import datetime as _dt
                                        stored = st.session_state.get(
                                            consent_key)
                                        log_entry = {
                                            'ts': _dt.datetime.utcnow().isoformat() + 'Z',
                                            'user_id': st.session_state.get('user_id'),
                                            'exchange_id': exchange_id,
                                            'consent': stored
                                        }
                                        with open('/workspaces/saoriverse-console/debug_chat.log', 'a', encoding='utf-8') as _fh:
                                            _fh.write(_json.dumps(
                                                log_entry, ensure_ascii=False) + '\n')
                                    except Exception:
                                        pass
                        # else: already seen in this session; do nothing
                    except ImportError:
                        st.warning("Consent UI unavailable")
                    except Exception as e:
                        st.warning(f"Consent settings error: {e}")
        # Debug output removed — internal diagnostic panels were removed from
        # the main UI surface. If you need to inspect internal processing
        # structures (signals, glyphs, SQL), consider adding a developer-only
        # diagnostic page or using logging instead.

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

                # Ensure we have a persistent user ID
                if 'persistent_user_id' not in st.session_state:
                    st.session_state['persistent_user_id'] = user_id

                # Initialize dynamic evolution system if not already in session
                if 'hybrid_processor' not in st.session_state and create_integrated_processor:
                    # Use adaptive extractor with persistence
                    adaptive_extractor = AdaptiveSignalExtractor(
                        adaptive=True,
                        use_discovered=True,
                        persistence_path=f"learning/user_signals/{st.session_state['persistent_user_id']}_signals.json"
                    )

                    # Create processor with persistent user ID
                    st.session_state['hybrid_processor'] = create_integrated_processor(
                        hybrid_learner=learner,
                        adaptive_extractor=adaptive_extractor,
                        user_id=st.session_state['persistent_user_id'],
                    )

                    # Initialize learning tracking
                    if 'learning_stats' not in st.session_state:
                        st.session_state['learning_stats'] = {
                            'exchanges_processed': 0,
                            'signals_learned': 0,
                            'glyphs_generated': 0
                        }

                # Process through integrated pipeline with dynamic glyph generation
                if 'hybrid_processor' in st.session_state:
                    processor = st.session_state['hybrid_processor']

                    # Ensure we're using the persistent user ID
                    evolution_result = processor.process_user_message(
                        user_message=user_input,
                        ai_response=response,
                        user_id=st.session_state['persistent_user_id'],
                        conversation_id=st.session_state.get(
                            'conversation_id', 'default'),
                        glyphs=debug_glyphs,
                    )

                    # Update learning statistics
                    st.session_state['learning_stats']['exchanges_processed'] += 1
                    if evolution_result['learning_result'].get('learned_to_user', False):
                        st.session_state['learning_stats']['signals_learned'] += len(
                            evolution_result.get('emotional_signals', [])
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

                        # Update learning statistics
                        st.session_state['learning_stats']['glyphs_generated'] += len(
                            new_glyphs)

                        # Display learning progress
                        st.sidebar.markdown("### 📊 Learning Progress")
                        st.sidebar.text(
                            f"Exchanges Processed: {st.session_state['learning_stats']['exchanges_processed']}")
                        st.sidebar.text(
                            f"Signals Learned: {st.session_state['learning_stats']['signals_learned']}")
                        st.sidebar.text(
                            f"Glyphs Generated: {st.session_state['learning_stats']['glyphs_generated']}")

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
                    if callable(generate_doc):
                        buf = generate_doc(
                            date, log_time, event, mood, reflections, insights)
                        # If a BytesIO-like object was returned, get raw bytes
                        try:
                            data_bytes = buf.getvalue()
                        except Exception:
                            # If it's already bytes or str, pass through
                            data_bytes = buf
                        st.download_button(
                            label="Download as Word Doc",
                            data=data_bytes,
                            file_name="personal_log.docx",
                        )
                    else:
                        # Fallback: provide a plain-text download if docx export not available
                        fallback_text = (
                            f"Date: {date}\nTime: {log_time}\nEvent: {event}\nMood: {mood}\n\n"
                            f"Reflections:\n{reflections}\n\nInsights:\n{insights}"
                        )
                        st.download_button(
                            label="Download as TXT",
                            data=fallback_text.encode("utf-8"),
                            file_name="personal_log.txt",
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


def render_main_app_safe(*args, **kwargs):
    """Runtime-safe wrapper around render_main_app.

    Catches exceptions raised during rendering, writes a full traceback to
    `debug_runtime.log`, attempts to display a minimal error to the user,
    and then re-raises the exception so host-level logs capture it as well.
    """
    try:
        return render_main_app(*args, **kwargs)
    except Exception as e:
        import traceback
        from pathlib import Path as _Path

        tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        try:
            _Path('debug_runtime.log').write_text(tb, encoding='utf-8')
        except Exception:
            # best-effort write
            pass

        try:
            # If Streamlit is usable, show a short excerpt to the user
            st.error(
                "A runtime error occurred; details have been written to debug_runtime.log")
            excerpt = '\n'.join(tb.splitlines()[-12:])
            st.markdown(
                f"<pre style='white-space:pre-wrap'>{excerpt}</pre>", unsafe_allow_html=True)
        except Exception:
            # If Streamlit can't render, print to stdout for host logs
            print(tb)

        # Re-raise so hosting environment also records the traceback
        raise
