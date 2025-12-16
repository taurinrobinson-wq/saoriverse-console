MD013 pilot: 5-file run

Parameters:

- Soft-wrap target: 100 characters
- `<!-- md013:ignore -->` allowed for exceptions

Files processed:

- `docs/reference/ADAPTIVE_EXTRACTOR_QUICK_SUMMARY.md`
- `velinor/markdowngameinstructions/05_npc_reaction_library.md`
- `velinor/story_map_velinor.md`
- `docs/reference/ADAPTIVE_DIMENSIONS_AND_GLYPHS.md`
- `docs/reference/TECHNICAL_ARCHITECTURE.md`

Summary:

- Pre-run linter output: `md013_pilot_before_lint.txt`
- Wrapper output: `md013_pilot_wrap_output.txt`
- Post-run linter output: `md013_pilot_after_lint.txt`

Observations:

- The wrapper successfully soft-wrapped paragraphs in all 5 files.
- Large narrative files (notably `story_map_velinor.md`) still contain many structural/lint issues beyond simple wrapping (heading styles, lists, and intentional long lines in tables/diagrams). These require manual review or targeted rules.

Next steps:

1. Review the `md013_pilot_after_lint.txt` diffs and identify a small set of manual exceptions (poems, ASCII art, long titles) to mark with `<!-- md013:ignore -->`.
2. If the 100-char target looks good, run the same wrapper across the remaining high-priority docs in a controlled batch (10–20 files), with review notes per batch.
