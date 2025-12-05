# 🎯 FINAL COMPREHENSIVE LIST - All Data Files Mapped

**Generated:** December 4, 2025  
**Status:** Complete Audit Ready for Implementation

---

## SUMMARY: 11 CRITICAL STARTUP FILES

### ✅ 4 Files That Work

| # | File Name | Actual Location | How It Works | Status |
|---|-----------|-----------------|--------------|--------|
| 1 | `nrc_emotion_lexicon.txt` | `data/lexicons/` | Fallback search (5 paths) | ✅ WORKS |
| 2 | `signal_lexicon.json` | `src/emotional_os_parser/` | PathManager | ✅ WORKS |
| 3 | `learned_lexicon.json` | `src/emotional_os_parser/` | PathManager | ✅ WORKS |
| 4 | `trauma_lexicon.json` | `src/emotional_os_safety/` | Relative path | ✅ WORKS |

### ⚠️ 1 File That Partially Works

| # | File Name | Actual Location | Expected Path | Issue | Status |
|---|-----------|-----------------|----------------|-------|--------|
| 5 | `suicidality_protocol.json` | `src/emotional_os/core/` | `emotional_os/core/` | Path mismatch | ⚠️ PARTIAL |

### ❌ 6 Files That Don't Work

| # | File Name | Actual Location | Expected Path | Issue | Status |
|---|-----------|-----------------|----------------|-------|--------|
| 6 | `glyph_lexicon_rows.json` | `data/` | `emotional_os/glyphs/` | Missing dir | ❌ BROKEN |
| 7 | `glyph_lexicon_rows.csv` | `data/` | `emotional_os/glyphs/` | Missing dir | ❌ BROKEN |
| 8 | `word_centric_emotional_lexicon_expanded.json` | `data/` | `emotional_os/lexicon/` | Missing dir | ❌ BROKEN |
| 9 | `antonym_glyphs_indexed.json` | `data/` | `emotional_os/glyphs/` | Missing dir | ❌ BROKEN |
| 10 | `runtime_fallback_lexicon.json` | `src/emotional_os_parser/` | `emotional_os/parser/` | Missing dir | ❌ BROKEN |
| 11 | `glyphs.db` | (Runtime created) | `emotional_os/glyphs/` | Inconsistent | ⚠️ INCONSISTENT |

---

## DETAILED BREAKDOWN

### FILE 1: NRC Emotion Lexicon ✅

**Name:** `nrc_emotion_lexicon.txt`  
**Format:** TSV (tab-separated values)  
**Current Location:** `d:\saoriverse-console\data\lexicons\nrc_emotion_lexicon.txt`  
**Code Expects:** Multiple paths (via fallback search)  
**Searched Paths:**
1. `data/lexicons/nrc_emotion_lexicon.txt` ← **FOUND FIRST** ✅
2. `data/lexicons/nrc_lexicon_cleaned.json`
3. `emotional_os/lexicon/nrc_emotion_lexicon.txt`
4. `src/../../../data/lexicons/nrc_emotion_lexicon.txt`
5. `src/../../../data/lexicons/nrc_lexicon_cleaned.json`

**Loader:** `src/parser/nrc_lexicon_loader.py` (lines 16-22)  
**Status:** ✅ **WORKS** - First search path matches actual location  
**Action Needed:** None

---

### FILE 2: Glyph Lexicon (JSON) ❌

**Name:** `glyph_lexicon_rows.json`  
**Format:** JSON (array of glyph objects)  
**Current Locations:** 
- `d:\saoriverse-console\data\glyph_lexicon_rows.json`
- `d:\saoriverse-console\src\emotional_os_glyphs\glyph_lexicon_rows.json` (copy)

**Code Expects:** `emotional_os/glyphs/glyph_lexicon_rows.json` (hardcoded)  
**Used By:** 
- `src/emotional_os_glyphs/glyph_factorial_engine.py` (line 74)
- `src/emotional_os_glyphs/antonym_glyphs_indexer.py` (line 27)
- `src/emotional_os_glyphs/advanced_pruning_engine.py` (line 89)

**Status:** ❌ **BROKEN** - Expected directory doesn't exist  
**Action Needed:** 
1. Create `emotional_os/glyphs/` directory
2. Copy file there: `cp data/glyph_lexicon_rows.json emotional_os/glyphs/`

**Impact:** Without this, glyph generation system completely fails

---

### FILE 3: Glyph Lexicon (CSV) ❌

**Name:** `glyph_lexicon_rows.csv`  
**Format:** CSV (comma-separated values)  
**Current Locations:**
- `d:\saoriverse-console\data\glyph_lexicon_rows.csv`
- `d:\saoriverse-console\src\emotional_os_glyphs\glyph_lexicon_rows.csv` (copy)

