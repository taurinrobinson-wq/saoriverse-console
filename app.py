"""
FirstPerson - Personal AI Companion
Main Streamlit entry point for post-reorganization deployment
"""

import streamlit as st

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
            _page_icon = _logo_path.read_bytes()
        except Exception:
            _page_icon = None
    # Use bytes (image) if available, otherwise an emoji
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon=_page_icon if _page_icon is not None else "🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    # Ensure any failure here doesn't prevent the rest of the app from loading
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

# Add workspace root to Python path to enable imports from emotional_os and other modules
# This is necessary when running from core/ directory
_workspace_root = str(Path(__file__).parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Initialize persisted reward model for feedback-driven adaptation.
# This keeps learned weights on disk so Streamlit UI and the FastAPI feedback
# endpoint converge on the same persisted state (weights file path).
try:
    from emotional_os.feedback.reward_model import RewardModel

    # repo-local persisted weights file; RewardModel will load if present
    reward_model = RewardModel(
        dim=128, path="emotional_os/feedback/weights.json", auto_load=True)
except Exception:
    reward_model = None

# Optional local composer wired to the persisted reward model so the UI
# can demonstrate re-ranking of candidate responses when feedback updates
try:
    from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer

    composer = DynamicResponseComposer(reward_model)
except Exception:
    composer = None

# Development reload marker removed. Temporary DEV timestamp and stdout
# print were used during debugging and have been deleted.


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
    if os.environ.get("MAINTENANCE_MODE") == "1":
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
            f'<link rel="icon" href="data:image/svg+xml;base64,{b64}" type="image/svg+xml">', unsafe_allow_html=True
        )
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
    if os.environ.get("RUN_IMPORT_DIAG") == "1":
        import importlib
        import platform
        import traceback as _traceback
        from pathlib import Path as _Path

        _out = []

        def _w(s):
            print(s)
            _out.append(str(s))

        _w("=== RUN_IMPORT_DIAG ===")
        _w("Platform: " + platform.platform())
        _w("Python: " + sys.version.replace("\n", " "))
        _w("Executable: " + sys.executable)
        _w("CWD: " + str(_Path.cwd()))
        _w("Sys.path:")
        for _p in sys.path:
            _w("  " + _p)

        try:
            import importlib.metadata as _md

            def _pkg_ver(n):
                try:
                    return _md.version(n)
                except Exception:
                    return "<not-installed>"

        except Exception:

            def _pkg_ver(n):
                return "<no-metadata>"

        for _pkg in ("streamlit", "requests"):
            _w(f"{_pkg} version: {_pkg_ver(_pkg)}")

        for _mod in ("main_v2", "emotional_os.deploy.modules.ui"):
            _w(f"-- import {_mod}")
            try:
                importlib.import_module(_mod)
                _w(f"IMPORT_OK {_mod}")
            except Exception:
                _w(f"IMPORT_FAILED {_mod}")
                for L in _traceback.format_exc().splitlines():
                    _w("   " + L)

        try:
            _logp = _Path("debug_imports.log")
            _logp.write_text("\n".join(_out), encoding="utf-8")
            _w(f"Wrote {_logp}")
        except Exception as _e:
            _w("Failed to write debug_imports.log: " + str(_e))
except Exception:
    # Diagnostic must never prevent normal startup
    pass
