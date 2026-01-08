Summary of automated/manual markdown fixes for `/docs/reference/TECHNICAL_ARCHITECTURE.md`:

- Heuristic pass: labeled unlabeled fenced code blocks as `text` (conservative) to resolve MD040 warnings.
- Confirmed MD040 occurrences are cleared for this file.

Remaining lint findings (post-edit):

- MD013 (line-length): several long lines remain and should be wrapped in a subsequent formatting pass.
- MD012/MD022/MD031/MD032: blank-line spacing around headings, lists, and fences needs cleanup.
- MD003/MD024: heading style variations and duplicate headings present; standardize later.

Recommendation:

- Defer formatting and line-wrapping to a dedicated sweep to preserve narrative tone.
- Proceed to the final triage file `docs/reference/ADAPTIVE_EXTRACTOR_QUICK_SUMMARY.md` next.

Actions taken:

- Committed `docs/reference/TECHNICAL_ARCHITECTURE.md` fence-language updates.
- Created this review note.
