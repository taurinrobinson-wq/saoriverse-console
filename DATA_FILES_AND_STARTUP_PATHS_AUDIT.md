# 📋 Complete Data Files and Config Audit: Startup Loading Paths

**Date:** December 4, 2025  
**Purpose:** Comprehensive mapping of all data/config files needed at startup, where they're located, where code expects them, and correction paths.

---

## 📊 Executive Summary

The system has **11 critical data files** needed at startup, split across multiple locations. There are significant discrepancies between:
- Where files actually exist in the repo
- Where code is trying to load them from
- What the correct paths should be

---

## 🔍 Complete Data Files Mapping

### 1. **NRC Emotion Lexicon**

| Property | Value |
|----------|-------|
| **File Name** | `nrc_emotion_lexicon.txt` |
| **Actual Location in Repo** | `data/lexicons/nrc_emotion_lexicon.txt` |
| **Code Tries to Load From** | Multiple fallback paths (hardcoded search) |
| **Fallback Paths Searched** | 1. `data/lexicons/nrc_emotion_lexicon.txt` ✓ (matches actual) |
| | 2. `data/lexicons/nrc_lexicon_cleaned.json` |
| | 3. `emotional_os/lexicon/nrc_emotion_lexicon.txt` |
| | 4. Relative path: `src/../../../data/lexicons/nrc_emotion_lexicon.txt` |
| | 5. Relative path: `src/../../../data/lexicons/nrc_lexicon_cleaned.json` |
| **Loader Code** | `src/parser/nrc_lexicon_loader.py` (lines 16-22) |
| **Status** | ✅ **WORKING** - First search path matches actual location |
| **Corrected Path** | `data/lexicons/nrc_emotion_lexicon.txt` (hardcoded in code) |

---

### 2. **Glyph Lexicon (JSON - Primary)**

| Property | Value |
|----------|-------|
| **File Name** | `glyph_lexicon_rows.json` |
| **Actual Location in Repo** | Multiple locations (duplicated): |
| | • `data/glyph_lexicon_rows.json` (primary) |
| | • `src/emotional_os_glyphs/glyph_lexicon_rows.json` (copy) |
| **Code Tries to Load From** | `emotional_os/glyphs/glyph_lexicon_rows.json` (hardcoded default) |
| **Actual Expected Path** | ❌ **PATH MISMATCH** - Directory doesn't match |
| **Modules Using This** | • `GlyphFactorialEngine` (line 73-74) |
| | • `AntonymGlyphsIndexer` (line 27) |
| | • `AntonymGlyphsIntegration` (line 55) |
| | • `AdvancedPruningEngine` (line 89) |
| **Loader Code Files** | • `src/emotional_os_glyphs/glyph_factorial_engine.py` |
| | • `src/emotional_os_glyphs/antonym_glyphs_indexer.py` |
| | • `src/emotional_os_glyphs/advanced_pruning_engine.py` |
| **Status** | ⚠️ **BROKEN** - Expected path doesn't exist |
| **Corrected Path** | Either: |
| | 1. Move file to: `emotional_os/glyphs/glyph_lexicon_rows.json` |
| | 2. OR update code to: `data/glyph_lexicon_rows.json` |

---

### 3. **Glyph Lexicon (CSV - Backup)**

| Property | Value |
|----------|-------|
| **File Name** | `glyph_lexicon_rows.csv` |
| **Actual Location in Repo** | • `data/glyph_lexicon_rows.csv` (primary) |
| | • `src/emotional_os_glyphs/glyph_lexicon_rows.csv` (copy) |
| **Code Tries to Load From** | `emotional_os/glyphs/glyph_lexicon_rows.csv` (hardcoded default) |
| **Actual Expected Path** | ❌ **PATH MISMATCH** - Directory doesn't match |
| **Status** | ⚠️ **BROKEN** - Expected path doesn't exist |
| **Corrected Path** | Either: |
| | 1. Move file to: `emotional_os/glyphs/glyph_lexicon_rows.csv` |
| | 2. OR update code to: `data/glyph_lexicon_rows.csv` |

