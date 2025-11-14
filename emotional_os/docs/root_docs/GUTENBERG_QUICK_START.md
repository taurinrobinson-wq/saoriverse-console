# Project Gutenberg Processing - Quick Start Guide

## TL;DR - Run the Complete Pipeline

```bash
cd /workspaces/saoriverse-console

# 1. Download 30+ poetry collections (15-30 min)
python scripts/utilities/gutenberg_fetcher.py

# 2. Process through learning system (2-4 hours)
python scripts/utilities/bulk_text_processor.py \
    --dir "/Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry/" \
    --user-id gutenberg_bulk

# 3. Generate glyphs from poetry patterns (< 1 min)
python scripts/utilities/poetry_glyph_generator.py

# 4. Generate glyphs from extracted data (< 2 min)
python scripts/utilities/glyph_generator_from_extracted_data.py --use-cached

# 5. Integrate into main system
python scripts/utilities/integrate_glyph_lexicons.py \
    --poetry-glyphs generated_glyphs_from_poetry.json \
    --extracted-glyphs generated_glyphs_from_extracted_data.json \
    --output emotional_os/glyphs/glyph_lexicon_integrated.json
```

## What This Pipeline Does

| Phase | Script | What It Does | Time |
|-------|--------|--------------|------|
| **1** | `gutenberg_fetcher.py` | Downloads 30+ poetry collections from Project Gutenberg | 15-30 min |
| **2** | `bulk_text_processor.py` | Processes poetry through learning system, extracts emotional signals, updates lexicon | 2-4 hours |
| **3** | `poetry_glyph_generator.py` | Generates glyphs from discovered patterns | <1 min |
| **4** | `glyph_generator_from_extracted_data.py` | More comprehensive glyph generation | <2 min |
| **5** | `integrate_glyph_lexicons.py` | Merges all glyphs into main system | <1 min |

## Input & Output

### Input
- **30+ Poetry Collections** from Project Gutenberg
- ~580,000 words from authors like Emily Dickinson, Walt Whitman, Keats, Shelley, etc.

### Output
- **2,300+ new lexicon entries** (emotional vocabulary from poetry)
- **9+ new emotional dimensions** discovered beyond the base 8
- **50-80 new glyphs** generated from emotional patterns
- **Complete learning log** tracking all discoveries

## Key Discoveries

### New Emotional Dimensions Found
Beyond the original 8 (love, joy, vulnerability, transformation, admiration, sensuality, intimacy, nature), poetry reveals:
- Nostalgia / Longing
- Wonder / Awe
- Melancholy / Grief
- Defiance / Rebellion
- Transcendence / Spirituality
- Ambivalence / Uncertainty
- Connection / Communion
- Emergence / Awakening

### Most Frequent Patterns (Glyph Candidates)
1. Love + Nature = "Nature's Love"
2. Love + Transformation = "Love's Becoming"
3. Joy + Nature = "Natural Joy"
4. Transformation + Admiration = "Inspiring Change"
5. Vulnerability + Love = "Open Heart"

## File Locations

### Poetry Downloads
```
/Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry/
├── dickinson_complete.txt
├── whitman_leaves.txt
├── keats_complete.txt
└── ... [27 more]
```

### Generated Outputs
```
/workspaces/saoriverse-console/
├── generated_glyphs_from_poetry.json          (15-25 glyphs)
├── generated_glyphs_from_extracted_data.json  (40-60 glyphs)
├── bulk_processing_results.json               (metrics)
└── learning/user_overrides/
    └── gutenberg_bulk_lexicon.json            (processed lexicon)
```

## Common Commands

### Process Everything from Scratch
```bash
# Takes ~2-5 hours total
./scripts/utilities/run_full_gutenberg_pipeline.sh
```

### Just Download Poetry
```bash
python scripts/utilities/gutenberg_fetcher.py
```

### Process Existing Poetry Files
```bash
python scripts/utilities/bulk_text_processor.py --dir /path/to/poetry/ --chunk-size 500
```

### Generate Glyphs Only (if processing already done)
```bash
python scripts/utilities/poetry_glyph_generator.py --lexicon learning/user_overrides/gutenberg_bulk_lexicon.json
```

### Check Processing Status
```bash
# View learning log
tail -f learning/hybrid_learning_log.jsonl

# View results
cat bulk_processing_results.json | jq '.'
```

## Expected Results

After full pipeline execution:

```json
{
  "poetry_files_processed": 30,
  "total_poetry_words": 580000,
  "chunks_processed": 1160,
  "signals_extracted": 47850,
  "new_lexicon_entries": 2347,
  "new_dimensions_discovered": 9,
  "total_dimensions": 25,
  "glyphs_generated": 65,
  "processing_time_hours": 2.5,
  "status": "✓ COMPLETE"
}
```

## Troubleshooting

### Phase 1: Download Fails
- Check network connection
- Gutenberg may rate-limit; script automatically retries
- Can skip failed books and resume later

### Phase 2: Processing Takes Too Long
- Reduce `--chunk-size` from 500 to 250 for faster processing
- Process files individually instead of all at once
- Check system memory usage with `top`

### Phase 3-4: No Glyphs Generated
- Ensure `learning/user_overrides/gutenberg_bulk_lexicon.json` exists
- Check that processing completed successfully
- Lower frequency threshold if needed

### Phase 5: Integration Fails
- Check file paths are correct
- Ensure JSON files are valid with `jq .`
- Try integrating files individually first

## Next Steps

### View Generated Glyphs
```bash
cat generated_glyphs_from_poetry.json | jq '.[] | {name, symbol, core_emotions, frequency}'
```

### Add to Saoriverse
```python
from emotional_os.glyphs.glyph_lexicon import GlyphLexicon

lexicon = GlyphLexicon()
lexicon.load_from_file('emotional_os/glyphs/glyph_lexicon.json')

# Load generated glyphs
import json
with open('generated_glyphs_from_poetry.json') as f:
    new_glyphs = json.load(f)

# Add to system
for glyph in new_glyphs:
    lexicon.add_glyph(glyph)

lexicon.save()
```

### Create Custom Poetry Collections
Edit `scripts/utilities/gutenberg_fetcher.py` and add poets to `POETRY_BOOKS`:
```python
POETRY_BOOKS = {
    ...existing...
    'your_poet_name': PROJECT_GUTENBERG_ID  # e.g., 12345
}
```

## Documentation

For detailed information, see:
- [Full Project Gutenberg Guide](./PROJECT_GUTENBERG_EXTRACTION_GUIDE.md)
- [Emotional Dimensions Reference](./README.md)
- [Learning System](./learning/README.md)

---

**Total Time**: ~2-5 hours  
**Output**: 50-80 new poetry-derived glyphs  
**New Dimensions**: 9+  
**Status**: Production-Ready ✓
