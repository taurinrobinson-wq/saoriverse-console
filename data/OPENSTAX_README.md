OpenStax Personality & Social extraction

What’s here

- Cleaned OpenStax pages saved under `data/openstax/` (one `_cleaned.txt` per URL).
- Candidate phrase CSV: `data/openstax_psych_phrases.csv`.
- Extraction helper: `tools/extract_openstax_psych_vocab.py` (re-run to refresh or change heuristics).

Quick resume (recommended)

1. Pull latest and switch to feature branch:

```bash
git pull origin main
```text
```



2. Install NLP deps (if needed):

```bash
python3 -m pip install requests beautifulsoup4 spacy
```text
```



3. Re-run extraction (if you want to refresh the outputs):

```bash
```text
```



4. Preview CSV results:

```bash
head -n 50 data/openstax_psych_phrases.csv
```



Notes

- The cleaned page files are safe to edit or further clean in `data/openstax/`.
- If you want to map phrases into the glyph lexicon, I can prepare an importer that converts CSV rows to the lexicon JSON schema.
- Branch: `feat/openstax-psych-extract` contains these outputs and is pushed to the remote.

If you want, I can also open a draft PR for review before you continue at home.