---

### 4. **Suicidality Protocol Configuration**

| Property | Value |
|----------|-------|
| **File Name** | `suicidality_protocol.json` |
| **Actual Location in Repo** | `src/emotional_os/core/suicidality_protocol.json` |
| **Code Tries to Load From** | `emotional_os/core/suicidality_protocol.json` (hardcoded default) |
| **Loader Code** | `src/emotional_os/core/suicidality_handler.py` (line 33) |
| **Status** | ⚠️ **BROKEN** - Path mismatch when running from root |
| **Note** | Works if code is run from `src/` directory, breaks from repo root |
| **Corrected Path** | `src/emotional_os/core/suicidality_protocol.json` |
| **OR Use PathManager** | Use `PathManager` class for dynamic resolution |

---

### 5. **Signal Lexicon (Base Signals)**

| Property | Value |
|----------|-------|
| **File Name** | `signal_lexicon.json` |
| **Actual Location in Repo** | `src/emotional_os_parser/signal_lexicon.json` |
| **Code Tries to Load From** | Multiple options: |
| | 1. Directly: `parser/signal_lexicon.json` |
| | 2. Or: `emotional_os/parser/signal_lexicon.json` |
| | 3. Via PathManager: searches multiple candidates |
| **Loader Code** | • `src/emotional_os_learning/hybrid_learner_v2.py` (line 62) |
| | • `src/emotional_os_lexicon/lexicon_loader.py` (not directly) |
| | • PathManager: `src/emotional_os/core/paths.py` (line 45-48) |
| **Status** | ⚠️ **PARTIALLY WORKING** |
| | - PathManager finds it (dynamic resolution) |
| | - Direct string paths may fail if wrong directory |
| **Corrected Path** | `src/emotional_os_parser/signal_lexicon.json` |
| | OR use PathManager for dynamic resolution |

---

### 6. **Learned Lexicon (Runtime Updates)**

| Property | Value |
|----------|-------|
| **File Name** | `learned_lexicon.json` |
| **Actual Location in Repo** | `src/emotional_os_parser/learned_lexicon.json` (template) |
| **Runtime Location** | Gets created at: `emotional_os/parser/learned_lexicon.json` |
| **Code Tries to Load From** | Via PathManager (multiple candidates): |
| | 1. `parser/learned_lexicon.json` |
| | 2. `data/lexicons/learned_lexicon.json` |
| | 3. `emotional_os/parser/learned_lexicon.json` |
| **Loader Code** | `src/emotional_os/core/paths.py` (line 51-55) |
| **Status** | ✅ **WORKING** - PathManager provides fallbacks |
| **Corrected Path** | `src/emotional_os_parser/learned_lexicon.json` (template) |

---

### 7. **Trauma Lexicon (Safety System)**

| Property | Value |
|----------|-------|
| **File Name** | `trauma_lexicon.json` |
| **Actual Location in Repo** | `src/emotional_os_safety/trauma_lexicon.json` |
| **Code Tries to Load From** | Relative to file location: `os.path.join(os.path.dirname(__file__), "trauma_lexicon.json")` |
| **Loader Code** | • `src/emotional_os_safety/sanctuary.py` (line 13) |
| | • `src/emotional_os_safety/sanctuary_handler.py` (line 9) |
| **Status** | ✅ **WORKING** - Uses relative path from module location |
| **Corrected Path** | No change needed - relative path works |

---

### 8. **Runtime Fallback Lexicon (Parser)**

