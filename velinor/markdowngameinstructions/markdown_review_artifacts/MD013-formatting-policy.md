Title: MD013 / Line-wrapping and related formatting policy (draft)

Purpose

- Provide a conservative, reviewable policy for addressing MD013 (line-length) and related spacing/heading rules across narrative-heavy docs.

Goals

- Preserve semantic structure and readability of narrative content (poetry notes, diagrams, prose).
- Avoid breaking code blocks, tables, or inline examples.
- Make changes easily reviewable and reversible (small commits per file or logical section).

Policy (Draft)

1. Line-length target: Soft-wrap at 100 characters for narrative paragraphs; hard limit 120 chars
only when unavoidable.
   - Rationale: many narrative lines contain long titles/phrases; 100 chars balances readability and avoiding noisy diffs.
2. Do not wrap or reflow inside fenced code blocks, tables, YAML front matter, or ASCII art diagrams
— these are excluded from automated wrapping. 3. When wrapping narrative text, prefer sentence-aware
wrapping (wrap at sentence boundaries when possible) and retain paragraph indentation. 4. Headings:
normalize to ATX style (`## Heading`) with a single blank line above and below the heading. 5.
Remove duplicate top-level headings (consolidate content instead of duplicating identical H1/H2). 6.
Blank lines: ensure single blank line between block elements (no more than 1 consecutive blank
line).

Process

- Run a conservative auto-wrap tool on a small subset (5–10 representative files) using the above settings.
- Manual review for files with ASCII art, long lists, poems, or content that would degrade with wrapping.
- Commit changes in small batches with clear commit messages: `fix(md013): wrap <file> — 100ch soft-wrap`.

Exceptions

- Poetry, code, and intentional long lines (e.g., exhibition titles, long URLs) may be marked with `<!-- md013:ignore -->` before the paragraph to exclude from automated wrapping.

Next steps

- Confirm the soft-wrap width (I recommend 100 chars) and whether to allow `<!-- md013:ignore -->` markers.
- If approved, I'll run a small pilot on 5 files and produce diffs for review.
