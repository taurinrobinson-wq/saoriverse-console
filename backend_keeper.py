#!/usr/bin/env python
"""
Wrapper script to keep backend running and restart if it crashes.
"""
import subprocess
import time
import os
import sys

os.chdir(r'D:\saoriverse-console')
os.environ['PORT'] = '8001'

while True:
    print(f"[{time.strftime('%H:%M:%S')}] Starting backend...", flush=True)
    try:
        result = subprocess.run(
            ['py', '-3.12', 'firstperson_backend.py'],
            timeout=None
        )
        print(f"[{time.strftime('%H:%M:%S')}] Backend exited with code {result.returncode}", flush=True)
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Backend crashed: {e}", flush=True)
    
    print(f"[{time.strftime('%H:%M:%S')}] Restarting in 2 seconds...", flush=True)
    time.sleep(2)
