#!/usr/bin/env bash
set -euo pipefail

# Run edge function integration tests locally.
# Expects a .env file in the project root with keys:
# SUPABASE_AUTH_URL, SUPABASE_FUNCTION_URL, SUPABASE_URL, SUPABASE_ANON_KEY

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv-edge-tests"

echo "Using project root: $ROOT_DIR"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements-dev.txt"

export PYTHONPATH="$ROOT_DIR"

echo "Running pytest (supabase/tests)
"
pytest -q "$ROOT_DIR/supabase/tests" -q

deactivate

echo "Edge tests complete."
