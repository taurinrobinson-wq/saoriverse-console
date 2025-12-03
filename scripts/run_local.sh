#!/usr/bin/env bash
set -euo pipefail

# Helper to run the app locally using the repo's virtualenv and local data.
# Usage: ./run_local.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ -f .venv/bin/activate ]; then
  # Activate project virtualenv if present
  # shellcheck disable=SC1091
  . .venv/bin/activate
else
  echo "No .venv found. Create one with:" >&2
  echo "  python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

# If a local env file exists, export its variables
if [ -f .env.local ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source .env.local
  set +o allexport
fi

# Start the Streamlit app via the project's start script (honors PORT)
python start.py
