import importlib


def test_import_ui_refactored_module():
    """Import-safety regression test: importing the UI refactored module must not raise or
    execute Streamlit rendering at import time.
    """
    importlib.invalidate_caches()
    # Import the module; pytest will fail the test if this raises an exception.
    mod = importlib.import_module("emotional_os.deploy.modules.ui_refactored")
    # Basic sanity: module should have the main entry functions we need
    assert hasattr(mod, "render_main_app")
    assert hasattr(mod, "render_main_app_safe")
