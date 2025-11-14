#!/usr/bin/env python3
"""Quick test for generate_conversation_title()"""
import sys
import os
import importlib

# Ensure repo root is on path so local package imports work when running script
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Import module after adjusting path
cm = importlib.import_module(
    'emotional_os.deploy.modules.conversation_manager')
generate_conversation_title = cm.generate_conversation_title


SAMPLES = [
    "My son Winston has been struggling a lot lately, and it's been weighing on me.",
    "I feel like I'm finally finding my rhythm again.",
    "Just wanted to say thanks for holding space.",
    "Short.",
    "",  # empty
    "Here's a very long first message that will exceed the maximum length and should be truncated by the title generator to ensure no more than the allowed 35 characters are used in the summary part of the title."
]


if __name__ == '__main__':
    for i, s in enumerate(SAMPLES, 1):
        title = generate_conversation_title(s)
        print(f"{i}. input={repr(s[:80])} -> title={title}")
    sys.exit(0)
