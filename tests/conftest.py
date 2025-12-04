"""Pytest configuration for FirstPerson test suite."""

import os
import sys

import pytest

# Add project root to path so tests can import modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def ensure_cwd_project_root():
    """Ensure each test runs with the project root as the current working directory.

    Some tests or helper scripts change the CWD; this autouse fixture resets it
    for isolation and prevents relative-path flakiness.
    """
    prev = os.getcwd()
    try:
        os.chdir(PROJECT_ROOT)
        yield
    finally:
        try:
            os.chdir(prev)
        except Exception:
            # best-effort restore; ignore failures to avoid masking test errors
            pass


@pytest.fixture
def sample_glyph():
    """Sample glyph for testing."""
    return {
        "glyph_name": "Euphoric Yearning",
        "gate": "Gate 5",
        "description": "Hopeful desire with presence"
    }


@pytest.fixture
def sample_signal():
    """Sample emotional signal for testing."""
    return {
        "voltage": 0.6,
        "tone": "Yearning",
        "attunement": 0.7,
        "certainty": 0.5,
        "valence": 0.3
    }


@pytest.fixture
def sample_user_input():
    """Sample user input for testing."""
    return "I've been feeling lost lately, like I'm not sure who I am anymore."


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary directory for test data."""
    return tmp_path / "test_data"
