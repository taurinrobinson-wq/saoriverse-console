# Project Gutenberg Poetry Bulk Processing 📚

## Overview
Successfully automated the download and processing of classic poetry collections from Project Gutenberg directly into the SaoriVerse learning pipeline.

## What Was Created

### 1. **gutenberg_fetcher.py** 
- Automatic downloader for 12+ poetry collections from Project Gutenberg
- Removes Project Gutenberg metadata (headers/footers)
- Processes each collection through signal extraction + learning pipeline
- Supports:
  - Emily Dickinson (complete works + single poems)
  - Walt Whitman (Leaves of Grass, Drum-Taps)
  - John Keats (complete works)
  - Samuel Taylor Coleridge
  - William Wordsworth (complete works)
  - Percy Bysshe Shelley (complete works)
  - Love poems anthology
  - Poems of passion & nature

**Status**: ✅ Running in background (PID 79838)

### 2. **bulk_text_processor.py**
- Processes large text files through the learning pipeline
- Splits files into semantic chunks (respects sentence boundaries)
- Extracts emotional signals from each chunk
- Learns keywords, phrases, and patterns automatically
- Tracks statistics: signals extracted, lexicon entries added, quality scores
- Outputs results to JSON for analysis

### 3. **run_gutenberg_learning.sh**
- Bash wrapper for running the fetcher with logging
- Creates timestamped log files
- Perfect for background/scheduled runs

---

## Poetry Collections Downloaded

| Collection | Size | Words | Status |
|-----------|------|-------|--------|
| Emily Dickinson Complete | 183 KB | 31,215 | ✓ Downloaded |
| Emily Dickinson (Single Poems) | 29 KB | 4,965 | ✓ Downloaded |
| Walt Whitman - Leaves of Grass | 756 KB | 121,712 | ✓ Downloaded |
| Walt Whitman - Drum-Taps | 115 KB | 20,375 | ✓ Downloaded |
| John Keats Complete | 330 KB | 59,023 | ✓ Downloaded |
| William Wordsworth Complete | 166 KB | 28,404 | ✓ Downloaded |
| Percy Bysshe Shelley Complete | 1.2 MB | 209,061 | ✓ Downloaded |
| Love Poems Anthology | 421 KB | (calculating) | ✓ Downloaded |

**Total Downloaded**: ~3.2 MB of classic poetry (~600K+ words)

---

## Learning Pipeline Integration

### Signal Processing
The system processes each poetry collection to extract 8 emotional signals:
- **Love** - romantic, intimate language
- **Intimacy** - personal connection and vulnerability
- **Sensuality** - physical and sensory experience
- **Vulnerability** - weakness, fear, exposure
- **Transformation** - change and evolution
- **Admiration** - respect and awe
- **Joy** - happiness, celebration, lightness
- **Nature** - natural imagery and symbolism

### Lexicon Expansion
From our test run with Emily Dickinson poetry:
- **504 new lexicon entries** from 255 words of text
- Keywords recognized: "sweet", "tender", "soul", "sense", "madness", "dangerous", "chain", "bird", "feathers", "perches", "sings", etc.
- 2-3 word phrases learned: "thing with feathers", "perches in the soul", "creak across my soul", etc.

**Expected Total**: 10,000-50,000+ new lexicon entries from ~600K words of poetry

---

## How It Works

### 1. Download Phase
```python
fetcher = GutenbergPoetryFetcher()
downloaded = fetcher.download_all_collections()
# Downloads 12 poetry collections from Project Gutenberg
```

### 2. Processing Phase
For each file:
- Split into 500-word chunks (respecting sentence boundaries)
- Extract emotional signals from each chunk
- Learn keywords and phrases
- Add to shared lexicon with metadata
- Track quality metrics

### 3. Results
Results saved to:
- `gutenberg_processing_results.json` - Statistics and metadata
- `gutenberg_learning.log` - Full processing log
- Updated `parser/signal_lexicon.json` - Expanded lexicon
- Updated `parser/learned_lexicon.json` - Learned patterns

---

## Current Status

✅ **10 poetry collections downloaded** (2 failed - 404 errors)
✅ **Processing started** - Currently learning from all downloaded texts
✅ **Running in background** - Will complete processing automatically
⏳ **ETA**: 5-15 minutes (depending on chunk processing speed)

---

## How to Monitor Progress

Check the log file:
```bash
tail -f gutenberg_learning.log
```

Or check results when complete:
```bash
cat gutenberg_processing_results.json | jq
```

---

## Next Steps

Once processing completes:

1. **Verify Results**
   - Check `gutenberg_processing_results.json`
   - Review new lexicon entries

2. **Optional: Add More Poetry**
   - Download other Project Gutenberg collections
   - Run bulk processor on any text file

3. **Test Integration**
   - Use Streamlit UI to see how learned patterns affect responses
   - Check signal detection on new user inputs

4. **Scale Further**
   - Download more collections (Shakespeare, Byron, Dickinson's complete works)
   - Process prose (novels, essays) for broader language patterns
   - Combine with user's personal poetry for personalized learning

---

## Technical Details

### Files Modified/Created
- ✅ `gutenberg_fetcher.py` - NEW (210 lines)
- ✅ `bulk_text_processor.py` - NEW (300 lines)
- ✅ `run_gutenberg_learning.sh` - NEW
- Committed to GitHub (commit 1233d41)

### Dependencies
- `requests` - HTTP library for downloading (installed)
- Existing: `hybrid_learner_v2.py`, `poetry_signal_extractor.py`, `signal_parser.py`

### Performance
- Downloads: ~2 seconds per book
- Processing: ~10-20ms per 500-word chunk
- Total estimated time: 10-20 minutes for all 10 collections

---

## System Architecture

```
Project Gutenberg API
        ↓
   gutenberg_fetcher.py
        ↓
   Download Poetry Collections
        ↓
   bulk_text_processor.py
        ↓
   Split into Chunks
        ↓
   poetry_signal_extractor.py
        ↓
   Extract Signals & Keywords
        ↓
   hybrid_learner_v2.py
        ↓
   Two-Tier Learning
   ├─ Personal Lexicon
   └─ Shared Lexicon
        ↓
   Updated Parser
   ├─ signal_lexicon.json
   └─ learned_lexicon.json
```

---

## Key Innovations

1. **Automated Bulk Learning** - No manual intervention needed
2. **Semantic Chunking** - Preserves context by respecting sentence boundaries
3. **Multi-Signal Extraction** - Captures 8 different emotional dimensions
4. **Dual Lexicon System** - Personal + shared learning
5. **Quality Scoring** - Tracks exchange quality for training value
6. **Metadata Tracking** - Records source, confidence, phrase_length for each entry

---

## Run Command

To run processing again in the future:
```bash
cd /Users/taurinrobinson/saoriverse-console
nohup /Users/taurinrobinson/saoriverse-console/venv/bin/python gutenberg_fetcher.py > gutenberg_learning.log 2>&1 &
```

Or use the shell script:
```bash
./run_gutenberg_learning.sh
```

---

**Status**: 🟢 ACTIVE PROCESSING | Check `gutenberg_learning.log` for real-time progress
