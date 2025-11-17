"""Main entry point for the Streamlit FirstPerson app.

High-level runtime flow:

- Startup: the app sets Streamlit `page_config`, injects UI theme/CSS, and
    loads optional helpers (preprocessor, limbic integration) using safe imports.
- Authentication: users sign in via `SaoynxAuthentication`; unauthenticated
    visitors see a demo-mode interface. The splash screen can be forced for QA.
- Preferences & Persistence: users opt into saving chats via Settings; per-
    session `learning_settings` (default: local-only) controls whether learning
    events are persisted locally (append-only JSONL) and whether remote AI is
    preferred. The UI enforces local-only processing by default.
- Message handling: when a user submits an emotionally charged message the
    text is parsed by `parse_input()` to extract signals, gates, glyphs and a
    voltage-style emotional summary. The `run_hybrid_pipeline()` coordinates
    local parsing and (optionally) remote AI enhancement while preserving
    local-first behavior and clear fallbacks.
- Response composition: replies are produced either by decoding an AI reply
    via `decode_ai_reply()` or by composing a local, multi-glyph response using
    `DynamicResponseComposer.compose_multi_glyph_response()` when AI is
    unavailable. The composer blends the top-N glyphs' tones, voltages and
    gate activations into a single, grounded reply.
- Learning & evolution: candidate signals/glyphs may be staged and persisted
    for later local evolution; deduplication and staging ensure near-duplicates
    are handled conservatively.

The goal: always return a grounded, private, and human-feeling response that
prefers local-only processing and preserves auditability of learning events.
"""

import streamlit as st
from pathlib import Path
import os
import base64
import json
import streamlit.components.v1 as components
from datetime import datetime

# Maintenance mode is controlled by the environment variable MAINTENANCE_MODE.
# To enable the friendly maintenance page without editing code, set
# MAINTENANCE_MODE=1 in your deployment environment. We avoid changing
# process environment variables in the repository by default.

# Important: don't import modules that use Streamlit until after
# we call st.set_page_config — Streamlit requires page_config to be the
# first Streamlit command in the main script. UI/auth modules import
# streamlit at top-level and can trigger Streamlit runtime behavior when
# imported.

