# 📊 Quick Reference: Data Files Startup Paths

## Summary Table

| File Name | Actual Location | Code Expects | Status | Fix |
|-----------|-----------------|--------------|--------|-----|
| `nrc_emotion_lexicon.txt` | `data/lexicons/` | `data/lexicons/` (via search) | ✅ Works | None needed |
| `glyph_lexicon_rows.json` | `data/` + `src/emotional_os_glyphs/` | `emotional_os/glyphs/` | ❌ Broken | Create dir or update code |
| `glyph_lexicon_rows.csv` | `data/` + `src/emotional_os_glyphs/` | `emotional_os/glyphs/` | ❌ Broken | Create dir or update code |
| `suicidality_protocol.json` | `src/emotional_os/core/` | `emotional_os/core/` | ⚠️ Partial | Use PathManager |
| `signal_lexicon.json` | `src/emotional_os_parser/` | Via PathManager | ✅ Works | None needed |
| `learned_lexicon.json` | `src/emotional_os_parser/` | Via PathManager | ✅ Works | None needed |
| `runtime_fallback_lexicon.json` | `src/emotional_os_parser/` | `emotional_os/parser/` | ❌ Broken | Create dir or update code |
| `trauma_lexicon.json` | `src/emotional_os_safety/` | Relative path | ✅ Works | None needed |
| `word_centric_emotional_lexicon_expanded.json` | `data/` | `emotional_os/lexicon/` | ❌ Broken | Create dir or update code |
| `antonym_glyphs_indexed.json` | `data/` + `src/emotional_os_glyphs/` | `emotional_os/glyphs/` | ❌ Broken | Create dir or update code |
| `glyphs.db` | (Created at runtime) | `emotional_os/glyphs/` | ⚠️ Inconsistent | Standardize path |

**Legend:**
- ✅ **Works** - File found and loads correctly
- ⚠️ **Partial** - Works in some cases but not all
- ❌ **Broken** - File not found or path mismatch
##

## Key Issues at a Glance

### Path Mismatches (Most Critical)

**Problem:** Code expects `emotional_os/` directory at repo root, but it doesn't exist.

**Modules Affected:**
- `GlyphFactorialEngine` - expects `emotional_os/glyphs/glyph_lexicon_rows.json`
- `AntonymGlyphsIndexer` - expects `emotional_os/glyphs/antonym_glyphs_indexed.json`
- `WordCentricLexicon` - expects `emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json`

**Files Actually Located:**
- `data/glyph_lexicon_rows.json` (actual)
- `src/emotional_os_parser/signal_lexicon.json` (actual)
- `src/emotional_os_safety/trauma_lexicon.json` (actual)
##

## Modules by Load Behavior

### Using PathManager (Dynamic - ✅ SAFE)
- `src/emotional_os/core/lexicon_learner.py`
- `src/emotional_os_learning/hybrid_learner_v2.py`

### Hardcoding Paths (Fragile - ⚠️ RISKY)
- `src/emotional_os_glyphs/glyph_factorial_engine.py`
- `src/emotional_os_glyphs/antonym_glyphs_indexer.py`
- `src/emotional_os_glyphs/advanced_pruning_engine.py`
- `src/emotional_os_lexicon/lexicon_loader.py`
- `src/emotional_os_safety/sanctuary.py`

### Using Search/Fallback (Flexible - ✅ GOOD)
- `src/parser/nrc_lexicon_loader.py` (searches 5 locations)
##

## Quick Diagnostic

### Check if File Can Be Found

**Run this to verify startup:**

