#!/usr/bin/env python3
"""Smoke test: call the app's response pipeline directly.

Runs two prompts and prints the cleaned response and timing. Uses
the same modules the Streamlit app calls so results mirror the UI.
"""
import time
import logging

# Ensure src is importable
import os, sys
ROOT = os.path.dirname(os.path.dirname(__file__))
# Add project root so `src` package can be imported as `src`
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

from emotional_os.deploy.modules.ui_components.session_manager import initialize_session_state
from emotional_os.deploy.modules.ui_components.response_handler import handle_response_pipeline

logging.basicConfig(level=logging.INFO)

def main():
    initialize_session_state()

    tests = [
        "What's up",
        "If you had a mood right now, what would it be?",
    ]

    for txt in tests:
        start = time.time()
        try:
            response, proc_time = handle_response_pipeline(txt, {})
        except Exception as e:
            response = f"[ERROR] {e}"
            proc_time = time.time() - start
        total = time.time() - start
        print("INPUT:", txt)
        print("RESPONSE:\n", response)
        print(f"Processed in {proc_time:.3f}s (total call {total:.3f}s)")
        print("-"*40)

if __name__ == '__main__':
    main()
