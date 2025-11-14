"""Pytest configuration for FirstPerson test suite."""
import sys
import os
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
