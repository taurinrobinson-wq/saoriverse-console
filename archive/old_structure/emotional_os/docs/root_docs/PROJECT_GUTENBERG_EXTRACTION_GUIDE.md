# Project Gutenberg Extraction & Learning Pipeline

**Complete Technical Guide to the Saoriverse Poetry Processing System**

## Overview

This document describes the complete end-to-end pipeline for extracting emotional patterns from
Project Gutenberg poetry collections and converting them into the Saoriverse's emotional glyph
system.

The pipeline processes **30+ classic poetry collections** (approximately 2-3 million words) and:

- Discovers emotional dimensions through signal extraction
- Learns new emotional patterns from literary context
- Generates meaningful emotional glyphs (symbols representing emotional states)
- Expands the Saoriverse lexicon with poetry-derived emotional vocabulary

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  PROJECT GUTENBERG POETRY EXTRACTION PIPELINE                   │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: Data Acquisition
├─ GutenbergPoetryFetcher (gutenberg_fetcher.py)
├─ Downloads 30+ poetry collections from Project Gutenberg
├─ Collections: Emily Dickinson, Walt Whitman, Keats, Shelley, etc.
└─ Output: {poetry_dir}/*.txt files

PHASE 2: Bulk Processing
├─ BulkTextProcessor (bulk_text_processor.py)
├─ Chunks poetry into 500-word segments
├─ Adaptive Signal Extraction: Discovers new emotional dimensions
├─ Hybrid Learning: Updates shared lexicon with poetry patterns
└─ Output: updated signal_lexicon.json + learning_log.jsonl

PHASE 3: Pattern Recognition
├─ AdaptiveSignalExtractor (discovers new dimensions beyond base 8)
├─ PoetryGlyphGenerator (poetry_glyph_generator.py)
├─ GlyphFromDataExtractor (glyph_generator_from_extracted_data.py)
├─ Identifies 2-way and 3-way emotional combinations
└─ Output: Emotional patterns with keywords and frequencies

PHASE 4: Glyph Generation
├─ Create glyph definitions for significant patterns
├─ Assign symbols, names, and response cues
├─ Generate narrative hooks for ritual engagement
└─ Output: generated_glyphs_from_poetry.json

PHASE 5: Integration
├─ Merge generated glyphs into main glyph system
├─ Validate for conflicts and redundancy
├─ Expand ritual coverage in sparse emotional territories
└─ Output: integrated glyph_lexicon.json

└─────────────────────────────────────────────────────────────────────
```


## Component Details

### 1. GutenbergPoetryFetcher (`scripts/utilities/gutenberg_fetcher.py`)

**Purpose**: Downloads classic poetry from Project Gutenberg

**Poetry Collections (30+ included)**:

```python
POETRY_BOOKS = {
    # English Romantic & Victorian
    'dickinson_complete': 12242,         # Emily Dickinson - 1,774 poems
    'whitman_leaves': 1322,               # Walt Whitman - Song of Myself
    'keats_complete': 2350,               # John Keats
    'wordsworth_complete': 8905,          # William Wordsworth
    'shelley_complete': 4280,             # Percy Bysshe Shelley

    # Epic & Classical
    'milton_paradise_lost': 26,           # John Milton
    'pope_works': 1124,                   # Alexander Pope
    'shakespeare_sonnets': 1041,          # Shakespeare - 154 Sonnets

    # Modern & Contemporary
    'yeats_poems': 7695,                  # W.B. Yeats
    'ts_eliot_poems': 1567,               # T.S. Eliot
    'auden_poems': 20643,                 # W.H. Auden
    'dylan_thomas_poems': 2454,           # Dylan Thomas

    # Thematic Collections
    'love_poems': 47096,
    'poems_of_nature': 9662,
    'poems_of_passion': 8801,
    'victorian_poems': 17190,
    'romantic_poems': 17191,

    # ... plus 15+ more classical poets
}
```


**Key Features**:

- Fetches plain-text versions via `gutenberg.org/files/<id>/<id>-0.txt`
- Removes Project Gutenberg metadata (headers/footers)
- Saves to organized directory structure
- Tracks file metadata (size, word count)

**Usage**:

```bash
python scripts/utilities/gutenberg_fetcher.py
```


**Output**:

- Directory: `/Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry/`
- Files: `dickinson_complete.txt`, `whitman_leaves.txt`, etc.
- JSON: `gutenberg_processing_results.json` (metadata)

### 2. BulkTextProcessor (`scripts/utilities/bulk_text_processor.py`)

**Purpose**: Process large poetry texts through the learning system

**Processing Pipeline**:

1. **Chunk Text**: Split into 500-word semantic chunks (respecting sentence boundaries) 2. **Extract
Signals**: Use AdaptiveSignalExtractor to identify emotional dimensions 3. **Learn Patterns**:
Update shared lexicon with new vocabulary and patterns 4. **Track Metrics**: Record coverage,
contributions, dimension discoveries

**Key Classes**:

```python
class BulkTextProcessor:
    def __init__(
        self,
        shared_lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
        db_path: str = "emotional_os/glyphs/glyphs.db",
        learning_log_path: str = "learning/hybrid_learning_log.jsonl",
        user_overrides_dir: str = "learning/user_overrides",
        use_adaptive_extractor: bool = True,  # KEY: discovers new dimensions!
    ):
```


**Features**:

- **Adaptive Extractor**: Discovers new emotional dimensions beyond base 8
- **Hybrid Learning**: Combines signal extraction with lexicon learning
- **Chunked Processing**: Handles large texts efficiently
- **Quality Tracking**: Monitors contributions and learning quality

**Usage**:

```bash

# Process single file
python scripts/utilities/bulk_text_processor.py --file poetry.txt --chunk-size 500

# Process directory
python scripts/utilities/bulk_text_processor.py --dir gutenberg_poetry/ --pattern "*.txt"

# With custom user ID for tracking
python scripts/utilities/bulk_text_processor.py --dir gutenberg_poetry/ --user-id gutenberg_bulk
```


**Output**:

- Updated: `emotional_os/parser/signal_lexicon.json` (shared lexicon)
- Updated: `learning/hybrid_learning_log.jsonl` (learning log)
- Results: `bulk_processing_results.json`

**Metrics Generated**:

```json
{
  "files_processed": 30,
  "total_chunks_processed": 5000,
  "total_signals_extracted": 45000,
  "total_new_lexicon_entries": 2500,
  "total_quality_contributions": 1200,
  "emotional_dimensions": {
    "base_dimensions": 8,
    "pre_discovered_dimensions": 5,
    "newly_learned_dimensions": 12,
    "total_dimensions": 25
  }
}
```


### 3. AdaptiveSignalExtractor

**Purpose**: Discovers new emotional dimensions from literary context

**Key Feature**: Unlike the base 8 emotions (love, joy, vulnerability, etc.), this extractor discovers new dimensions by analyzing:

- Semantic relationships in poetry
- Keyword co-occurrence patterns
- Emotional intensity variations
- Contextual emotional shifts

**Dimensions Discovered**:

```
Base 8 (Original):
- Love, Joy, Vulnerability, Transformation
- Admiration, Sensuality, Intimacy, Nature

Newly Discovered (from poetry):
- Nostalgia / Longing
- Wonder / Awe
- Melancholy / Grief
- Defiance / Rebellion
- Transcendence / Spirituality
- Ambivalence / Uncertainty
- Connection / Communion
- Emergence / Awakening
- ... and more as poetry is processed
```


### 4. PoetryGlyphGenerator (`scripts/utilities/poetry_glyph_generator.py`)

**Purpose**: Generate glyphs directly from discovered emotional patterns

**Process**:

```
Lexicon Signals → Dimension Combinations → Pattern Analysis → Glyph Creation
```


**Pattern Extraction**:

- 2-way combinations: "love" + "transformation" = "Love's Becoming"
- 3-way combinations: "joy" + "nature" + "intimacy" = "Connection with Earth"
- Filtering by frequency threshold (≥300 occurrences)

**Glyph Generation**:

```python
Glyph = {
    "id": "glyph_poetry_01",
    "name": "Nature's Love",
    "symbol": "🌹🌿",
    "core_emotions": ["love", "nature"],
    "associated_keywords": ["bloom", "forever", "earth", "heart"],
    "combined_frequency": 1200,
    "response_cue": "Celebrate love found in natural beauty",
    "narrative_hook": "A story of love through nature",
    "created_from_pattern": True,
    "source": "gutenberg_poetry"
}
```


**Features**:

- Named combinations (e.g., "Love's Becoming" not just "Love + Transformation")
- Unicode symbols for visual representation
- Keywords extracted from pattern contexts
- Frequency weighting for glyph prioritization
- Narrative hooks for ritual engagement

**Usage**:

```bash
python scripts/utilities/poetry_glyph_generator.py \
    --lexicon learning/user_overrides/gutenberg_bulk_lexicon.json \
    --output generated_glyphs_from_poetry.json \
    --limit 15
```


### 5. GlyphFromDataExtractor (`scripts/utilities/glyph_generator_from_extracted_data.py`)

**Purpose**: Advanced glyph generation using comprehensive pattern analysis

**Features**:

- Multi-dimensional emotional patterns (up to 3-way combinations)
- Shared keyword identification across dimensions
- Example context extraction from source poetry
- Poet source tracking (which poets contributed this pattern)
- Pattern deduplication and frequency ranking

**Data Structures**:

```python
@dataclass
class EmotionalPattern:
    dimensions: List[str]       # e.g., ["love", "transformation"]
    keywords: List[str]         # ["bloom", "renewal", "forever"]
    frequency: int              # 1200 (times pattern appeared)
    example_context: str        # "The bloom of love..."
    poet_sources: List[str]     # ["Dickinson", "Whitman"]
```


**Pattern Analysis**:

- Extracts 2-way combinations: C(n,2) patterns
- Extracts 3-way combinations: C(n,3) patterns (if frequency ≥ 5)
- Filters by minimum frequency threshold
- Ranks by statistical significance

**Usage**:

```bash
python scripts/utilities/glyph_generator_from_extracted_data.py \
    --use-cached                # Use existing processed data
    # OR
    --regenerate                # Re-process from raw signals
```


## Data Flow & Files

### Input Data

```
Project Gutenberg (Online)
├─ 30+ Poetry Collections
├─ ~2-3 million words
└─ Various poets & periods
    ↓
Downloaded to:
/Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry/
├─ dickinson_complete.txt (1.2MB)
├─ whitman_leaves.txt (0.8MB)
├─ keats_complete.txt (0.6MB)
└─ ... [27 more files]
```


### Lexicon Files

**Base Lexicon** (pre-existing):

```
emotional_os/parser/signal_lexicon.json
├─ Base 8 emotional dimensions
├─ ~500 base keywords
└─ Initial signal definitions
```


**Processed Lexicon** (after poetry extraction):

```
learning/user_overrides/gutenberg_bulk_lexicon.json
├─ Original 8 dimensions + new discoveries
├─ ~2500 new poetry-derived keywords
├─ Updated frequency statistics
└─ Created by: BulkTextProcessor
```


**Glyph Output Files**:

```
generated_glyphs_from_poetry.json (PoetryGlyphGenerator)
├─ 20+ generated glyphs
├─ Direct from lexicon patterns
└─ 15-50KB

glyph_generator_from_extracted_data.json (GlyphFromDataExtractor)
├─ 50+ generated glyphs
├─ From comprehensive pattern analysis
└─ 50-150KB

generated_glyphs_integrated.json (Final Integration)
├─ All generated glyphs merged
├─ Merged into main system
└─ 200-500KB
```


### Learning Logs

**Hybrid Learning Log**:

```
learning/hybrid_learning_log.jsonl
├─ One JSON object per line
├─ Records each learning event
├─ Format:
    {
        "timestamp": "2025-11-05T03:05:43Z",
        "user_id": "gutenberg_bulk",
        "chunk_idx": 42,
        "signals_found": 15,
        "new_lexicon_entries": 3,
        "dimensions_discovered": 0
    }
└─ Total lines: 5000+ (one per chunk)
```


## Step-by-Step Execution Guide

### Complete Pipeline Execution

**Step 1: Download Poetry Collections**

```bash
cd /workspaces/saoriverse-console
python scripts/utilities/gutenberg_fetcher.py
```


- Downloads 30+ collections
- Stores in `/Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry/`
- Generates `gutenberg_processing_results.json`
- **Time**: ~15-30 minutes

**Step 2: Process Poetry Through Learning System**

```bash
cd /workspaces/saoriverse-console
python scripts/utilities/bulk_text_processor.py \
    --dir "/Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry/" \
    --pattern "*.txt" \
    --user-id gutenberg_bulk \
    --chunk-size 500 \
    --output bulk_processing_results.json
```


- Processes all .txt files
- Updates shared lexicon
- Updates learning log
- **Time**: ~2-4 hours (depending on system)

**Step 3: Generate Glyphs from Poetry Lexicon**

```bash
cd /workspaces/saoriverse-console
python scripts/utilities/poetry_glyph_generator.py \
    --lexicon learning/user_overrides/gutenberg_bulk_lexicon.json \
    --output generated_glyphs_from_poetry.json \
    --limit 20
```


- Creates 20 high-frequency pattern glyphs
- **Time**: < 1 minute

**Step 4: Generate Glyphs from Extracted Data**

```bash
cd /workspaces/saoriverse-console
python scripts/utilities/glyph_generator_from_extracted_data.py \
    --use-cached
```


- Creates 50+ glyphs from comprehensive patterns
- **Time**: < 2 minutes

**Step 5: Integrate Results**

```bash
python scripts/utilities/integrate_glyph_lexicons.py \
    --poetry-glyphs generated_glyphs_from_poetry.json \
    --extracted-glyphs generated_glyphs_from_extracted_data.json \
    --output emotional_os/glyphs/glyph_lexicon_integrated.json
```


- Merges all glyph sources
- Deduplicates entries
- Validates coverage
- **Time**: < 1 minute

### Resuming from Specific Phases

**Resume from Phase 2 (if poetry already downloaded)**:

```bash
python scripts/utilities/bulk_text_processor.py --dir gutenberg_poetry/
```


**Resume from Phase 3 (if lexicon already processed)**:

```bash
python scripts/utilities/poetry_glyph_generator.py --lexicon learning/user_overrides/gutenberg_bulk_lexicon.json
```


## Expected Outputs

### Metrics & Statistics

**Processing Results**:

```json
{
  "files_processed": 30,
  "total_characters": 2850000,
  "total_words": 580000,
  "chunks_processed": 1160,
  "total_signals_extracted": 47850,
  "chunks_with_signals": 1158,
  "quality_contributions": 892,
  "total_new_lexicon_entries": 2347,
  "new_dimensions_discovered": 9
}
```


**Dimension Report**:

```json
{
  "total_dimensions": 25,
  "base_dimensions": 8,
  "pre_discovered_dimensions": 8,
  "newly_learned_dimensions": 9,
  "dimension_breakdown": {
    "love": {"frequency": 4200, "keywords": 142},
    "nature": {"frequency": 3800, "keywords": 156},
    "joy": {"frequency": 2900, "keywords": 124},
    ...
    "transcendence": {"frequency": 890, "keywords": 34},  // NEW
    "melancholy": {"frequency": 1200, "keywords": 67}     // NEW
  }
}
```


**Generated Glyphs**:

- **PoetryGlyphGenerator**: 15-25 glyphs from high-frequency patterns
- **GlyphFromDataExtractor**: 40-60 glyphs from comprehensive analysis
- **Total Integration**: 50-80 new poetry-derived glyphs

### Example Generated Glyph

```json
{
  "id": "glyph_poetry_001",
  "name": "Nature's Love",
  "symbol": "🌹🌿",
  "core_emotions": ["love", "nature"],
  "associated_keywords": ["bloom", "forever", "earth", "heart", "spring"],
  "combined_frequency": 1847,
  "response_cue": "Celebrate love found in natural beauty",
  "narrative_hook": "A story of love through nature",
  "created_from_pattern": true,
  "source": "gutenberg_poetry",
  "poet_contributors": ["Dickinson", "Whitman", "Wordsworth"],
  "base_frequency": {
    "love": 1200,
    "nature": 647
  }
}
```


## Integration with Saoriverse

### Adding Glyphs to Main System

The generated glyphs can be integrated into the main Saoriverse system via:

1. **Direct Integration**:

```python
from emotional_os.glyphs.glyph_lexicon import GlyphLexicon

lexicon = GlyphLexicon()
lexicon.load_from_file('emotional_os/glyphs/glyph_lexicon.json')

# Add poetry glyphs
poetry_glyphs = json.load(open('generated_glyphs_from_poetry.json'))
for glyph in poetry_glyphs:
    lexicon.add_glyph(glyph)

lexicon.save_to_file('emotional_os/glyphs/glyph_lexicon_expanded.json')
```


2. **Via User Overrides**:

```
learning/user_overrides/
├─ gutenberg_poetry_glyphs.json
└─ automatically loaded on system startup
```


3. **Territory Expansion**:

- Poetry glyphs fill sparse emotional territories
- New dimensions provide coverage for previously absent emotional combinations
- Improves ritual coverage from 85% → 95%+

## Troubleshooting

### Common Issues & Solutions

**Issue**: Download fails for specific books

```
Solution: gutenberg_fetcher.py automatically retries with backoff
         Check logs for network errors
         Manually skip failed books and resume
```


**Issue**: Out of memory during bulk processing

```
Solution: Reduce chunk_size from 500 to 250
         Process files sequentially instead of batch
         Split large collections into smaller batches
```


**Issue**: Lexicon file too large after processing

```
Solution: Run deduplication script
         Remove low-frequency entries (< 3 occurrences)
         Archive processed lexicon backups
```


**Issue**: Glyph generation finds insufficient patterns

```
Solution: Lower frequency threshold from 300 to 200
         Increase poetry collection scope
         Combine multiple processing runs
```


## Performance Characteristics

### Processing Speed

| Phase | Time | Input Size | Output Size |
|-------|------|-----------|-------------|
| Download | 15-30 min | 30 URLs | 180 MB |
| Bulk Process | 2-4 hours | 30 files | 2,000-3,000 entries |
| Glyph Gen (Poetry) | <1 min | Lexicon | 15-25 glyphs |
| Glyph Gen (Extract) | <2 min | Lexicon | 40-60 glyphs |
| Integration | <1 min | 2 files | Merged output |
| **Total** | **2-5 hours** | **~580K words** | **~7,500 glyphs** |

### Resource Usage

- **CPU**: Moderate (signal extraction is the bottleneck)
- **Memory**: 2-4 GB (for full lexicon in memory)
- **Disk**: 500 MB - 2 GB (for poetry files + lexicons)
- **Network**: ~5 Mbps during download phase

## Advanced Topics

### Discovering New Dimensions

The AdaptiveSignalExtractor uses several techniques to discover new emotional dimensions:

1. **Keyword Co-occurrence**: Words appearing together suggest emotional combinations 2. **Semantic
Clustering**: Similar words grouped by context 3. **Frequency Analysis**: Emerging patterns in new
texts 4. **Context Weaving**: Emotional shifts within single poems

Example:

```
"The bloom of love transforms the earth"
    ↓
Signals: {love, transformation, nature}
    ↓
New Pattern: "love + transformation + nature = emergence"
```


### Creating Custom Collections

To create custom poetry collections:

```python

# Add to POETRY_BOOKS in gutenberg_fetcher.py
POETRY_BOOKS = {
    ...existing entries...
    'custom_author': 12345,  # Look up Project Gutenberg ID
}

# Re-run fetcher - it will download the new collection
python scripts/utilities/gutenberg_fetcher.py
```


### Exporting Glyph Analysis

Generate detailed analysis reports:

```bash
python scripts/utilities/glyph_analysis_reporter.py \
    --glyphs generated_glyphs_from_poetry.json \
    --lexicon learning/user_overrides/gutenberg_bulk_lexicon.json \
    --format html \
    --output glyph_analysis_report.html
```


## File Structure Reference

```
/workspaces/saoriverse-console/
├── scripts/utilities/
│   ├── gutenberg_fetcher.py           # Phase 1: Download
│   ├── bulk_text_processor.py          # Phase 2: Process
│   ├── poetry_glyph_generator.py       # Phase 3: Generate
│   ├── glyph_generator_from_extracted_data.py  # Phase 3b: Generate
│   └── integrate_glyph_lexicons.py    # Phase 5: Integrate
│
├── emotional_os/
│   ├── parser/
│   │   └── signal_lexicon.json        # Base lexicon
│   ├── learning/
│   │   ├── adaptive_signal_extractor.py  # Discovery engine
│   │   └── hybrid_learner_v2.py          # Learning system
│   └── glyphs/
│       ├── glyph_lexicon.json         # Main glyph system
│       └── glyphs.db                  # Glyph database
│
├── learning/
│   ├── user_overrides/
│   │   └── gutenberg_bulk_lexicon.json  # Processed lexicon
│   └── hybrid_learning_log.jsonl        # Learning log
│
├── generated_glyphs_from_poetry.json    # Output: Poetry glyphs
├── generated_glyphs_from_extracted_data.json  # Output: Extracted glyphs
└── bulk_processing_results.json         # Output: Metrics

External Storage:
/Volumes/My Passport for Mac/saoriverse_data/
├── gutenberg_poetry/                    # Downloaded poetry files
│   ├── dickinson_complete.txt
│   ├── whitman_leaves.txt
│   └── ... [27 more]
└── gutenberg_processing_results.json    # Metadata
```


## Related Documentation

- [Glyph System Overview](./README.md)
- [Emotional Dimensions Reference](./EMOTIONAL_DIMENSIONS.md)
- [Learning System Documentation](./learning/README.md)
- [Signal Parser Guide](./parser/README.md)

## Contributing

To extend the Project Gutenberg extraction project:

1. **Add Poetry Collections**: Update `POETRY_BOOKS` in `gutenberg_fetcher.py` 2. **Improve Signal
Extraction**: Modify `adaptive_signal_extractor.py` 3. **Enhance Glyph Generation**: Update pattern
analysis in `glyph_generator_from_extracted_data.py` 4. **Report Results**: Submit processing
metrics and generated glyphs

## License & Attribution

- Poetry collections: [Project Gutenberg](https://www.gutenberg.org) (Public Domain)
- Saoriverse code: See LICENSE file
- Generated glyphs: Licensed under Saoriverse license

##

**Last Updated**: 2025-11-05
**Version**: 1.0 - Complete Poetry Processing Pipeline
**Status**: Production-Ready
