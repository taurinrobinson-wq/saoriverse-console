"""
FirstPerson - Personal AI Companion
Main Streamlit entry point

Requires Python 3.11 or 3.12 (not 3.13+)
"""

import sys
import os
from pathlib import Path

# Pre-startup: Ensure spaCy model is available (for Streamlit Cloud compatibility)
try:
    from streamlit import cache_resource
    # Import the pre-run hook to ensure spaCy model is downloaded before app loads
    sys.path.insert(0, str(Path(__file__).parent / ".streamlit"))
    from pre_run_hook import ensure_spacy_model
    ensure_spacy_model()
except Exception as e:
    print(f"⚠️ Pre-run hook warning: {e}")

# Verify Python version compatibility
if sys.version_info >= (3, 13):
    print(f"❌ ERROR: Python {sys.version_info.major}.{sys.version_info.minor} is not supported")
    print("Please use Python 3.11 or 3.12")
    print("")
    print("To fix:")
    print("  1. Deactivate current venv: deactivate")
    print("  2. Use workspace venv: source /workspaces/saoriverse-console/.venv/bin/activate")
    print("  3. Run: streamlit run app.py")
    sys.exit(1)

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
import time

# Add a marker file so health checks can detect startup
_STARTUP_MARKER = Path(__file__).parent / ".streamlit_starting"
if not _STARTUP_MARKER.exists():
    _STARTUP_MARKER.touch()

# Set page config first (MUST be before other streamlit calls)
try:
    logo_path = Path("static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
    page_icon = None
    if logo_path.exists():
        try:
            page_icon = logo_path.read_bytes()
        except Exception:
            page_icon = None
    
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon=page_icon if page_icon is not None else "🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

# Diagnostic: Show which Python executable is being used
import sys
with st.sidebar:
    python_exe = sys.executable
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Check if running Python 3.12
    if sys.version_info.major == 3 and sys.version_info.minor == 12:
        st.success(f"✓ Python {python_version}")
    else:
        st.warning(f"⚠️ Python {python_version}\n\nFor full functionality, use Python 3.12:\n\n```\npy -3.12 -m streamlit run app.py\n```")
    
    with st.expander("Diagnostic Info"):
        st.code(python_exe, language="text")

# Now import the UI system
try:
    from emotional_os.deploy.modules.ui_refactored import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    # Try alternative import path if the main one fails
    try:
        import sys
        from pathlib import Path
        # Add src to path if it's not already there
        src_path = str(Path(__file__).parent / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from emotional_os.deploy.modules.ui_refactored import main
        
        if __name__ == "__main__":
            main()
    except Exception as e2:
        st.error(f"Failed to load FirstPerson UI: {str(e2)}")
        import traceback
        st.error(traceback.format_exc())
        
except Exception as e:
    st.error(f"Failed to load FirstPerson UI: {str(e)}")
    import traceback
    st.error(traceback.format_exc())
