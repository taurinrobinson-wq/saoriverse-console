"""
Startup script that launches both Next.js and FastAPI, then stays alive.
This runs as PID 1 so the container stays running.
"""
import subprocess
import time
import sys
import signal
import os

def signal_handler(sig, frame):
    """Handle shutdown gracefully."""
    print("Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print("Starting Velinor services...")

# Start Next.js frontend in background
print("[*] Starting Next.js frontend on port 3000...")
next_process = subprocess.Popen(
    ["npm", "start"],
    cwd="/app/velinor-web",
    stdout=open("/tmp/frontend.log", "w"),
    stderr=subprocess.STDOUT
)

# Wait for Next.js to start
time.sleep(5)

# Start FastAPI backend in background
print("[*] Starting FastAPI backend on port 8000...")
api_process = subprocess.Popen(
    ["python3", "velinor_api.py"],
    cwd="/app",
    stdout=open("/tmp/api.log", "w"),
    stderr=subprocess.STDOUT,
    env={**os.environ, "PORT": "8000"}
)

# Wait for API to start
time.sleep(3)

# Start nginx as main process
print("[*] Starting nginx reverse proxy on port 8000...")
subprocess.run(
    ["nginx", "-g", "daemon off;"],
    check=False
)

# Keep the container alive
while True:
    time.sleep(1)
    if next_process.poll() is not None:
        print("Next.js process died!")
        break
    if api_process.poll() is not None:
        print("API process died!")
        break
