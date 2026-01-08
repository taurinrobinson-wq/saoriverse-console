Velinor data folder

Purpose
- Canonical schemas live in `schema.json` (JSON Schema) to standardize background, NPC, and glyph data.
- `first_glyph_sample.json` contains a minimal playable dataset for the first glyph (Nordia's ``Primal Oblivion``) used for prototyping and wiring.

How to use
1. Load `first_glyph_sample.json` into your scene manager during prototyping.
2. Use the `backgrounds` section to populate the three-layer visual system (background, midground, foreground) and overlays.
3. `npcs[].dialogueNodes` are simple nodes; each `choices` entry can contain `effects` which map to T, O, N, E stat adjustments.
4. `glyphs[].triggerType` defines a simple trigger; `presence_and_wait` is a default trigger that requires the player to stand with an NPC for a configured duration.

Notes
- Keep asset paths consistent and versioned, e.g. `amphitheater_base_v01.png`.
- Expand dialogue nodes to a full tree by adding `conditions` and `onEnterScript` keys.
- The sample contains minimal values; extend as needed for your scene wiring.

