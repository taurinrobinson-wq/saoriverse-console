#!/usr/bin/env python
"""Test the Streamlit app imports."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing imports...")

try:
    print("1. Testing emotional_os.deploy.modules.ui_refactored import...")
    from emotional_os.deploy.modules.ui_refactored import main
    print("   ✓ ui_refactored imports successfully")
except Exception as e:
    print(f"   ✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    print("2. Testing emotional_os.core.firstperson imports...")
    from emotional_os.core.firstperson import create_orchestrator, create_affect_parser
    print("   ✓ firstperson imports successfully")
except Exception as e:
    print(f"   ✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    print("3. Testing response_handler imports...")
    from emotional_os.deploy.modules.ui_components.response_handler import handle_response_pipeline
    print("   ✓ response_handler imports successfully")
except Exception as e:
    print(f"   ✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    print("4. Testing session_manager imports...")
    from emotional_os.deploy.modules.ui_components.session_manager import initialize_session_state
    print("   ✓ session_manager imports successfully")
except Exception as e:
    print(f"   ✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All imports successful!")
