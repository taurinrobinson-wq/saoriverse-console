#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer setup] Starting setup script"

PYTHON=$(which python || true)
if [ -z "$PYTHON" ]; then
  echo "No python executable found in PATH. Exiting."
  exit 1
fi

echo "Using python: $PYTHON" 
echo "Upgrading pip and installing requirements..."
"$PYTHON" -m pip install --upgrade pip setuptools wheel || true

if [ -f "requirements.txt" ]; then
  "$PYTHON" -m pip install -r requirements.txt || true
else
  echo "requirements.txt not found; skipping pip install"
fi

echo "[devcontainer setup] Completed."
echo "If you want to start the Streamlit UI run:"
echo "  streamlit run src/streamlit_integration/chat_sandbox.py  --server.enableCORS false --server.enableXsrfProtection false"
exit 0
