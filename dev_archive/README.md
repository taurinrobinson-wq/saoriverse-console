# dev_archive — Archived developer scripts

These files were moved from the repository root into `dev_archive/` as part
of a cleanup to keep the main tree focused on runtime code. History is
preserved (moves were performed with `git mv`).

Moved files

- `phase_1_generator.py`
- `phase_2_pruner.py`
- `phase_3_generator.py`
- `phase_4_id_deduplicator.py`
- `phase_4_ritual_tester.py`
- `generate_scenario_report.py`
- `glyph_effectiveness_validator.py`

Why these were archived

- These are one-off generation / maintenance / reporting scripts used for
  dataset creation, pruning, deduplication, QA, and reporting. They are not
  required for normal app runtime (Streamlit UI) and clutter the top-level
  repository tree.

How to restore a file

If you want to restore any file to its original location, use `git mv` to
move it back and commit. Example (from the repo root):

```bash
# move a single file back to the repo root
git mv dev_archive/phase_1_generator.py phase_1_generator.py
git commit -m "chore: restore phase_1_generator.py from dev_archive"
```

Or restore multiple files:

```bash
git mv dev_archive/* .
git commit -m "chore: restore archived dev scripts"
```

How to run these scripts

- These scripts are standalone Python scripts. They expect to be run from the
  repository root so relative paths resolve correctly. Example:

```bash
python3 dev_archive/phase_1_generator.py
```

- Some scripts modify or read the canonical glyph lexicon at:
  `emotional_os/glyphs/glyph_lexicon_rows.json`. Create a backup before
  running them.

Notes & safety

- Keep `dev_archive/` under version control (we used `git mv`) so history is
  preserved. If you later decide to delete these files permanently, prefer
  creating a separate archival branch and/or using Git LFS for large assets.
- If you need these scripts for repeated workflow (e.g., routine pruning or
  generation), consider moving them to `dev_tools/` and adding a short
  developer README describing usage and scheduling.

Generated on: 2025-11-18
