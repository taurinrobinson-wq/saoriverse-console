#!/usr/bin/env bash
set -euo pipefail

# Upload a SoundFont (.sf2) to a GitHub Release and print its SHA256.
#
# Usage:
#   ./scripts/release_sf2.sh <tag> [path/to/FluidR3_GM.sf2]
#
# If `gh` is available it will be used. Otherwise the script falls back to
# the GitHub API and requires `GITHUB_TOKEN` to be set in the environment.

REPO_ARG="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$REPO_ARG" ]]; then
  echo "Could not determine origin remote; set GITHUB_REPO=owner/repo or run from a git repo." >&2
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <tag> [sf2-path]" >&2
  exit 1
fi

TAG=$1
SF2_PATH=${2:-Offshoots/ToneCore/sf2/FluidR3_GM.sf2}

if [[ ! -f "$SF2_PATH" ]]; then
  echo "SF2 file not found at $SF2_PATH" >&2
  exit 1
fi

echo "Computing SHA256 for $SF2_PATH..."
SHA256=$(sha256sum "$SF2_PATH" | awk '{print $1}')
echo "SHA256: $SHA256"

# Determine owner/repo
if [[ -n "${GITHUB_REPO:-}" ]]; then
  REPO=${GITHUB_REPO}
else
  # convert git URL to owner/repo
  if [[ "$REPO_ARG" =~ github.com[:/]+([^/]+)/([^.]+) ]]; then
    REPO="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
  else
    echo "Unable to parse origin URL ('$REPO_ARG'). Please set GITHUB_REPO=owner/repo." >&2
    exit 1
  fi
fi

echo "Repository: $REPO"

basename_sf2=$(basename "$SF2_PATH")

if command -v gh >/dev/null 2>&1; then
  echo "Using gh CLI to publish release/upload asset"
  if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    echo "Release $TAG exists — uploading asset (will overwrite if exists)"
    gh release upload "$TAG" "$SF2_PATH" --clobber --repo "$REPO"
  else
    echo "Creating release $TAG and attaching asset"
    gh release create "$TAG" "$SF2_PATH" --title "$TAG" --notes "SF2 release — SHA256: $SHA256" --repo "$REPO"
  fi
  echo "Done. Asset uploaded via gh. SHA256: $SHA256"
  exit 0
fi

# Fallback: use GitHub API
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "gh CLI not found and GITHUB_TOKEN is not set; cannot upload via API." >&2
  exit 1
fi

AUTH_HEADER="Authorization: token ${GITHUB_TOKEN}"
API_BASE="https://api.github.com/repos/$REPO"

echo "Using GitHub API to create/find release '$TAG'"
release_json=$(curl -s -H "$AUTH_HEADER" "$API_BASE/releases/tags/$TAG" || true)
upload_url=''
if echo "$release_json" | jq -e .id >/dev/null 2>&1; then
  upload_url=$(echo "$release_json" | jq -r .upload_url)
  echo "Found existing release: upload_url=$upload_url"
else
  echo "Release not found; creating new release $TAG"
  create_json=$(curl -s -X POST -H "$AUTH_HEADER" -d @- "$API_BASE/releases" <<JSON
{"tag_name":"$TAG","name":"$TAG","body":"SF2 release — SHA256: $SHA256","draft":false,"prerelease":false}
JSON
)
  upload_url=$(echo "$create_json" | jq -r .upload_url)
  if [[ "$upload_url" == "null" || -z "$upload_url" ]]; then
    echo "Failed to create release: $create_json" >&2
    exit 1
  fi
fi

# upload_url contains a template like: https://uploads.github.com/repos/:owner/:repo/releases/:id/assets{?name,label}
upload_url=${upload_url%%\{*}

echo "Uploading asset to $upload_url"
curl --fail -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/octet-stream" --data-binary @"$SF2_PATH" "$upload_url?name=$basename_sf2"

echo "Upload complete. SHA256: $SHA256"
