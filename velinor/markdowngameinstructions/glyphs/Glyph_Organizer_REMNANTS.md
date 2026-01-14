Glyph → REMNANTS mapping

- Purpose: provide a canonical JSON mapping where glyph acquisition or interaction applies small, bounded deltas to REMNANTS traits.
- Location: `velinor/data/glyph_remnants_map.json`

Notes on design:
- Deltas are small (±0.06 or less) to avoid breaking NPC trait caps.
- Each mapping includes `glyph_name`, `owner`, and `remnants_impact` (trait deltas).

Example entries (Saori glyphs):
- Glyph id 11 — Glyph of Infrasensory Oblivion: owner `Saori`, impacts `{memory: -0.06, empathy: +0.04, skepticism: +0.02}`
- Glyph id 74 — Glyph of Dormant Potential: owner `Saori`, impacts `{memory: +0.04, nuance: +0.03, trust: +0.02}`
- Glyph id 75 — Glyph of Mirrored Loss: owner `Saori`, impacts `{empathy: +0.05, need: +0.04, skepticism: +0.01}`

Integration guidance:
- Game code should load `velinor/data/glyph_remnants_map.json` and apply `remnants_impact` to the player or NPC profile during acquisition events.
- Respect caps on REMNANTS values (0.1 max delta per interaction recommended).
