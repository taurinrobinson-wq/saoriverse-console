#!/usr/bin/env bash
# Helper to push with a timeout and limited retries to avoid hangs.
# Usage: ./scripts/git-push-timeout.sh [timeout-seconds] [retries]

set -euo pipefail

TIMEOUT=${1:-120}
RETRIES=${2:-3}
BRANCH=${GIT_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}
REMOTE=${GIT_REMOTE:-origin}

echo "[git-push-timeout] pushing branch '$BRANCH' to remote '$REMOTE' with timeout=${TIMEOUT}s retries=${RETRIES}"

try=0
while [ $try -lt $RETRIES ]; do
  try=$((try + 1))
  echo "[git-push-timeout] attempt $try/$RETRIES..."
  # Show remote info first for diagnostics
  git remote -v || true
  git ls-remote "$REMOTE" HEAD || true

  # Use the POSIX timeout command if available; fall back to perl loop if not.
  if command -v timeout >/dev/null 2>&1; then
    if timeout "$TIMEOUT" git push "$REMOTE" "HEAD"; then
      echo "[git-push-timeout] push succeeded"
      exit 0
    else
      echo "[git-push-timeout] push attempt $try failed or timed out"
    fi
  else
    # fallback: run push in background and kill after timeout
    git push "$REMOTE" "HEAD" &
    pid=$!
    ( sleep "$TIMEOUT" && kill -9 "$pid" >/dev/null 2>&1 ) & watcher=$!
    wait "$pid" 2>/dev/null || true
    kill -9 "$watcher" >/dev/null 2>&1 || true
    # Check last push status in git
    if git rev-parse --verify --quiet origin/"$BRANCH" >/dev/null 2>&1; then
      echo "[git-push-timeout] push appears successful (origin/$BRANCH exists)"
      exit 0
    else
      echo "[git-push-timeout] push attempt $try failed or timed out (fallback)"
    fi
  fi

  # small backoff before retrying
  sleep 2
done

echo "[git-push-timeout] all $RETRIES attempts failed"
exit 2
