#!/usr/bin/env bash
# Simple ffmpeg grading helper for Velinor aesthetic adjustments.
# Desaturates, slightly darkens, adds a vignette and film grain.

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <input> <output> [saturation] [brightness] [contrast] [grain]"
  echo "Example: $0 sealina_final.mp4 sealina_final_grade.mp4 0.6 -0.03 1.02 12"
  exit 1
fi

IN="$1"
OUT="$2"
SATURATION="${3:-0.6}"
BRIGHTNESS="${4:--0.03}"
CONTRAST="${5:-1.02}"
GRAIN="${6:-12}"
LUT_PATH="${7:-}"

# Notes:
# - eq: basic exposure/contrast/saturation adjustments
# - vignette: darken edges to focus center (radius tuned for cinematic feel)
# - noise: adds film-like grain
# - format=yuv420p for compatibility

VF_FILTERS="format=yuv420p"

# apply optional lut3d first (if provided)
if [ -n "$LUT_PATH" ]; then
  if [ ! -f "$LUT_PATH" ]; then
    echo "LUT file not found: $LUT_PATH"
    exit 2
  fi
  VF_FILTERS+=",lut3d='$LUT_PATH'"
fi

VF_FILTERS+=",eq=brightness=${BRIGHTNESS}:contrast=${CONTRAST}:saturation=${SATURATION},vignette=PI/3,noise=alls=${GRAIN}:allf=t"

ffmpeg -hide_banner -loglevel info -y -i "$IN" \
  -vf "$VF_FILTERS" \
  -c:v libx264 -preset slow -crf 20 -c:a copy "$OUT"

echo "Wrote: $OUT"
