def test_dance_mode_importable():
    # Ensure the demo module imports and exposes the dance_mode function
    import importlib

    mod = importlib.import_module("demos.streamlit_dance_mode")
    assert hasattr(mod, "dance_mode")
