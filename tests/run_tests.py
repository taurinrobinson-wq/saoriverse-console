#!/usr/bin/env python
"""
Test runner for FirstPerson / Emotional OS test suite.
Provides unified interface to run tests from various categories.

Usage:
    python tests/run_tests.py                 # Run all tests
    python tests/run_tests.py unit             # Run only unit tests
    python tests/run_tests.py integration      # Run only integration tests
    python tests/run_tests.py performance      # Run only performance tests
    python tests/run_tests.py --verbose        # Run with verbose output
"""

import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
repo_root = Path(__file__).resolve().parent
os.chdir(str(repo_root))


def run_pytest(category=None, verbose=False):
    """Run pytest with appropriate configuration."""
    # Use the venv python if available
    import subprocess
    import sys

    # Try to detect venv Python interpreter
    python_exe = sys.executable
    if ".venv" not in python_exe and ".venv" in sys.prefix:
        # We're in venv, find the proper interpreter
        import os

        venv_bin = os.path.join(sys.prefix, "bin", "python")
        if os.path.exists(venv_bin):
            python_exe = venv_bin

    cmd = [python_exe, "-m", "pytest"]

    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")  # Always show test names

    # Add output formatting
    cmd.extend(["--tb=short", "--color=yes"])

    # Specify test path
    if category:
        category_map = {
            "unit": "tests/unit",
            "integration": "tests/integration",
            "performance": "tests/performance",
        }
        if category not in category_map:
            print(f"❌ Unknown category: {category}")
            print(f"   Valid options: {', '.join(category_map.keys())}")
            return 1
        cmd.append(category_map[category])
    else:
        cmd.append("tests")

    print(f"\n{'='*70}")
    print(f"Running tests: {' '.join(cmd[4:])}")
    print(f"{'='*70}\n")

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point."""
    category = None
    verbose = False

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg in ["unit", "integration", "performance"]:
            category = arg
        elif arg in ["-v", "--verbose"]:
            verbose = True
        elif arg in ["-h", "--help"]:
            print(__doc__)
            return 0

    # Run tests
    exit_code = run_pytest(category, verbose)

    if exit_code == 0:
        print(f"\n{'='*70}")
        print("✅ All tests passed!")
        print(f"{'='*70}\n")
    else:
        print(f"\n{'='*70}")
        print(f"❌ Tests failed with exit code {exit_code}")
        print(f"{'='*70}\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
