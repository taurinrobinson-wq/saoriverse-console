**Glyph Rules — Updates & Suggestions**

Location: `velinor/markdowngameinstructions/Glyph_Rules.json`

Summary
- An authoritative rulebook (`Glyph_Rules.json`) was added and used to refine enrichment heuristics for:
  - `tone_integration`
  - `remnants_integration`
  - `player_choices`
  - `narrative_triggers`

Files created/updated
- `velinor/markdowngameinstructions/Glyph_Rules.json` — authoritative NPC + domain rules
- `velinor/markdowngameinstructions/Glyph_Organizer.json` — converted + enriched dataset
- `scripts/convert_glyph_csv_to_json.py` — CSV → JSON converter
- `scripts/enrich_glyph_json.py` — tone/remnants enrichment (now uses rulebook)
- `scripts/enrich_choices_and_triggers.py` — choices/triggers enrichment (now uses rulebook)
- `velinor/markdowngameinstructions/Glyph_Organizer.schema.json` — JSON Schema
- `scripts/validate_glyph_json.py` — validator using `jsonschema`

High-level suggestions (actionable)

1. Expand authoritative rules
- Encode full NPC rules for: Kaelen (both personas), Sealina, Helia, Malrik, Drossel, Veynar, Elenya, Inodora, Nordia, Ravi, Nima.
- For each NPC include: `tone_integration`, `remnants_integration`, `player_choices`, `narrative_triggers`, and a `notes` field describing edge cases.

2. Stillness / Presence rules
- Define quantitative stillness thresholds for `Presence` arcs (e.g., `presence_time_seconds` defaults) and how they map to `player_choices` (`sit_or_leave`, `say_nothing`).
- Add an optional `presence_strength` score to glyph entries for runtime checks.

3. Kaelen / Trickster rules
- Explicitly model persona selection: `persona_flag` in UI state (backend) or `twine_tag` to mark trickster vs kaelen.
- Rules: if `alignment=align` → `narrative_triggers` include `give_true_route`; if `alignment=oppose` → `narrative_triggers` include `lead_to_maze` + `maze_end`.

4. Sealina / Legacy rules
- Mark `memory_fragments` references (e.g., `photo_mother.png`) in JSON.  
- `player_choices` should include `return_item` when items are found.

5. Collapse / Corruption rules
- Add `corruption_level` hint (low/med/high) to entries that use `broken_corelink` or `corrupted_data` so procedural text can escalate imagery.

6. Player choices & triggers — refinement
- Create canonical enumerations for `player_choices` and `narrative_triggers` (single source of truth) and reference them in the schema (future work).

7. Authoring workflow
- Provide a short `manage_glyphs.py` CLI to run convert → enrich → validate → (optionally) commit, and a `--dry-run` mode for checks.

8. Tests & validation
- Add unit tests that validate a sample of glyphs against the schema and the rulebook mappings.

Suggested next steps (priority)
1. You supply authoritative rule text for the remaining NPCs and Presence thresholds. I will encode it in `Glyph_Rules.json` and re-run enrichment.
2. Add `presence_time_seconds` and `presence_strength` fields to schema if you want numeric checks. I can update schema accordingly.
3. If you want the CLI wrapper next, I can add `scripts/manage_glyphs.py` that executes the pipeline and optionally commits. That can come after rule expansion.

Notes
- All changes are committed to `main`. Re-running the enrichment scripts is idempotent — re-run after rule edits to refresh JSON.
- The current heuristics are conservative; I recommend explicit rule additions for Kaelen (both personas), and Presence arcs (Helia / Ravi / Elka) as the next high-value items.

Owner / contact
- Created by automated assistant; please review and add your authoritative rules in `velinor/markdowngameinstructions/Glyph_Rules.json`.
