# Glyphs cleanup utility

This folder contains a small utility to parse a downloaded SQL export of the `glyphs` table,
normalize fields, deduplicate, and produce preview artifacts so you can review changes before
applying them to Supabase.

Files

- `cleanup_glyphs.py` — main script. Runs in dry-run by default and produces:
  - `dev_tools/cleaned_glyphs.json`
  - `dev_tools/cleaned_glyphs_upsert.csv`
  - `dev_tools/cleanup_report.md`

How to run (dry-run, safe)

```bash
python3 dev_tools/cleanup_glyphs.py --source glyphs_rows.sql --dry-run --sample 20
```

Options

- `--source`: path to SQL file containing the INSERT INTO ... VALUES (...) export. Defaults to `glyphs_rows.sql`.
- `--out-json` / `--out-csv` / `--report-md`: output paths.
- `--sample`: how many rows to include in the report sample.

Notes

- The script is conservative and is intended for local review. It does not write to Supabase.
- After you review the outputs I can add a safe upsert step that:

1) creates a backup export from Supabase 2) upserts cleaned rows in batches using the service-role
key 3) writes an upsert report

If you'd like me to proceed with a live dry-run against Supabase (backup + staged upsert without
commit), export `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` into this shell and tell me to run
the next step.
