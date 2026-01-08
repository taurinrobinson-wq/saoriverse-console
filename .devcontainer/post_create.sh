#!/usr/bin/env bash
set -euo pipefail

# Idempotent post-create script for devcontainer
# - ensures a project virtualenv at .venv
# - upgrades pip/setuptools/wheel and installs requirements.txt if present

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[post_create] Running post-create setup in $ROOT_DIR"

# Prefer python3 from PATH; fallback to system python
PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON" ]; then
  echo "[post_create] No python interpreter found in PATH. Please ensure Python is available." >&2
  exit 1
fi

VENV_DIR="$ROOT_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
  echo "[post_create] Virtualenv already exists at $VENV_DIR; using existing venv"
else
  echo "[post_create] Creating virtualenv at $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
fi

PIP="$VENV_DIR/bin/pip"
PY="$VENV_DIR/bin/python"

if [ ! -x "$PIP" ] || [ ! -x "$PY" ]; then
  echo "[post_create] venv missing pip/python executables; aborting" >&2
  exit 1
fi

echo "[post_create] Upgrading pip, setuptools, wheel"
"$PIP" install --upgrade pip setuptools wheel >/dev/null

REQ_FILE="$ROOT_DIR/requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "[post_create] Installing requirements from $REQ_FILE"
  # Use --upgrade to reconcile small changes; do not reinstall if already satisfied
  "$PIP" install --upgrade -r "$REQ_FILE"
else
  echo "[post_create] No requirements.txt found; skipping pip install"
fi

echo "[post_create] Done. To use the virtualenv in VS Code, set python.defaultInterpreterPath to $VENV_DIR/bin/python"

exit 0
