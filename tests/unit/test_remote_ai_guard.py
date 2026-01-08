import os

import pytest


def test_create_supabase_integrator_blocked(monkeypatch):
    """Creating a Supabase integrator with explicit config should raise when remote AI is disabled."""
    monkeypatch.setenv("PROCESSING_MODE", "local")
    # Ensure ALLOW_REMOTE_AI is not set
    monkeypatch.delenv("ALLOW_REMOTE_AI", raising=False)

    from emotional_os.supabase.supabase_integration import create_supabase_integrator

    with pytest.raises(RuntimeError):
        create_supabase_integrator({"function_url": "https://example.com", "anon_key": "abc"})


def test_create_supabase_integrator_allowed_with_opt_in(monkeypatch):
    """When ALLOW_REMOTE_AI=1, creation should not raise."""
    monkeypatch.setenv("PROCESSING_MODE", "local")
    monkeypatch.setenv("ALLOW_REMOTE_AI", "1")

    from emotional_os.supabase.supabase_integration import create_supabase_integrator

    # Should not raise
    create_supabase_integrator({"function_url": "https://example.com", "anon_key": "abc"})