**Code Expects:** `emotional_os/glyphs/glyph_lexicon_rows.csv` (hardcoded default)  
**Used By:** `src/emotional_os_glyphs/glyph_factorial_engine.py` (line 73) - fallback if JSON unavailable  
**Status:** ❌ **BROKEN** - Same issue as JSON  
**Action Needed:**
1. Copy file: `cp data/glyph_lexicon_rows.csv emotional_os/glyphs/`

---

### FILE 4: Suicidality Protocol ⚠️

**Name:** `suicidality_protocol.json`  
**Format:** JSON (configuration object)  
**Current Location:** `d:\saoriverse-console\src\emotional_os\core\suicidality_protocol.json`  
**Code Expects:** `emotional_os/core/suicidality_protocol.json` (hardcoded default)  
**Loader:** `src/emotional_os/core/suicidality_handler.py` (line 33)  
**Status:** ⚠️ **PARTIAL** 
- Works if running from `src/` directory
- Breaks if running from repo root
- Path mismatch causes inconsistency

**Action Needed:**
1. Copy file: `cp src/emotional_os/core/suicidality_protocol.json emotional_os/core/`
2. OR refactor code to use dynamic path resolution

**Impact:** Crisis handling won't activate

---

### FILE 5: Signal Lexicon ✅

**Name:** `signal_lexicon.json`  
**Format:** JSON (signal definitions)  
**Current Location:** `d:\saoriverse-console\src\emotional_os_parser\signal_lexicon.json`  
**Code Expects:** Multiple paths via PathManager  
**Used By:**
- `src/emotional_os_learning/hybrid_learner_v2.py` (line 62)
- Tests and scripts

**Status:** ✅ **WORKS** - PathManager handles path resolution  
**Action Needed:** None

---

### FILE 6: Word-Centric Lexicon ❌

**Name:** `word_centric_emotional_lexicon_expanded.json`  
**Format:** JSON (word -> emotion mapping)  
**Current Locations:**
- `d:\saoriverse-console\data\word_centric_emotional_lexicon_expanded.json`
- `d:\saoriverse-console\src\emotional_os_lexicon\word_centric_emotional_lexicon_expanded.json`

**Code Expects:** `emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json` (hardcoded)  
**Loader:** `src/emotional_os_lexicon/lexicon_loader.py` (line 18)  
**Status:** ❌ **BROKEN** - Expected directory doesn't exist  
**Action Needed:**
1. Create `emotional_os/lexicon/` directory
2. Copy file: `cp data/word_centric_emotional_lexicon_expanded.json emotional_os/lexicon/`

---

### FILE 7: Learned Lexicon ✅

**Name:** `learned_lexicon.json`  
**Format:** JSON (learned patterns, gets updated at runtime)  
**Current Location:** `d:\saoriverse-console\src\emotional_os_parser\learned_lexicon.json` (template)  
**Code Expects:** Multiple paths via PathManager
- `parser/learned_lexicon.json`
- `data/lexicons/learned_lexicon.json`
- `emotional_os/parser/learned_lexicon.json`

**Status:** ✅ **WORKS** - PathManager finds it  
**Action Needed:** None

---

### FILE 8: Runtime Fallback Lexicon ❌

**Name:** `runtime_fallback_lexicon.json`  
**Format:** JSON (fallback patterns)  
**Current Location:** `d:\saoriverse-console\src\emotional_os_parser\runtime_fallback_lexicon.json`  
**Code Expects:** `emotional_os/parser/runtime_fallback_lexicon.json` (hardcoded)  
**Used By:** `scripts/data/clean_and_salvage_glyphs.py` (line 22)  
**Status:** ❌ **BROKEN** - Expected directory doesn't exist  
**Action Needed:**
1. Create `emotional_os/parser/` directory
2. Copy file: `cp src/emotional_os_parser/runtime_fallback_lexicon.json emotional_os/parser/`

---

### FILE 9: Trauma Lexicon ✅

**Name:** `trauma_lexicon.json`  
**Format:** JSON (trauma/crisis keywords)  
**Current Location:** `d:\saoriverse-console\src\emotional_os_safety\trauma_lexicon.json`  
**Code Expects:** Relative path from module location  
**Loaders:** 
- `src/emotional_os_safety/sanctuary.py` (line 13)
- `src/emotional_os_safety/sanctuary_handler.py` (line 9)

**Status:** ✅ **WORKS** - Uses relative path from module  
**Action Needed:** None

---

### FILE 10: Antonym Glyphs Index ❌

**Name:** `antonym_glyphs_indexed.json`  
**Format:** JSON (opposite emotion mappings)  
**Current Locations:**
- `d:\saoriverse-console\data\antonym_glyphs_indexed.json`
- `d:\saoriverse-console\src\emotional_os_glyphs\antonym_glyphs_indexed.json` (copy)

