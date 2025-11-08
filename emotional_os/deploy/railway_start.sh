#!/usr/bin/env bash
# Railway start script: enable serving the static chat HTML and start the FastAPI server

# Ensure PORT is set by Railway
PORT=${PORT:-8000}

# Enable serving static chat template from this container
export SERVE_STATIC_CHAT=1

# Optional: you can set other environment variables here or let Railway provide them via project settings
# e.g. export SUPABASE_URL=...

exec python -m uvicorn fastapi_app:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 30
