#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <input> <output_basename> [scale_height] [crf_mp4] [crf_webm]"
  echo "Example: $0 input.mp4 Tessa_Greeting_opt 720 23 32"
  exit 1
fi

IN="$1"
OUT_BASE="$2"
SCALE_H="${3:-720}"
CRF_MP4="${4:-23}"
CRF_WEBM="${5:-32}"

OUT_DIR=$(dirname "$IN")
MP4_OUT="$OUT_DIR/${OUT_BASE}.mp4"
WEBM_OUT="$OUT_DIR/${OUT_BASE}.webm"
META_OUT="$OUT_DIR/${OUT_BASE}.meta.json"

if [ ! -f "$IN" ]; then
  echo "Input file not found: $IN"
  exit 2
fi

echo "Optimizing $IN -> $MP4_OUT and $WEBM_OUT (scale height=${SCALE_H})"

# MP4 (H.264) optimized for web playback
ffmpeg -hide_banner -loglevel info -y -i "$IN" \
  -c:v libx264 -preset medium -crf "$CRF_MP4" -movflags +faststart -pix_fmt yuv420p \
  -vf "scale=-2:${SCALE_H}" -c:a aac -b:a 128k "$MP4_OUT"

# WebM (VP9) with constrained quality (b=0 + crf)
ffmpeg -hide_banner -loglevel info -y -i "$IN" \
  -c:v libvpx-vp9 -b:v 0 -crf "$CRF_WEBM" -vf "scale=-2:${SCALE_H}" -c:a libopus -b:a 96k "$WEBM_OUT"

# Sidecar metadata: instruct engine to play once (no loop)
cat > "$META_OUT" <<EOF
{
  "loop": false,
  "autoplay": true,
  "poster": null,
  "notes": "Optimized for in-game playback. Use mp4 primarily; webm provided as alternative."
}
EOF

echo "Wrote: $MP4_OUT"
echo "Wrote: $WEBM_OUT"
echo "Wrote: $META_OUT"