# Must be first Streamlit command
# Prefer the project SVG as the page icon if available; fall back to emoji.
try:
    _logo_path = Path(
        "static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
    _page_icon = None
    if _logo_path.exists():
        try:
            # Read the SVG bytes and convert to a base64 data URI so
            # Streamlit consistently uses the provided image as the
            # page icon instead of falling back to the emoji.
            svg_bytes = _logo_path.read_bytes()
            try:
                _b64 = base64.b64encode(svg_bytes).decode('ascii')
                _page_icon = f"data:image/svg+xml;base64,{_b64}"
            except Exception:
                # If base64 encoding fails for any reason, fall back
                # to passing raw bytes (previous behavior).
                _page_icon = svg_bytes
        except Exception:
            _page_icon = None
    # Use bytes (image) if available, otherwise an emoji
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon=_page_icon if _page_icon is not None else "🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    # Ensure any failure here doesn't prevent the rest of the app from loading
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Development reload marker removed. Temporary DEV timestamp and stdout
# print were used during debugging and have been deleted.


# Startup safety check: if Supabase credentials are present but a global
# local-only guard is NOT set, warn loudly so deployments don't accidentally
# make remote/OpenAI calls. This shows an in-UI warning (when Streamlit is
# available) and logs a WARNING to stdout/logs. It's intentionally resilient
# so it won't break import-time behavior in tests or non-Streamlit environments.
def _startup_remote_ai_safety_check():
    try:
        import logging as _logging
        _logger = _logging.getLogger(__name__)
    except Exception:
        _logger = None

    try:
        force_local = str(os.getenv('FORCE_LOCAL_ONLY', '')
                          ).lower() in ('1', 'true', 'yes')
        has_supabase = bool(os.getenv('SUPABASE_FUNCTION_URL') or os.getenv('SUPABASE_URL') or os.getenv(
            'SUPABASE_ANON_KEY') or os.getenv('SUPABASE_USER_TOKEN') or os.getenv('SUPABASE_KEY'))
        if has_supabase and not force_local:
            msg = (
                "⚠️ Security warning: Supabase/remote AI credentials are present but "
                "FORCE_LOCAL_ONLY is not enabled. The application may make remote AI calls. "
                "To enforce local-only operation, set environment variable: FORCE_LOCAL_ONLY=1"
            )
            try:
                if _logger:
                    _logger.warning(msg)
            except Exception:
                pass
            try:
                # Prefer Streamlit UI warning when running in the app context
                import streamlit as _st
                _st.warning(msg)
            except Exception:
                # Fall back to printing so CI/deploy logs still capture it
                print(msg)
    except Exception:
        # Safety check should never raise
        try:
            print('Startup remote-AI safety check failed (non-fatal)')
        except Exception:
            pass


# Run safety check early during startup
_startup_remote_ai_safety_check()


def safe_embed_html(content: str, height: int | None = None, use_iframe: bool = True) -> None:
    """Embed HTML in a safer, isolated way when possible.

    - Prefers `components.html` (iframe) to avoid leaking styles into the
      parent Streamlit document. Falls back to `st.markdown(..., unsafe...)`
      when iframe embedding is not appropriate or fails.

    Parameters
    - content: HTML/CSS/JS string to embed
    - height: optional pixel height for the iframe. If None, a small
      default will be used.
    - use_iframe: when False, force fallback to `st.markdown`.
    """
    try:
        if use_iframe:
            # components.html isolates injected markup inside an iframe which
            # prevents global CSS from leaking into the host app. Use scrolling
            # so long style blocks won't be clipped.
            components.html(content, height=height or 160, scrolling=True)
            return
    except Exception:
        # If iframe embedding fails for any reason, fall back to markdown.
        pass

    # Fallback: inject as raw markdown (preserves previous behaviour)
    try:
        st.markdown(content, unsafe_allow_html=True)
    except Exception:
        # Last resort: print to STDOUT so diagnostics capture the output
        print("[safe_embed_html] failed to embed content")


# Quick maintenance mode: when MAINTENANCE_MODE=1 is set in the environment,
# render a simple friendly maintenance page and stop further app execution.
# This is a reversible, low-risk change so you can show users a working page
# while I continue diagnosing the root cause in the background.
try:
    if os.environ.get('MAINTENANCE_MODE') == '1':
        st.markdown(
            """
            <div style="display:flex;align-items:center;justify-content:center;height:70vh;">
              <div style="text-align:center;max-width:720px;padding:28px;border-radius:12px;border:1px solid #E8EDF3;background:linear-gradient(180deg,#FBFDFF,#FFFFFF)">
                <h2 style="margin:0 0 8px 0;color:#23262A;font-weight:400">FirstPerson — temporarily offline for maintenance</h2>
                <p style="color:#586069;margin:0 0 12px 0">We're applying a quick fix so the full app will be back shortly. Thank you for your patience.</p>
                <p style="color:#6B7178;margin:0;font-size:0.9rem">If you signed in and expect to see data, please try again in a few minutes.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Halt further Streamlit execution to keep the page simple and stable
        try:
            st.stop()
        except Exception:
            # If st.stop is not available for some reason, exit silently
            import sys as _sys
            _sys.exit(0)
except Exception:
    # Do not allow maintenance-mode logic to block normal startup on errors
    pass

# Replace default favicon with project logo (use embedded data URI so Streamlit
# will show the SVG as the browser favicon regardless of static file serving).
try:
    logo_path = Path(
        "static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
    if logo_path.exists():
        svg_bytes = logo_path.read_bytes()
        b64 = base64.b64encode(svg_bytes).decode("ascii")
        st.markdown(
            f"<link rel=\"icon\" href=\"data:image/svg+xml;base64,{b64}\" type=\"image/svg+xml\">", unsafe_allow_html=True)
except Exception:
    # Non-fatal: keep the emoji favicon if embedding fails
    pass

# Now import modules that rely on Streamlit being initialized (after page config).
# Wrap imports in a try/except that prints the full traceback so deployment logs
# will contain the original error (Streamlit's UI can redact exceptions).
# Optional env-gated import diagnostic: set RUN_IMPORT_DIAG=1 in the environment
# (Streamlit Cloud env vars or export on your host) to have the app print a
# full environment snapshot and attempt imports before normal startup. The
# output is written to debug_imports.log in the app directory and also printed
# to stdout so deployment logs capture it.
try:
    if os.environ.get('RUN_IMPORT_DIAG') == '1':
        import platform
        import importlib
        import traceback as _traceback
        from pathlib import Path as _Path

        _out = []

        def _w(s):
            print(s)
            _out.append(str(s))

        _w('=== RUN_IMPORT_DIAG ===')
        _w('Platform: ' + platform.platform())
        _w('Python: ' + sys.version.replace('\n', ' '))
        _w('Executable: ' + sys.executable)
        _w('CWD: ' + str(_Path.cwd()))
        _w('Sys.path:')
        for _p in sys.path:
            _w('  ' + _p)

        try:
            import importlib.metadata as _md

            def _pkg_ver(n):
                try:
                    return _md.version(n)
                except Exception:
                    return '<not-installed>'
        except Exception:
            def _pkg_ver(n):
                return '<no-metadata>'

        for _pkg in ('streamlit', 'requests'):
            _w(f"{_pkg} version: {_pkg_ver(_pkg)}")

        for _mod in ('main_v2', 'emotional_os.deploy.modules.ui'):
            _w(f"-- import {_mod}")
            try:
                importlib.import_module(_mod)
                _w(f"IMPORT_OK {_mod}")
            except Exception:
                _w(f"IMPORT_FAILED {_mod}")
                for L in _traceback.format_exc().splitlines():
                    _w('   ' + L)

        try:
            _logp = _Path('debug_imports.log')
            _logp.write_text('\n'.join(_out), encoding='utf-8')
            _w(f'Wrote {_logp}')
        except Exception as _e:
            _w('Failed to write debug_imports.log: ' + str(_e))
except Exception:
    # Diagnostic must never prevent normal startup
    pass
try:
    # Import both the primary renderer and the safe runtime wrapper (if present).
    # Use module imports + importlib.reload so Streamlit's re-run will pick up
    # edits to these modules without requiring a full process restart.
    import importlib
    import emotional_os.deploy.modules.ui as _ui_module
    import emotional_os.deploy.modules.auth as _auth_module

    try:
        importlib.reload(_ui_module)
    except Exception:
        # If reload fails, fall back to the already-imported module object.
        pass

    try:
        importlib.reload(_auth_module)
    except Exception:
        pass

    render_main_app = _ui_module.render_main_app
    render_main_app_safe = _ui_module.render_main_app_safe
    render_splash_interface = _ui_module.render_splash_interface
    delete_user_history_from_supabase = _ui_module.delete_user_history_from_supabase
    SaoynxAuthentication = _auth_module.SaoynxAuthentication
except Exception:
    import traceback
    import sys
    print("Traceback importing UI/auth modules:")
    traceback.print_exc()
    raise


# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['theme'] = 'Light'
    st.session_state['theme_loaded'] = False

    # Initialize learning persistence
    # Default to a local-only processing mode. The `scripts/local_integration`
    # module exposes `get_processing_mode()` which prefers an environment
    # override but otherwise returns 'local'. This disables hybrid/OpenAI
    # behavior by default.
    # Enforce local-only processing for the app frontend. Do not consult
    # alternate processing modes or remote-AI flags here: the UI and
    # engine are fixed to local behavior.
    default_mode = 'local'

    st.session_state['learning_settings'] = {
        'processing_mode': default_mode,
        'enable_learning': True,
        'persist_learning': True
    }

    # Create learning directories if they don't exist
    os.makedirs('learning/user_signals', exist_ok=True)
    os.makedirs('learning/user_overrides', exist_ok=True)
    os.makedirs('learning/conversation_glyphs', exist_ok=True)


# Customize navigation text
# [safe_embed_html patch] replaced inline block at original location (Customize navigation text)
safe_embed_html("""
    <style>
    div.st-emotion-cache-j7qwjs span.st-emotion-cache-6tkfeg {
        visibility: hidden;
        position: relative;
    }
    
    div.st-emotion-cache-j7qwjs span.st-emotion-cache-6tkfeg::before {
        visibility: visible;
        position: absolute;
        content: "FirstPerson - Emotional AI Companion";
        left: 0;
    }
    </style>
""", height=120)

# Remove stacked markdown blocks that only contain <style> tags (they create visible padding).
# This script hides any element-container whose markdown child contains only a <style> element.
# [safe_embed_html patch - global script] replaced inline script block; this script needs to run in the
# parent page (it manipulates the DOM outside any iframe), so we force the markdown fallback by
# setting `use_iframe=False` when calling `safe_embed_html` so the behaviour remains unchanged.
safe_embed_html("""
<script>
(function(){
    function removeStyleOnlyMarkdown(){
        try{
            const containers = document.querySelectorAll('div[data-testid="stMarkdownContainer"]');
            containers.forEach(c=>{
                // If the container has exactly one child and it's a STYLE tag, hide the nearest element-container
                if(c.children.length === 1 && c.children[0].tagName && c.children[0].tagName.toLowerCase() === 'style'){
                    // Walk up to find the element-container wrapper
                    let el = c;
                    while(el && !el.classList.contains('element-container')){
                        el = el.parentElement;
                    }
                    if(el){
                        el.style.display = 'none';
                        el.style.margin = '0';
                        el.style.padding = '0';
                    }
                }
            });
        }catch(e){console.warn('removeStyleOnlyMarkdown failed', e)}
    }

    window.addEventListener('load', function(){
        removeStyleOnlyMarkdown();
        // run again shortly after load for dynamic rendering
        setTimeout(removeStyleOnlyMarkdown, 150);
    });

    // Observe DOM changes to catch dynamically injected style blocks
    const observer = new MutationObserver(function(mutations){
        removeStyleOnlyMarkdown();
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", use_iframe=False, height=240)

# Hide the top brand row (emoji + H1) when the app is embedded in certain layouts.
# This prevents the duplicated header/title from rendering in pages where space is limited.
# Targets the header H1 id and the adjacent emoji block.
# [safe_embed_html patch] replaced header-hide CSS block
safe_embed_html("""
    <style>
    /* Hide specific header by id */
    /* Primary: hide the H1 Streamlit generates for the page header */
    h1#firstperson-personal-ai-companion { display: none !important; }

    /* Fallbacks: hide heading container that may be wrapped by Streamlit test ids */
    [data-testid="stHeadingWithActionElements"] { display: none !important; }
    [data-testid="stHeadingWithActionElements"] h1 { display: none !important; }

    /* Also hide any h1 whose id starts with the page slug (defensive) */
    h1[id^="firstperson"] { display: none !important; }

    /* Hide the small emoji/logo block rendered adjacent to the header */
    /* This targets the inner markdown container with the inline style font-size: 2.5rem */
    div[data-testid="stMarkdownContainer"] div[style*="font-size: 2.5rem"] { display: none !important; }

    /* Hide any horizontal block that contains the brand row to avoid layout shift */
    div[data-testid="stHorizontalBlock"] > div > div > div > div > div > div > div > h1 { display: none !important; }
    </style>
""", use_iframe=False, height=140)

# Target specific Streamlit-generated padding block class and reduce its top padding
# Target specific Streamlit-generated padding block and reduce its top padding
# [safe_embed_html patch] replaced padding CSS block
safe_embed_html("""
            <style>
            /* Reduce top padding on the large header container that pushes content down */
            .st-emotion-cache-7tauuy { padding: 0rem 1rem 1rem !important; }
            </style>
        """, use_iframe=False, height=80)

# Apply theme only if not already loaded for this session
if not st.session_state.get('theme_loaded'):
    if st.session_state.get('theme') == 'Dark':
        # [safe_embed_html patch] replaced dark-theme CSS block
        safe_embed_html("""
            <style>
            body, .stApp {background-color: #0E1117; color: #FAFAFA;}
            .stButton>button {
                background-color: #262730;
                color: #FAFAFA;
                border: 1px solid #555;
            }
            </style>
        """, use_iframe=False, height=140)
    else:
        # [safe_embed_html patch] replaced light-theme CSS block
        safe_embed_html("""
            <style>
            body, .stApp {background-color: #FFFFFF; color: #31333F;}
            .stButton>button {
                background-color: #F0F2F6;
                color: #31333F;
                border: 1px solid #E0E0E0;
            }
            </style>
        """, use_iframe=False, height=140)
    st.session_state['theme_loaded'] = True

# Basic theme compatibility
# Basic theme compatibility
# [safe_embed_html patch] replaced basic theme compatibility CSS
safe_embed_html("""
    <style>
    [data-testid="stSidebarNav"] {color: inherit;}
    .stMarkdown {color: inherit;}
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    </style>
""", use_iframe=False, height=100)

# Reduce font sizes in the sidebar for a denser layout
# Reduce font sizes in the sidebar for a denser layout
# [safe_embed_html patch] replaced sidebar font-size CSS block
safe_embed_html("""
    <style>
    /* Target the Streamlit sidebar container and reduce text sizes */
    [data-testid="stSidebar"] { font-size: 0.92rem !important; }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stWidgetLabel,
    [data-testid="stSidebar"] .stButton>button,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stMetric {
        font-size: 0.92rem !important;
        line-height: 1.15 !important;
    }

    /* Slightly larger for small titles if present */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] .stTitle {
        font-size: 1rem !important;
    }

    /* Ensure buttons and inputs remain usable */
    [data-testid="stSidebar"] .stButton>button {
        padding: 6px 10px !important;
    }
    </style>
""", use_iframe=False, height=220)

# NOTE: the per-session/export download control was intentionally moved into
# the Privacy & Consent panel (`render_consent_settings_panel`) to avoid
# showing duplicate download buttons in the sidebar. The fallback button
# that previously lived here has been removed to simplify the authenticated
# sidebar. If you need a global download shortcut again, reintroduce it
# behind a feature-flag.

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

    def render_error_ui(exc: Exception, tb: str | None = None) -> None:
        """Render a minimal, centered error page with a soft visual tone.

        Parameters
        - exc: the exception instance that occurred
        - tb: optional full traceback string (may be large). We display a short,
          sanitized excerpt and encourage checking server logs for the full trace.
        """
        try:
            # Soft visual tone and centered box
            st.markdown(
                """
                <style>
                .fp-error-wrap { display:flex; align-items:center; justify-content:center; height:70vh; }
                .fp-error-box {
                    background: linear-gradient(180deg, #FBFDFF, #FFFFFF);
                    border: 1px solid #E8EDF3;
                    box-shadow: 0 8px 24px rgba(18,24,31,0.06);
                    padding: 28px;
                    border-radius: 12px;
                    max-width: 720px;
                    text-align: center;
                }
                .fp-error-title { font-size: 1.5rem; margin-bottom: 8px; color: #23262A; }
                .fp-error-msg { color: #586069; margin-bottom: 12px; }
                .fp-trace { background:#F6F8FA; color:#1F2933; padding:12px; border-radius:8px; text-align:left; font-family: monospace; white-space: pre-wrap; overflow-x:auto; max-height:240px; }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="fp-error-wrap"><div class="fp-error-box">', unsafe_allow_html=True)
            st.markdown(
                '<div class="fp-error-title">Something went wrong</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="fp-error-msg">An unexpected error occurred while starting the app. The server logs contain the full traceback.</div>',
                unsafe_allow_html=True,
            )

            # Show the exception type and a short message (truncate long messages)
            short_msg = (str(exc) or type(exc).__name__)[:240]
            st.markdown(
                f"<div style='font-size:0.9rem;color:#6B7178;margin-bottom:12px;'>Error: {type(exc).__name__}: {short_msg}</div>", unsafe_allow_html=True)

            # If a traceback was provided, show a short excerpt inside a details block
            if tb:
                excerpt = '\n'.join(tb.splitlines()[-8:])
                st.markdown(
                    '<details><summary>Show more (sanitized traceback)</summary>', unsafe_allow_html=True)
                st.markdown(
                    f"<div class='fp-trace'>{excerpt}</div>", unsafe_allow_html=True)
                st.markdown('</details>', unsafe_allow_html=True)

            st.markdown('</div></div>', unsafe_allow_html=True)
        except Exception:
            # If rendering the nice UI fails, fall back to a minimal Streamlit error and print the traceback
            try:
                st.error(
                    "A critical error occurred during startup. Check the server logs for details.")
            except Exception:
                # If Streamlit is completely unusable, at least print to stdout
                print(
                    "A critical error occurred during startup. Check the server logs for details.")
            import traceback as _tb
            _tb.print_exc()


def main():
    """Main application entry point."""
    # Initialize authentication
    auth = SaoynxAuthentication()
    # Default to rendering the main app interface immediately. The UI now
    # supports a demo-first flow: when the user is not authenticated we show
    # the full interface in demo mode and expose Sign In / Register in the
    # sidebar. The legacy splash screen can still be shown by setting the
    # `force_splash` session_state key (useful for QA or debugging).
    if st.session_state.get('force_splash', False):
        render_splash_interface(auth)
        return

    # Prefer the safe renderer (captures runtime exceptions to debug_runtime.log)
    try:
        if 'render_main_app_safe' in globals() and callable(globals().get('render_main_app_safe')):
            globals().get('render_main_app_safe')()
        else:
            render_main_app()
    except Exception:
        # Let the outer __main__ exception handler render a friendly page
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        # Look up the renderer safely to avoid static analysis warnings about
        # potentially-unbound callables during import-time checks.
        _renderer = globals().get('render_error_ui')
        if callable(_renderer):
            try:
                _renderer(e, tb)
            except Exception:
                # If rendering the error UI fails, at least print the traceback
                print(tb)
        else:
            # No renderer available; print the traceback so logs contain details
            print(tb)
