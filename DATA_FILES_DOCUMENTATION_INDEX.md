# 📑 Data Files & Startup Paths - Complete Documentation Index

**Generated:** December 4, 2025  
**Purpose:** Comprehensive audit of all data/config files needed at startup

---

## 📚 Documentation Files Created

### 1. **DATA_FILES_STARTUP_AUDIT_SUMMARY.md** ⭐ START HERE
**Reading Time:** 5 minutes  
**Best For:** Quick understanding of the problem and solutions

**Contains:**
- Executive summary of issues
- List of files that will/won't load
- Impact of each issue
- 3 solution options with difficulty estimates
- Pre-startup verification checklist

**Key Section:** "The Problem in 30 Seconds" - read this first!

---

### 2. **DATA_FILES_CHECKLIST.md** ⭐ USE THIS
**Reading Time:** 2 minutes  
**Best For:** Quick pre-startup verification

**Contains:**
- Bash commands to check if files exist
- Quick fix one-liner
- Status summary table
- Troubleshooting guide
- Python verification script

**Use Case:** Before starting the app, run the checks to verify everything is ready

---

### 3. **DATA_FILES_AND_STARTUP_PATHS_AUDIT.md** 📋 REFERENCE
**Reading Time:** 15 minutes  
**Best For:** Detailed understanding of each file

**Contains:**
- Complete mapping of all 11 startup files
- Current location vs. expected location
- Where code tries to load from
- Why each file works or fails
- Directory structure issues
- Recommended corrections

**Use Case:** Understanding why a specific file fails to load

---

### 4. **QUICK_REFERENCE_DATA_PATHS.md** 🔍 QUICK LOOK
**Reading Time:** 5 minutes  
**Best For:** Quick reference while fixing issues

**Contains:**
- Summary table of all files
- Key issues at a glance
- Modules by load behavior (PathManager vs. hardcoded)
- Diagnostic Python script
- Configuration by module
- Startup order diagram

**Use Case:** Quick lookup while implementing fixes

---

### 5. **CODE_LOCATIONS_NEEDING_FIXES.md** 🛠️ FOR DEVELOPERS
**Reading Time:** 20 minutes  
**Best For:** Implementing code fixes

**Contains:**
- Every Python file that loads data
- Exact line numbers
- Current code vs. problem
- Suggested fix code
- Pattern to apply to all modules
- Using PathManager example

**Use Case:** Refactoring code to use correct paths or PathManager

---

## 🎯 Quick Navigation

### "I need to START THE APP NOW"
1. Read: **DATA_FILES_STARTUP_AUDIT_SUMMARY.md** (section: "The Problem in 30 Seconds")
2. Run: **DATA_FILES_CHECKLIST.md** (section: "Minimal Fix (5 minutes)")
3. Try: Start app

### "I want to understand what's wrong"
1. Read: **DATA_FILES_STARTUP_AUDIT_SUMMARY.md** (full)
2. Reference: **DATA_FILES_AND_STARTUP_PATHS_AUDIT.md** (sections 1-3)
3. Look up: **QUICK_REFERENCE_DATA_PATHS.md** (tables)

### "I need to fix the code"
1. Review: **CODE_LOCATIONS_NEEDING_FIXES.md** (full)
2. Reference: **CODE_LOCATIONS_NEEDING_FIXES.md** (section: "Pattern to Apply")
3. Implement: Suggested fixes

### "I'm debugging a specific file load error"
1. Check: **DATA_FILES_AND_STARTUP_PATHS_AUDIT.md** (find the file in tables)
2. Look up: **CODE_LOCATIONS_NEEDING_FIXES.md** (find the loading code)
3. Run: **DATA_FILES_CHECKLIST.md** (diagnostic scripts)

---

## 📊 Document Comparison

| Document | Audience | Time | Depth | Best Used |
|----------|----------|------|-------|-----------|
| Summary | Everyone | 5 min | Overview | Understanding problem |
| Checklist | Operators | 2 min | Quick | Before startup |
| Audit | Analysts | 15 min | Deep | Root cause analysis |
| Quick Ref | Developers | 5 min | Reference | During work |
| Code Locs | Developers | 20 min | Deep | Fixing code |

---

## 🔴 The Core Issue (2-Sentence Version)

Code expects files in `emotional_os/` directory at repo root, but they're actually in `data/` and `src/emotional_os_*/` directories. Without these files accessible at the expected paths, the app fails to load critical features.

---

## 🟡 Critical Files (Must Have)

| File | Current Location | Expected by Code | Fix |
|------|------------------|------------------|-----|
| `glyph_lexicon_rows.json` | `data/` | `emotional_os/glyphs/` | Copy file |
| `glyph_lexicon_rows.csv` | `data/` | `emotional_os/glyphs/` | Copy file |
| `suicidality_protocol.json` | `src/emotional_os/core/` | `emotional_os/core/` | Copy file |
| `word_centric_emotional_lexicon_expanded.json` | `data/` | `emotional_os/lexicon/` | Copy file |