try:
    # Import both the primary renderer and the safe runtime wrapper (if present).
    # Use module imports + importlib.reload so Streamlit's re-run will pick up
    # edits to these modules without requiring a full process restart.
    import importlib

    import emotional_os.deploy.modules.auth as _auth_module
    import emotional_os.deploy.modules.ui_refactored as _ui_module

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

    # Optional feedback widget (visible via sidebar toggle)
    try:
        import numpy as _np

        from emotional_os.feedback.feedback_store import FeedbackStore as _FeedbackStore
        from emotional_os.feedback.reward_model import RewardModel as _RewardModel

        _store = _FeedbackStore("emotional_os/feedback/feedback.jsonl")
        # reuse reward_model if present, otherwise load a local instance
        try:
            _rm = reward_model
            if _rm is None:
                raise NameError
        except Exception:
            _rm = _RewardModel(
                dim=128, path="emotional_os/feedback/weights.json")

        if st.sidebar.checkbox("Show Feedback Widget", value=False):
            st.sidebar.markdown("---")
            st.header("Feedback Loop Demo")
            candidate_text = st.text_area(
                "Candidate Response:", value="This is a sample response.")
            rating = st.radio(
                "Rate this response:",
                options=[+1, -1],
                format_func=lambda x: "👍 Positive" if x == 1 else "👎 Negative",
            )
            corrected_text = st.text_input(
                "Suggest a corrected response (optional):")
            features_text = st.text_input(
                "Features (comma-separated, optional):", value="0.5,0.2,-0.1")
            try:
                feats = _np.array(
                    [float(x.strip()) for x in features_text.split(",") if x.strip() != ""])
            except Exception:
                feats = _np.array([0.5, 0.2, -0.1])

            if st.button("Submit Feedback"):
                entry = {"rating": int(
                    rating), "text": corrected_text, "features": feats.tolist()}
                _store.append(entry)
                try:
                    if feats.size:
                        _rm.update(feats, int(rating))
                except Exception as e:
                    st.error(f"Failed to update reward model: {e}")
                st.success("Feedback submitted and reward model updated!")
                st.json(entry)
                # Demonstration: build a tiny candidate set and ask the composer
                try:
                    # ensure we have a usable reward model instance
                    if _rm is not None:
                        from emotional_os.glyphs.dynamic_response_composer import (
                            DynamicResponseComposer as _DRC,
                        )

                        _composer = _DRC(_rm)
                        # Build three simple candidate feature vectors derived from the provided features
                        base = _np.zeros(_rm.dim)
                        if feats.size:
                            base[: min(feats.size, _rm.dim)] = feats[: _rm.dim]

                        candidates = [
                            {"text": "Option A", "features": base.tolist()},
                            {"text": "Option B", "features": (
                                base * 0.5).tolist()},
                            {"text": "Option C", "features": (
                                base * -1.0).tolist()},
                        ]
                        try:
                            sel = _composer.compose(candidates)
                            st.info(f"Composer selected: {sel}")
                        except Exception:
                            # non-fatal: composer demo is optional
                            pass
                except Exception:
                    pass
    except Exception:
        # If feedback modules are not available, silently ignore widget creation
        pass

except ImportError as _import_err:
    import traceback
    
    # Print error for debugging
    print(f"Import error: {_import_err}")
    traceback.print_exc()
    
    # Provide a minimal fallback UI
    st.error("⚠️ Authentication subsystem unavailable — try demo mode below")
    
    if st.button("📋 Demo Mode"):
        import uuid
        user_id = str(uuid.uuid4())
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.username = "demo_user"
        st.session_state["show_login"] = False
        st.session_state["show_register"] = False
        st.rerun()
    
    # Provide dummy functions so the rest of the code doesn't break
    def render_main_app():
        st.markdown("## Demo Mode Active")
        st.write("Core modules are loading... please refresh the page.")
        
    def render_main_app_safe(*args, **kwargs):
        render_main_app()
        
    def render_splash_interface():
        st.markdown("## Demo Mode")
        if st.button("Enter"):
            st.session_state.authenticated = True
            st.rerun()
            
    def delete_user_history_from_supabase(user_id):
        return True, "Demo mode"
        
    class SaoynxAuthentication:
        def __init__(self):
            pass
            
except Exception as _err:
    import traceback
    print("Unexpected error importing UI/auth modules:")
    traceback.print_exc()
    st.error(f"Unexpected error: {_err}")
    st.stop()


# Initialize session state
if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    st.session_state["theme"] = "Light"
    st.session_state["theme_loaded"] = False

    # Initialize learning persistence
    # Default to a local-only processing mode. The `scripts/local_integration`
    # module exposes `get_processing_mode()` which prefers an environment
    # override but otherwise returns 'local'. This disables hybrid/OpenAI
    # behavior by default.
    # Enforce local-only processing for the app frontend. Do not consult
    # alternate processing modes or remote-AI flags here: the UI and
    # engine are fixed to local behavior.
    default_mode = "local"

    st.session_state["learning_settings"] = {
        "processing_mode": default_mode,
        "enable_learning": True,
        "persist_learning": True,
    }

    # Create learning directories if they don't exist
    os.makedirs("learning/user_signals", exist_ok=True)
    os.makedirs("learning/user_overrides", exist_ok=True)
    os.makedirs("learning/conversation_glyphs", exist_ok=True)


