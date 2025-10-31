# Automated test to validate all major modules import without error
import pytest

def test_imports():
    try:
        import emotional_os.deploy.config
        import emotional_os.glyphs.signal_parser
        import emotional_os.glyphs.lexicon_learner
        import emotional_os.supabase.supabase_integration
        import emotional_os.auth.auth_emotional_os
        import emotional_os.ritual_ui.main
        import emotional_os.portal.admin_portal
        import emotional_os.parser.signal_parser
    except Exception as e:
        pytest.fail(f"Import failed: {e}")