```python
from pathlib import Path

files_to_check = {
    "nrc_emotion_lexicon.txt": [
        Path("data/lexicons/nrc_emotion_lexicon.txt"),
    ],
    "glyph_lexicon_rows.json": [
        Path("emotional_os/glyphs/glyph_lexicon_rows.json"),
        Path("data/glyph_lexicon_rows.json"),
        Path("src/emotional_os_glyphs/glyph_lexicon_rows.json"),
    ],
    "suicidality_protocol.json": [
        Path("emotional_os/core/suicidality_protocol.json"),
        Path("src/emotional_os/core/suicidality_protocol.json"),
    ],
    "signal_lexicon.json": [
        Path("emotional_os/parser/signal_lexicon.json"),
        Path("src/emotional_os_parser/signal_lexicon.json"),
        Path("parser/signal_lexicon.json"),
    ],
    "trauma_lexicon.json": [
        Path("src/emotional_os_safety/trauma_lexicon.json"),
    ],
    "word_centric_emotional_lexicon_expanded.json": [
        Path("emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json"),
        Path("data/word_centric_emotional_lexicon_expanded.json"),
        Path("src/emotional_os_lexicon/word_centric_emotional_lexicon_expanded.json"),
    ],
    "antonym_glyphs_indexed.json": [
        Path("emotional_os/glyphs/antonym_glyphs_indexed.json"),
        Path("data/antonym_glyphs_indexed.json"),
        Path("src/emotional_os_glyphs/antonym_glyphs_indexed.json"),
    ],
}

for fname, paths in files_to_check.items():
    found = False
    for p in paths:
        if p.exists():
            print(f"✅ {fname}: Found at {p}")
            found = True
            break
    if not found:
        print(f"❌ {fname}: NOT FOUND - searched {[str(p) for p in paths]}")
```


##

## Configuration by Module

### Glyph System (`src/emotional_os_glyphs/`)
- Expects: `emotional_os/glyphs/glyph_lexicon_rows.{json,csv}`
- Also expects: `emotional_os/glyphs/antonym_glyphs_indexed.json`
- Database: `emotional_os/glyphs/glyphs.db`

### Parser System (`src/emotional_os_parser/`)
- Has: `signal_lexicon.json` (relative location)
- Has: `learned_lexicon.json` (gets updated)
- Has: `runtime_fallback_lexicon.json`

### Safety System (`src/emotional_os_safety/`)
- Has: `trauma_lexicon.json` (using relative path ✅)
- Uses: `suicidality_protocol.json` (from `src/emotional_os/core/`)

### Lexicon System (`src/emotional_os_lexicon/`)
- Expects: `emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json`
- Actual: `data/word_centric_emotional_lexicon_expanded.json`

### Learning System (`learning/`)
- Creates: `hybrid_learning_log.jsonl` at runtime
- Creates: `user_overrides/{user_id}_lexicon.json` per user
##

## Startup Order

When the app starts, these files are loaded in this order:

1. **NRC Lexicon** → `data/lexicons/nrc_emotion_lexicon.txt`
2. **Signal Lexicon** → `src/emotional_os_parser/signal_lexicon.json` (or via PathManager)
3. **Glyph Lexicon** → ❌ **FAILS** - expects `emotional_os/glyphs/`
4. **Suicidality Protocol** → ⚠️ **PARTIAL** - expects `emotional_os/core/`
5. **Trauma Lexicon** → `src/emotional_os_safety/trauma_lexicon.json` ✅
6. **Word Lexicon** → ❌ **FAILS** - expects `emotional_os/lexicon/`
##

## Recommended Minimal Fix

**Fastest solution to get system working:**

```bash

# Create missing directory structure
mkdir -p emotional_os/glyphs
mkdir -p emotional_os/core
mkdir -p emotional_os/parser
mkdir -p emotional_os/lexicon
mkdir -p emotional_os/safety

# Copy files (or symlink if on same filesystem)
cp data/glyph_lexicon_rows.json emotional_os/glyphs/
cp data/glyph_lexicon_rows.csv emotional_os/glyphs/
cp data/antonym_glyphs_indexed.json emotional_os/glyphs/
cp src/emotional_os_parser/signal_lexicon.json emotional_os/parser/
cp src/emotional_os_parser/runtime_fallback_lexicon.json emotional_os/parser/
cp src/emotional_os_lexicon/word_centric_emotional_lexicon_expanded.json emotional_os/lexicon/
cp src/emotional_os_safety/trauma_lexicon.json emotional_os/safety/
cp src/emotional_os/core/suicidality_protocol.json emotional_os/core/
```



This ensures all hardcoded paths will work immediately.
##

## Recommended Long-Term Fix

1. Use `PathManager` everywhere instead of hardcoded paths
2. Remove duplicate files (keep only in `data/` or `src/`)
3. Add startup validation: `python -m src.emotional_os.core.startup_check`
4. Document expected file structure in README