# Customize navigation text
# [safe_embed_html patch] replaced inline block at original location (Customize navigation text)
safe_embed_html(
    """
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
""",
    height=120,
)

# Remove stacked markdown blocks that only contain <style> tags (they create visible padding).
# This script hides any element-container whose markdown child contains only a <style> element.
# [safe_embed_html patch - global script] replaced inline script block; this script needs to run in the
# parent page (it manipulates the DOM outside any iframe), so we force the markdown fallback by
# setting `use_iframe=False` when calling `safe_embed_html` so the behaviour remains unchanged.
safe_embed_html(
    """
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
""",
    use_iframe=False,
    height=240,
)

# Hide the top brand row (emoji + H1) when the app is embedded in certain layouts.
# This prevents the duplicated header/title from rendering in pages where space is limited.
# Targets the header H1 id and the adjacent emoji block.
# [safe_embed_html patch] replaced header-hide CSS block
safe_embed_html(
    """
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
""",
    use_iframe=False,
    height=140,
)

# Target specific Streamlit-generated padding block class and reduce its top padding
# Target specific Streamlit-generated padding block and reduce its top padding
# [safe_embed_html patch] replaced padding CSS block
safe_embed_html(
    """
            <style>
            /* Reduce top padding on the large header container that pushes content down */
            .st-emotion-cache-7tauuy { padding: 0rem 1rem 1rem !important; }
            </style>
        """,
    use_iframe=False,
    height=80,
)

# Apply theme only if not already loaded for this session
if not st.session_state.get("theme_loaded"):
    if st.session_state.get("theme") == "Dark":
        # [safe_embed_html patch] replaced dark-theme CSS block
        safe_embed_html(
            """
            <style>
            body, .stApp {background-color: #0E1117; color: #FAFAFA;}
            .stButton>button {
                background-color: #262730;
                color: #FAFAFA;
                border: 1px solid #555;
            }
            </style>
        """,
            use_iframe=False,
            height=140,
        )
    else:
        # [safe_embed_html patch] replaced light-theme CSS block
        safe_embed_html(
            """
            <style>
            body, .stApp {background-color: #FFFFFF; color: #31333F;}
            .stButton>button {
                background-color: #F0F2F6;
                color: #31333F;
                border: 1px solid #E0E0E0;
            }
            </style>
        """,
            use_iframe=False,
            height=140,
        )
    st.session_state["theme_loaded"] = True

# Basic theme compatibility
# Basic theme compatibility
# [safe_embed_html patch] replaced basic theme compatibility CSS
safe_embed_html(
    """
    <style>
    [data-testid="stSidebarNav"] {color: inherit;}
    .stMarkdown {color: inherit;}
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    </style>
""",
    use_iframe=False,
    height=100,
)

# Reduce font sizes in the sidebar for a denser layout
# Reduce font sizes in the sidebar for a denser layout
# [safe_embed_html patch] replaced sidebar font-size CSS block
safe_embed_html(
    """
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
""",
    use_iframe=False,
    height=220,
)

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
                f"<div style='font-size:0.9rem;color:#6B7178;margin-bottom:12px;'>Error: {type(exc).__name__}: {short_msg}</div>",
                unsafe_allow_html=True,
            )

            # If a traceback was provided, show a short excerpt inside a details block
            if tb:
                excerpt = "\n".join(tb.splitlines()[-8:])
                st.markdown(
                    "<details><summary>Show more (sanitized traceback)</summary>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='fp-trace'>{excerpt}</div>", unsafe_allow_html=True)
                st.markdown("</details>", unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)
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
    if st.session_state.get("force_splash", False):
        render_splash_interface(auth)
        return

    # Prefer the safe renderer (captures runtime exceptions to debug_runtime.log)
    try:
        if "render_main_app_safe" in globals() and callable(globals().get("render_main_app_safe")):
            globals().get("render_main_app_safe")()
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

        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        # Look up the renderer safely to avoid static analysis warnings about
        # potentially-unbound callables during import-time checks.
        _renderer = globals().get("render_error_ui")
        if callable(_renderer):
            try:
                _renderer(e, tb)
            except Exception:
                # If rendering the error UI fails, at least print the traceback
                print(tb)
        else:
            # No renderer available; print the traceback so logs contain details
            print(tb)
