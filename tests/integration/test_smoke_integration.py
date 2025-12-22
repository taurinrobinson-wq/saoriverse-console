import os
from pathlib import Path

import pytest

# Smoke test: import the parser and run a trivial parse using a simple greeting
try:
    from emotional_os.core.signal_parser import parse_input
except Exception:
    parse_input = None


def test_parse_input_smoke_creates_response(tmp_path):
    # Ensure fixture DB exists in expected location (create via script)
    # Find repository root robustly by walking parents until we find a known file
    p = Path(__file__).resolve()
    repo_root = p
    for _ in range(6):  # avoid infinite loops; repo won't be deeper than this
        if (repo_root / "velonix_lexicon.json").exists() or (repo_root / "scripts").exists():
            break
        repo_root = repo_root.parent
    fixture_script = repo_root / "scripts" / "create_sqlite_fixture.py"
    # Create fixture
    assert fixture_script.exists(), f"Fixture script missing: {fixture_script}"
    import sys
    import subprocess
    # Use the current Python executable so tests run on Windows and Unix
    subprocess.run([sys.executable, str(fixture_script)], check=True)
    fixture_db = repo_root / "emotional_os" / "glyphs" / "glyphs_integration_fixture.db"
    assert fixture_db.exists(), "Fixture DB was not created"

    assert parse_input is not None, "parse_input import failed"

    # Use a simple greeting which the parser handles without DB dependencies
    r = parse_input("hi", str(repo_root / "velonix_lexicon.json"), db_path=str(fixture_db))
    assert isinstance(r, dict)
    assert "voltage_response" in r
    assert r["voltage_response"] is not None
