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
echo "  streamlit run main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py) --server.enableCORS false --server.enableXsrfProtection false"

### Jupyter Lab support: activate .venv (if present) and ensure jupyterlab is installed
if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
  echo "Activating .venv"
  # shellcheck disable=SC1091
  . .venv/bin/activate
  echo "Installing jupyterlab into .venv"
  python -m pip install --upgrade pip
  python -m pip install jupyterlab || true
else
  # If virtualenv not present, install into container python environment
  echo ".venv not found; installing jupyterlab into container python"
  "$PYTHON" -m pip install --upgrade pip
  "$PYTHON" -m pip install jupyterlab || true
fi

exit 0