**Code Expects:** `emotional_os/glyphs/antonym_glyphs_indexed.json` (hardcoded)  
**Used By:** `src/emotional_os_glyphs/antonym_glyphs_indexer.py` (line 27)  
**Status:** ❌ **BROKEN** - Expected directory doesn't exist  
**Action Needed:**
1. Copy file: `cp data/antonym_glyphs_indexed.json emotional_os/glyphs/`

---

### FILE 11: Glyphs Database (SQLite) ⚠️

**Name:** `glyphs.db`  
**Format:** SQLite database  
**Current Location:** Created at runtime (doesn't exist initially)  
**Code Expects:** Inconsistent expectations
- PathManager searches: `glyphs.db`, `data/glyphs.db`
- Hardcoded in modules: `emotional_os/glyphs/glyphs.db`

**Status:** ⚠️ **INCONSISTENT** - Multiple paths used  
**Action Needed:**
1. Standardize to: `emotional_os/glyphs/glyphs.db`
2. Create directory before first run

---

## AFFECTED MODULES SUMMARY

### Critical (Won't Start)
- **Glyph Factorial Engine** - Can't load glyphs
- **Advanced Pruning Engine** - Can't prune glyphs
- **Word-Centric Lexicon** - Can't map words to emotions

### Important (Partial Failure)
- **Antonym Glyphs Indexer** - Can't find opposite emotions
- **Suicidality Handler** - Crisis protocol inconsistent

### Working Fine
- **NRC Lexicon Loader** - Finds file via search
- **Signal Parser** - Uses PathManager
- **Learning System** - Uses PathManager
- **Safety/Sanctuary** - Uses relative paths

---

## DIRECTORY STRUCTURE FIXES NEEDED

```
Create: emotional_os/
  Create: emotional_os/glyphs/
    Copy: data/glyph_lexicon_rows.json
    Copy: data/glyph_lexicon_rows.csv
    Copy: data/antonym_glyphs_indexed.json
  Create: emotional_os/core/
    Copy: src/emotional_os/core/suicidality_protocol.json
  Create: emotional_os/lexicon/
    Copy: data/word_centric_emotional_lexicon_expanded.json
  Create: emotional_os/parser/
    Copy: src/emotional_os_parser/runtime_fallback_lexicon.json
```

---

## IMPLEMENTATION CHECKLIST

### Pre-Startup
- [ ] Create `emotional_os/` directory structure
- [ ] Copy all 9 critical data files
- [ ] Run verification script
- [ ] Check that all files exist

### Startup
- [ ] Run app from repo root (not from `src/`)
- [ ] Monitor for file-not-found errors
- [ ] Verify glyph system loads
- [ ] Verify suicidality protocol activates

### Post-Startup
- [ ] Check logs for any path warnings
- [ ] Verify all features work
- [ ] Test crisis handling
- [ ] Test word lexicon

---

## FILE SIZES

| File | Size | Location |
|------|------|----------|
| `glyph_lexicon_rows.json` | ~1.5 MB | `data/` |
| `glyph_lexicon_rows.csv` | ~0.8 MB | `data/` |
| `word_centric_emotional_lexicon_expanded.json` | ~2.5 MB | `data/` |
| `nrc_emotion_lexicon.txt` | ~0.6 MB | `data/lexicons/` |
| `antonym_glyphs_indexed.json` | ~0.4 MB | `data/` |
| `signal_lexicon.json` | ~15 KB | `src/emotional_os_parser/` |
| `suicidality_protocol.json` | ~5 KB | `src/emotional_os/core/` |
| `trauma_lexicon.json` | ~3 KB | `src/emotional_os_safety/` |
| `runtime_fallback_lexicon.json` | ~10 KB | `src/emotional_os_parser/` |
| `learned_lexicon.json` | ~5 KB | `src/emotional_os_parser/` |

**Total Size of Critical Files:** ~5.8 MB

---

## ESTIMATED TIME TO FIX

| Option | Time | Effort | Code Changes |
|--------|------|--------|--------------|
| A: Create Directory | 5 min | Low | None |
| B: Update Code Paths | 30 min | Medium | ~5 files |
| C: Use PathManager | 1-2 hrs | High | ~10 files |

---

## RECOMMENDED NEXT STEPS

1. **Immediate (Now):** 
   - Run 5-minute fix (Option A)
   - Verify files exist
   - Test app startup

2. **Short-term (Today):**
   - Read `CODE_LOCATIONS_NEEDING_FIXES.md`
   - Understand impact of each file
   - Plan permanent solution

3. **Medium-term (This Week):**
   - Implement Option B or C
   - Clean up duplicate files
   - Update documentation

4. **Long-term (This Month):**
   - Centralize all path management
   - Remove all hardcoded paths
   - Implement comprehensive testing

---

**Document Complete:** All 11 files analyzed and mapped  
**Confidence Level:** Very High (based on comprehensive code review)  
**Ready to Implement:** Yes