| Property | Value |
|----------|-------|
| **File Name** | `runtime_fallback_lexicon.json` |
| **Actual Location in Repo** | `src/emotional_os_parser/runtime_fallback_lexicon.json` |
| **Code Tries to Load From** | `emotional_os/parser/runtime_fallback_lexicon.json` |
| **Loader Code** | `scripts/data/clean_and_salvage_glyphs.py` (line 22) |
| **Status** | ⚠️ **BROKEN** - Path mismatch |
| **Corrected Path** | `src/emotional_os_parser/runtime_fallback_lexicon.json` |

---

### 9. **Word-Centric Emotional Lexicon**

| Property | Value |
|----------|-------|
| **File Name** | `word_centric_emotional_lexicon_expanded.json` |
| **Actual Location in Repo** | `data/word_centric_emotional_lexicon_expanded.json` |
| **Code Tries to Load From** | `emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json` |
| **Loader Code** | `src/emotional_os_lexicon/lexicon_loader.py` (line 18) |
| **Status** | ⚠️ **BROKEN** - Path mismatch |
| **Alternative File** | `src/emotional_os_lexicon/word_centric_emotional_lexicon.json` also exists |
| **Corrected Path** | Either: |
| | 1. Move to: `emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json` |
| | 2. OR update code to: `data/word_centric_emotional_lexicon_expanded.json` |

---

### 10. **Antonym Glyphs Index**

| Property | Value |
|----------|-------|
| **File Name** | `antonym_glyphs_indexed.json` |
| **Actual Location in Repo** | • `data/antonym_glyphs_indexed.json` |
| | • `src/emotional_os_glyphs/antonym_glyphs_indexed.json` |
| **Code Tries to Load From** | `emotional_os/glyphs/antonym_glyphs_indexed.json` |
| **Loader Code** | `src/emotional_os_glyphs/antonym_glyphs_indexer.py` (line 27) |
| **Status** | ⚠️ **BROKEN** - Path mismatch |
| **Corrected Path** | Move to: `emotional_os/glyphs/antonym_glyphs_indexed.json` |

---

### 11. **Glyph Database (SQLite)**

| Property | Value |
|----------|-------|
| **File Name** | `glyphs.db` |
| **Actual Location in Repo** | No file found yet (gets created on first load) |
| **Code Tries to Load From** | Via PathManager: |
| | 1. `glyphs.db` |
| | 2. `data/glyphs.db` |
| **Loader Code** | • `src/emotional_os/core/paths.py` (line 62) |
| | • Multiple modules use: `db_path="emotional_os/glyphs/glyphs.db"` |
| **Status** | ⚠️ **INCONSISTENT** - Code uses different paths: |
| | • PathManager searches: `glyphs.db`, `data/glyphs.db` |
| | • Code hardcodes: `emotional_os/glyphs/glyphs.db` |
| **Corrected Path** | Standardize to: `emotional_os/glyphs/glyphs.db` |

---

## 📂 Directory Structure Issues

### Current State:
```
d:\saoriverse-console\
├── data/
│   ├── glyph_lexicon_rows.json
│   ├── glyph_lexicon_rows.csv
│   ├── antonym_glyphs_indexed.json
│   ├── word_centric_emotional_lexicon_expanded.json
│   └── lexicons/
│       └── nrc_emotion_lexicon.txt
│
├── src/
│   ├── emotional_os/
│   │   └── core/
│   │       ├── suicidality_protocol.json  ✓
│   │       └── (other files)
│   │
│   ├── emotional_os_glyphs/
│   │   ├── glyph_lexicon_rows.json (copy)
│   │   ├── glyph_lexicon_rows.csv (copy)
│   │   ├── antonym_glyphs_indexed.json (copy)
│   │   └── (other modules)
│   │
│   ├── emotional_os_parser/
│   │   ├── signal_lexicon.json  ✓
│   │   ├── learned_lexicon.json
│   │   ├── runtime_fallback_lexicon.json
│   │   └── (other modules)
│   │
│   ├── emotional_os_lexicon/
│   │   ├── word_centric_emotional_lexicon.json
│   │   ├── word_centric_emotional_lexicon_expanded.json
│   │   └── (other modules)
│   │
│   └── emotional_os_safety/
│       ├── trauma_lexicon.json  ✓
│       └── (other modules)
│
└── (emotional_os/ - MISSING - doesn't exist at repo root)
    └── glyphs/ - Expected by code but directory not created
```

