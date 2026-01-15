#!/usr/bin/env bash
# Example batch generator for Automatic1111 WebUI REST API
# Start the WebUI (Automatic1111) locally, then run this script from the repo root.
# Adjust `API` and parameters as needed.

API="http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR="output/generated"
mkdir -p "$OUTDIR"

# Define prompts (slug|prompt)
cat <<'PROMPTS' > /tmp/npc_prompts.txt
# slug|prompt
dakrin|semi-realistic painterly portrait, middle-aged woman, strong build, braided hair, ritual leathers, muted earth tones, iron armband, stoic expression, soft lighting, chest-up, subtle background, velinor aesthetic
elka|semi-realistic painterly portrait, contemplative woman, long loose hair, shrine robes pale blue and grey, subtle circuitry jewelry, serene expression, soft lighting, chest-up, gentle background, velinor aesthetic
helia|semi-realistic painterly portrait, warm grounded woman, mid-forties, loose tied hair, healer wraps green and brown, herbs and cords, gentle compassionate expression, soft lighting, chest-up, velinor aesthetic
kiv|semi-realistic painterly portrait, older wiry man, greying hair, clay-stained robes, pottery shard adornments, contemplative sorrowful expression, soft lighting, chest-up, velinor aesthetic
lark|semi-realistic painterly portrait, strong mason mid-thirties, stone-dust wraps, tool belt, earnest protective expression, soft lighting, chest-up, velinor aesthetic
seyla|semi-realistic painterly portrait, sharp-featured woman early forties, archivist robes ochre and red, lineage markers, focused weary expression, soft lighting, chest-up, velinor aesthetic
juria|semi-realistic painterly portrait, lean sailor late twenties, windswept hair with beads, layered blue fabrics, rope bracelets, bright mischievous expression, soft lighting, chest-up, velinor aesthetic
korinth|semi-realistic painterly portrait, sturdy sailor early thirties, tied-back hair, heavy green coat, cargo ledger, calm amused expression, soft lighting, chest-up, velinor aesthetic
PROMPTS

# Generation parameters
SAMPLER_NAME="Euler a"
STEPS=28
CFG_SCALE=8.5
WIDTH=1024
HEIGHT=1024

while IFS='|' read -r slug prompt; do
  for i in 1 2 3; do
    echo "Generating $slug v$i"
    filename="$OUTDIR/npc_${slug}_v${i}.png"
    payload=$(jq -n --arg p "$prompt" --argjson steps $STEPS --argjson cfg $CFG_SCALE --arg w $WIDTH --arg h $HEIGHT '{"prompt":$p, "steps":$steps, "cfg_scale":$cfg, "width":$w, "height":$h, "sampler_name": "'${SAMPLER_NAME}'"}')
    curl -s -X POST "$API" -H 'Content-Type: application/json' -d "$payload" | jq -r '.images[0]' | base64 --decode > "$filename"
  done
done < /tmp/npc_prompts.txt

echo "Batch generation complete. Outputs in $OUTDIR"
