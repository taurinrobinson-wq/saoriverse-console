# Glyphs Migration Summary

This file summarizes the conservative cleanup, fragment detection, and CI fixes performed on the
`chore/cleanup-telemetry-fragments` branch. It is intended as a brief migration note for reviewers
and for future audits.

## What changed

- Added a conservative cleanup & enrichment pipeline (`dev_tools/cleanup_glyphs.py`) that runs in `--dry-run` mode by default.
- Implemented encoding fixes, name rehydration heuristics, slug normalization, trigger refinement, and inference for `glyph_type` and `emotional_tone`.
- Added fragment scoring to flag low-integrity rows (tagged `glyph_type: "fragment"` and `emotional_tone: "discard_candidate"`).
- Instrumented lightweight telemetry points in the runtime parser to make activation and selection events observable when enabled (toggleable via environment or UI).
- CI workflow `.github/workflows/self_diagnostic.yml` patched to safely push auto-fix commits back to the PR head branch (avoids detached-HEAD push failures).

## What was auto-fixed by CI

- The self-diagnostic job ran `tools/self_diagnostic.py --auto-fix` and applied a small set of conservative edits (formatting & small targeted fixes). The workflow now commits and pushes those edits back to the PR head branch when appropriate.

## Artifacts produced (dry-run)

- `dev_tools/cleaned_glyphs.json` — normalized preview of cleaned rows
- `dev_tools/cleaned_glyphs_upsert.csv` — CSV suitable for batched upsert (dry-run)
- `dev_tools/cleanup_report.md` — human-readable summary of actions performed by the cleanup script
- `dev_tools/lowest_integrity_sample.csv` — bottom 50 glyphs by integrity score (for manual review)
- `dev_tools/fragments_to_review.json` — flagged fragments for manual inspection (if run with `--fragments`)

## Safety and process notes

- No writes to Supabase were performed by default. The cleanup tool runs as a dry-run unless explicitly invoked with a non-dry flag and Supabase credentials.
- Before any upsert or destructive action we will (upon your instruction) take a full backup of the `glyphs` table and produce `dev_tools/glyphs_backup_<timestamp>.json`.
- Telemetry is opt-in. It can be enabled via environment variable `SAORI_ENABLE_TELEMETRY=1` or via the Streamlit UI checkbox added in the PR.

## How to review

1. Inspect `dev_tools/lowest_integrity_sample.csv` and `dev_tools/cleanup_report.md` for problematic
candidates. 2. Optionally run `python3 dev_tools/cleanup_glyphs.py --source glyphs_rows.sql
--dry-run --fragments` locally to regenerate `dev_tools/fragments_to_review.json` if you want a
different threshold or additional samples. 3. When satisfied, request an explicit upsert step (I
will create a backup and run batched upserts using `SUPABASE_SERVICE_ROLE_KEY`).

## Next steps (recommended)

- Your review of the bottom-50 sample and `fragments_to_review.json` (if you want it generated).
- Decide whether to adjust the fragment threshold or integrity rubric.
- If approved, instruct me to create a Supabase backup and proceed with a safe, batched upsert.

##

Commit: chore/cleanup-telemetry-fragments — adds migration summary for PR context.