### Problems Identified:
1. **No `emotional_os/` directory at repo root** - Code expects it
2. **Duplicate data files** - Same files in `data/` and `src/*/`
3. **Path inconsistencies** - Code sometimes uses `src/...`, sometimes `data/...`, sometimes `emotional_os/...`
4. **No dynamic resolution** - Many modules hardcode paths instead of using PathManager

---

## 🔧 Required Corrections

### Option A: Create Missing Directory Structure
Create `emotional_os/glyphs/` at repo root and move files there:
```bash
mkdir -p emotional_os/glyphs
cp data/glyph_lexicon_rows.json emotional_os/glyphs/
cp data/glyph_lexicon_rows.csv emotional_os/glyphs/
cp data/antonym_glyphs_indexed.json emotional_os/glyphs/
```

### Option B: Update Code to Use Correct Paths
Modify all file loading code to use:
- `data/glyph_lexicon_rows.json` instead of `emotional_os/glyphs/glyph_lexicon_rows.json`
- `data/antonym_glyphs_indexed.json` instead of `emotional_os/glyphs/antonym_glyphs_indexed.json`
- Use PathManager for dynamic resolution

### Option C: Hybrid Approach (RECOMMENDED)
1. **Keep current structure as-is** for backward compatibility
2. **Update PathManager** in `src/emotional_os/core/paths.py` to include all candidate locations
3. **Standardize all code** to use PathManager instead of hardcoded paths
4. **Add startup validation** to check all required files exist

---

## 📋 Startup File Checklist

These files **MUST** exist before the system can start:

| File | Location | Type | Purpose |
|------|----------|------|---------|
| `nrc_emotion_lexicon.txt` | `data/lexicons/` | TSV | Base emotion mapping |
| `glyph_lexicon_rows.json` | `data/` or `emotional_os/glyphs/` | JSON | Primary glyph vocabulary |
| `glyph_lexicon_rows.csv` | `data/` or `emotional_os/glyphs/` | CSV | Backup glyph lexicon |
| `suicidality_protocol.json` | `src/emotional_os/core/` | JSON | Crisis protocol config |
| `signal_lexicon.json` | `src/emotional_os_parser/` | JSON | Base signal definitions |
| `trauma_lexicon.json` | `src/emotional_os_safety/` | JSON | Trauma keywords |
| `word_centric_emotional_lexicon_expanded.json` | `data/` or `src/emotional_os_lexicon/` | JSON | Word->emotion mapping |
| `antonym_glyphs_indexed.json` | `data/` or `emotional_os/glyphs/` | JSON | Antonym pairs index |

---

## 🚀 Recommended Implementation Priority

**Priority 1 (Critical):**
- [ ] Create `emotional_os/glyphs/` directory
- [ ] Verify all 8 startup files exist in their expected locations
- [ ] Add startup validation script

**Priority 2 (Important):**
- [ ] Update PathManager to handle all actual file locations
- [ ] Add logging to show which paths are being searched
- [ ] Document actual vs. expected paths in README

**Priority 3 (Nice to Have):**
- [ ] Refactor all hardcoded paths to use PathManager
- [ ] Remove duplicate files and consolidate to single location
- [ ] Add configuration file to override default paths

---

## 📝 Notes

- **PathManager** (`src/emotional_os/core/paths.py`) exists but is underutilized
- Many modules bypass PathManager and use hardcoded strings
- The `src/` directory is treated as a module prefix in code, not a literal directory
- Tests use multiple path variants, indicating path resolution is fragile
- Learning system creates new files dynamically in `learning/` directory

