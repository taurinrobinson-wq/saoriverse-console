NPC Placeholder Spec Sheet — Velinor

Purpose
- Consolidated spec sheet for batch generation of placeholder NPC portraits that match the existing Velinor painterly style.
- Includes: human-readable descriptions, batch‑friendly prompts, filename conventions, and generation notes for Automatic1111.

How to use
1. Pick a generation backend (Automatic1111 / Ollama / Stable Diffusion CLI).
2. Start the backend locally (e.g., Automatic1111 WebUI on `http://127.0.0.1:7860`).
3. Use `tools/batch_generate_automatic1111.sh` as an example to create images from the batch‑friendly prompts.
4. Postprocess outputs with `tools/asset_pipeline.py` to apply the painterly finish and thumbnails.

Naming convention
- Output images: `npc_<slug>_v1.png`, `npc_<slug>_v2.png`, `npc_<slug>_v3.png`
- Finalized assets (after `asset_pipeline`): `assets/npcs/<original-filename>` and thumbnails in `assets/npcs/thumbnails/`.

Batch settings recommendation (Automatic1111)
- Sampler: Euler a or DPM++ 2M Karras
- Sampling steps: 20–40
- CFG Scale: 7.0–9.0
- Size: 1024x1024 (generate square then crop/mask)
- Face restoration: off (painterly style needs original shading)
- Seed: random (or set for reproducible batches)

Included NPCs (from your specs)
- Dakrin — Trial Warden
  - batch prompt: `semi-realistic painterly portrait, middle-aged woman, strong build, braided hair, ritual leathers, muted earth tones, iron armband, stoic expression, soft lighting, chest-up, subtle background, velinor aesthetic`
  - suggested slug: `dakrin`

- Elka — Glyph Console Worshipper
  - batch prompt: `semi-realistic painterly portrait, contemplative woman, long loose hair, shrine robes pale blue and grey, subtle circuitry jewelry, serene expression, soft lighting, chest-up, gentle background, velinor aesthetic`
  - slug: `elka`

- Helia — Shrine Healer
  - batch prompt: `semi-realistic painterly portrait, warm grounded woman, mid-forties, loose tied hair, healer wraps green and brown, herbs and cords, gentle compassionate expression, soft lighting, chest-up, velinor aesthetic`
  - slug: `helia`

- Kiv — The Clay Hermit
  - batch prompt: `semi-realistic painterly portrait, older wiry man, greying hair, clay-stained robes, pottery shard adornments, contemplative sorrowful expression, soft lighting, chest-up, velinor aesthetic`
  - slug: `kiv`

- Lark — Shrine Mason
  - batch prompt: `semi-realistic painterly portrait, strong mason mid-thirties, stone-dust wraps, tool belt, earnest protective expression, soft lighting, chest-up, velinor aesthetic`
  - slug: `lark`

- Seyla — Archivist of Lineage
  - batch prompt: `semi-realistic painterly portrait, sharp-featured woman early forties, archivist robes ochre and red, lineage markers, focused weary expression, soft lighting, chest-up, velinor aesthetic`
  - slug: `seyla`

- Juria & Korinth — Sea Merchants (paired)
  - Juria batch prompt: `semi-realistic painterly portrait, lean sailor late twenties, windswept hair with beads, layered blue fabrics, rope bracelets, bright mischievous expression, soft lighting, chest-up, velinor aesthetic`
  - Korinth batch prompt: `semi-realistic painterly portrait, sturdy sailor early thirties, tied-back hair, heavy green coat, cargo ledger, calm amused expression, soft lighting, chest-up, velinor aesthetic`
  - slugs: `juria`, `korinth`

- Optional secondary NPCs: Desert Elder, Shrine Keeper, Harbor Dock Worker, Market Shrine Keeper (prompts available in the batch file)

Postprocess pipeline
1. Run generation to produce 1024x1024 PNGs in `output/generated/`.
2. Use `python tools/asset_pipeline.py --input-dir output/generated --out-dir assets/npcs --size 1024` to produce painterly, alpha-corrected final assets and thumbnails.

Notes on style matching
- The provided sample portraits emphasize subdued occlusion, painterly brush texture, muted warm palette, and directional studio-like lighting. The batch prompts above are tuned for that look; you can add a style token such as `velinor portrait rendering` or any custom model tag if you have a fine-tuned model.
- If you want exact matching, provide 3–5 anchor images (one of which you uploaded) and I can produce tuned prompts or an embedding for models that support image-conditioned generation.

Safety and IP
- These are placeholder NPC portraits. When using external models or services, ensure licenses permit derivative art and distribution for your project.

Files added
- `tools/batch_generate_automatic1111.sh` — example curl-based batch generator for Automatic1111 REST API.

If you want, I can also add:
- An `ollama` example script
- A small CLI tool that reads `Glyph_Organizer.json`, maps `npc.name` → `slug`, and writes a CSV of missing NPCs to use for batch generation.

