import importlib


def test_import_ui_module():
    """Import-safety regression test: importing the UI module must not raise or
    execute Streamlit rendering at import time.
    """
    importlib.invalidate_caches()
    # Import the module; pytest will fail the test if this raises an exception.
    mod = importlib.import_module('emotional_os.deploy.modules.ui')
    # Basic sanity: module should have the loader function we refactored
    assert hasattr(mod, '_load_inline_svg')
