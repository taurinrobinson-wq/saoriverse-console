#!/usr/bin/env bash
# Railway start script: enable serving the static chat HTML and start the FastAPI server

# Ensure PORT is set by Railway
PORT=${PORT:-8000}

# Enable serving static chat template from this container
export SERVE_STATIC_CHAT=1

echo "[railway_start] SERVE_STATIC_CHAT=${SERVE_STATIC_CHAT} PORT=${PORT}"
echo "[railway_start] Starting FastAPI (uvicorn) - serving static chat HTML from templates if enabled"

# Optional: you can set other environment variables here or let Railway provide them via project settings
# e.g. export SUPABASE_URL=...

# Ensure lexicon directory exists
LEX_DIR="data/lexicons"
mkdir -p "${LEX_DIR}"

# If an environment variable NRC_LEXICON_URL is provided, attempt to download the NRC lexicon
# into ${LEX_DIR}/nrc_emotion_lexicon.txt. This lets Railway fetch the lexicon at container
# startup without committing the (large) lexicon file into the repository.
if [ -n "${NRC_LEXICON_URL:-}" ]; then
	TARGET_FILE="${LEX_DIR}/nrc_emotion_lexicon.txt"
	if [ -f "${TARGET_FILE}" ]; then
		echo "[railway_start] NRC lexicon already exists at ${TARGET_FILE}; skipping download"
	else
		echo "[railway_start] NRC_LEXICON_URL set; downloading NRC lexicon from ${NRC_LEXICON_URL} => ${TARGET_FILE}"
		if command -v curl >/dev/null 2>&1; then
			curl -fsSL "${NRC_LEXICON_URL}" -o "${TARGET_FILE}" || echo "[railway_start] ERROR: curl failed to download NRC lexicon"
		elif command -v wget >/dev/null 2>&1; then
			wget -qO "${TARGET_FILE}" "${NRC_LEXICON_URL}" || echo "[railway_start] ERROR: wget failed to download NRC lexicon"
		else
			echo "[railway_start] WARNING: neither curl nor wget available; cannot download NRC lexicon"
		fi
		if [ -f "${TARGET_FILE}" ]; then
			echo "[railway_start] NRC lexicon downloaded successfully"
		else
			echo "[railway_start] NRC lexicon not present after attempted download"
		fi
	fi
else
	echo "[railway_start] NRC_LEXICON_URL not set; skipping lexicon download. To enable full emotion lookup, set NRC_LEXICON_URL to a raw file URL or commit the file to ${LEX_DIR}/nrc_emotion_lexicon.txt"
fi

exec python -m uvicorn fastapi_app:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 30