---

## 🟢 Files That Work

| File | Location | Why |
|------|----------|-----|
| `nrc_emotion_lexicon.txt` | `data/lexicons/` | Uses fallback search |
| `trauma_lexicon.json` | `src/emotional_os_safety/` | Uses relative path |
| `signal_lexicon.json` | `src/emotional_os_parser/` | Uses PathManager |

---

## 🛠️ Three Fix Options

### Option A: Create Directory (⚡ 5 minutes)
```bash
mkdir -p emotional_os/{glyphs,core,lexicon}
cp data/glyph_lexicon_rows.* emotional_os/glyphs/
cp data/word_centric_emotional_lexicon_expanded.json emotional_os/lexicon/
cp src/emotional_os/core/suicidality_protocol.json emotional_os/core/
```

**Pros:** Instant, no code changes, works with existing code  
**Cons:** Duplicates files

---

### Option B: Update Code Paths (📝 30 minutes)
Refactor all hardcoded paths in Python files.

**Pros:** Clean solution, no duplicates  
**Cons:** Requires code changes in multiple files

**See:** `CODE_LOCATIONS_NEEDING_FIXES.md`

---

### Option C: Use PathManager (🏗️ 1-2 hours)
Refactor to centralize path management.

**Pros:** Most maintainable long-term  
**Cons:** Biggest effort

**See:** `CODE_LOCATIONS_NEEDING_FIXES.md` (section: "Using PathManager")

---

## 📋 Files Analyzed

**Total Files Examined:** 50+  
**Data Files Identified:** 11  
**Issues Found:** 6 critical, 3 high, 2 medium  
**Modules Affected:** 5 critical systems

### Modules Analyzed

✅ **Parser System** (`src/emotional_os_parser/`)
- NRC Lexicon Loader
- Signal Parser
- Hybrid Learner

✅ **Glyph System** (`src/emotional_os_glyphs/`)
- Glyph Factorial Engine
- Antonym Glyphs Indexer
- Advanced Pruning Engine

✅ **Safety System** (`src/emotional_os_safety/`)
- Sanctuary Handler
- Crisis Router

✅ **Learning System** (`src/emotional_os_learning/`)
- Hybrid Learner V2
- Lexicon Learner

✅ **Lexicon System** (`src/emotional_os_lexicon/`)
- Word-Centric Lexicon Loader

---

## 🚀 Recommended Reading Order

### For Quick Fix (5 minutes)
1. DATA_FILES_STARTUP_AUDIT_SUMMARY.md (first section)
2. DATA_FILES_CHECKLIST.md (Minimal Fix section)
3. Run the commands
4. Done!

### For Understanding (30 minutes)
1. DATA_FILES_STARTUP_AUDIT_SUMMARY.md (full)
2. QUICK_REFERENCE_DATA_PATHS.md (tables)
3. DATA_FILES_AND_STARTUP_PATHS_AUDIT.md (file details)
4. Done!

### For Implementation (2 hours)
1. DATA_FILES_STARTUP_AUDIT_SUMMARY.md (full)
2. CODE_LOCATIONS_NEEDING_FIXES.md (full)
3. Implement fixes in code
4. DATA_FILES_CHECKLIST.md (verification)
5. Done!

---

## 📞 FAQ

**Q: Can I start the app now?**  
A: Probably not fully. See "The Problem in 30 Seconds" in Summary.

**Q: Which fix should I do?**  
A: Option A (create directory) - fastest and works immediately.

**Q: Will this break anything?**  
A: No. Creating the directory and copying files won't break existing code.

**Q: How long does it take?**  
A: 5 minutes for Option A, 30 minutes for Option B, 1-2 hours for Option C.

**Q: What happens if I don't fix this?**  
A: Glyph system won't load, suicidality protocol won't activate, word lexicon won't work.

---

## 🎯 Success Criteria

After applying fixes, verify with:

```bash
# All these should exist:
ls -la emotional_os/glyphs/glyph_lexicon_rows.json
ls -la emotional_os/glyphs/glyph_lexicon_rows.csv  
ls -la emotional_os/core/suicidality_protocol.json
ls -la emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json
ls -la data/lexicons/nrc_emotion_lexicon.txt

# When all show files exist:
echo "✅ Ready to start app"
```

---

## 📝 Notes

- All documentation generated from comprehensive repo scan
- Based on code analysis of 50+ Python files
- Tested paths verified against actual file system
- Solutions provided with exact commands and code examples
- All recommendations are backward compatible

---

## 🔗 Related Documentation

- `README.md` - General project documentation
- `DEPLOYMENT_QUICK_REFERENCE.md` - Deployment instructions
- `LEARNING_QUICK_REFERENCE.md` - Learning system guide
- `SUICIDALITY_PROTOCOL_GUIDE.md` - Crisis handling reference

---

## 📄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-04 | Initial comprehensive audit |

---

**Last Updated:** December 4, 2025  
**Confidence Level:** High (based on code analysis)  
**Ready to Implement:** Yes

