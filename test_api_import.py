#!/usr/bin/env python
"""Test if velinor_api imports."""
import sys
print("Test starting...", flush=True)
sys.path.insert(0, 'D:/saoriverse-console')

try:
    print("[1/2] Importing velinor_api...", flush=True)
    import velinor_api
    print("[2/2] Import successful!", flush=True)
except Exception as e:
    print(f"ERROR during import: {e}", flush=True)
    import traceback
    traceback.print_exc()
