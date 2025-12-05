# ✅ Data Files Checklist & Quick Reference

**Purpose:** Quick checklist to verify all startup files are in place before running the app.

---

## 🚀 Pre-Startup Verification

### Step 1: Check Core Data Files

```bash
# NRC Emotion Lexicon
[ -f "data/lexicons/nrc_emotion_lexicon.txt" ] && echo "✅ NRC Lexicon" || echo "❌ MISSING: data/lexicons/nrc_emotion_lexicon.txt"

# Glyph Lexicons (JSON)
[ -f "data/glyph_lexicon_rows.json" ] && echo "✅ Glyph JSON (data/)" || echo "❌ MISSING: data/glyph_lexicon_rows.json"

# Glyph Lexicons (CSV)
[ -f "data/glyph_lexicon_rows.csv" ] && echo "✅ Glyph CSV (data/)" || echo "❌ MISSING: data/glyph_lexicon_rows.csv"

# Word Lexicon
[ -f "data/word_centric_emotional_lexicon_expanded.json" ] && echo "✅ Word Lexicon (data/)" || echo "❌ MISSING: data/word_centric_emotional_lexicon_expanded.json"

# Antonym Index
[ -f "data/antonym_glyphs_indexed.json" ] && echo "✅ Antonym Index (data/)" || echo "❌ MISSING: data/antonym_glyphs_indexed.json"
```

### Step 2: Check Config Files

```bash
# Suicidality Protocol
[ -f "src/emotional_os/core/suicidality_protocol.json" ] && echo "✅ Suicidality Protocol" || echo "❌ MISSING: src/emotional_os/core/suicidality_protocol.json"

# Signal Lexicon
[ -f "src/emotional_os_parser/signal_lexicon.json" ] && echo "✅ Signal Lexicon" || echo "❌ MISSING: src/emotional_os_parser/signal_lexicon.json"

# Trauma Lexicon
[ -f "src/emotional_os_safety/trauma_lexicon.json" ] && echo "✅ Trauma Lexicon" || echo "❌ MISSING: src/emotional_os_safety/trauma_lexicon.json"
```

### Step 3: Apply Quick Fix (if needed)

If any files are missing from their expected locations, run the quick fix:

```bash
# Create expected directory structure
mkdir -p emotional_os/glyphs
mkdir -p emotional_os/core
mkdir -p emotional_os/lexicon
mkdir -p emotional_os/parser
mkdir -p emotional_os/safety

# Copy glyph files
cp data/glyph_lexicon_rows.json emotional_os/glyphs/ 2>/dev/null || echo "Note: glyph JSON not copied"
cp data/glyph_lexicon_rows.csv emotional_os/glyphs/ 2>/dev/null || echo "Note: glyph CSV not copied"
cp data/antonym_glyphs_indexed.json emotional_os/glyphs/ 2>/dev/null || echo "Note: antonym index not copied"

# Copy config files
cp src/emotional_os_lexicon/word_centric_emotional_lexicon_expanded.json emotional_os/lexicon/ 2>/dev/null || echo "Note: word lexicon not copied"
cp src/emotional_os/core/suicidality_protocol.json emotional_os/core/ 2>/dev/null || echo "Note: protocol config not copied"
cp src/emotional_os_parser/signal_lexicon.json emotional_os/parser/ 2>/dev/null || echo "Note: signal lexicon not copied"
cp src/emotional_os_parser/runtime_fallback_lexicon.json emotional_os/parser/ 2>/dev/null || echo "Note: fallback lexicon not copied"

# Verify
echo ""
echo "Verification after quick fix:"
ls -la emotional_os/glyphs/ 2>/dev/null | grep -E "\.json|\.csv" || echo "emotional_os/glyphs/ - needs files"
ls -la emotional_os/core/ 2>/dev/null || echo "emotional_os/core/ - needs creation"
ls -la emotional_os/lexicon/ 2>/dev/null | grep -E "\.json" || echo "emotional_os/lexicon/ - needs files"
```

---

## 📋 File Status Summary Table

| File | Location | Status | Used By |
|------|----------|--------|---------|
| `nrc_emotion_lexicon.txt` | `data/lexicons/` | ✅ Found | NRC Lexicon Loader |
| `glyph_lexicon_rows.json` | `data/` | ⚠️ Need to copy | Glyph Factorial, Pruning Engine |
| `glyph_lexicon_rows.csv` | `data/` | ⚠️ Need to copy | Glyph Factorial, Pruning Engine |
| `suicidality_protocol.json` | `src/emotional_os/core/` | ⚠️ Need to copy | Suicidality Handler |
| `signal_lexicon.json` | `src/emotional_os_parser/` | ✅ Found | Parser, Learning |
| `trauma_lexicon.json` | `src/emotional_os_safety/` | ✅ Found | Safety, Sanctuary |
| `word_centric_emotional_lexicon_expanded.json` | `data/` | ⚠️ Need to copy | Lexicon Loader |
| `antonym_glyphs_indexed.json` | `data/` | ⚠️ Need to copy | Antonym Indexer |
| `learned_lexicon.json` | `src/emotional_os_parser/` | ✅ Created at runtime | Learning |
| `runtime_fallback_lexicon.json` | `src/emotional_os_parser/` | ✅ Found | Data scripts |

---

## 🔧 Minimal Fix (5 minutes)

```bash
# Just run this from repo root:
mkdir -p emotional_os/{glyphs,core,lexicon,parser,safety}
cp data/glyph_lexicon_rows.* emotional_os/glyphs/
cp data/antonym_glyphs_indexed.json emotional_os/glyphs/
cp data/word_centric_emotional_lexicon_expanded.json emotional_os/lexicon/
cp src/emotional_os/core/suicidality_protocol.json emotional_os/core/
cp src/emotional_os_parser/signal_lexicon.json emotional_os/parser/ 2>/dev/null
cp src/emotional_os_parser/runtime_fallback_lexicon.json emotional_os/parser/ 2>/dev/null
```

---

## 🎯 File Location Reference

### MUST EXIST (Critical Startup)

**For Glyph System:**
- `emotional_os/glyphs/glyph_lexicon_rows.json`
- `emotional_os/glyphs/glyph_lexicon_rows.csv`
- `emotional_os/glyphs/antonym_glyphs_indexed.json`

**For Config:**
- `emotional_os/core/suicidality_protocol.json`
- `emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json`

**For Data:**
- `data/lexicons/nrc_emotion_lexicon.txt`

---

### AUTOMATICALLY FOUND (Already Work)

**Via Relative Path:**
- `src/emotional_os_safety/trauma_lexicon.json`

**Via PathManager:**
- `src/emotional_os_parser/signal_lexicon.json`
- `src/emotional_os_parser/learned_lexicon.json`
- `src/emotional_os_parser/runtime_fallback_lexicon.json`

---

## 🐛 Troubleshooting

### "FileNotFoundError: glyph_lexicon_rows.json"
**Solution:** Run quick fix above to copy files to `emotional_os/glyphs/`

### "FileNotFoundError: suicidality_protocol.json"
**Solution:** Copy from `src/emotional_os/core/` to `emotional_os/core/`

### "FileNotFoundError: word_centric_emotional_lexicon_expanded.json"
**Solution:** Copy from `data/` to `emotional_os/lexicon/`

### "Module not found: emotional_os"
**Solution:** Make sure you're running from repo root, not from `src/` directory

### App starts but no glyphs load
**Solution:** Verify files in `emotional_os/glyphs/` exist and aren't empty

---

## 📊 Quick Status Check

```python
# Run this Python script to check all files:

from pathlib import Path

checks = {
    "✅ Working": [
        ("NRC Lexicon", "data/lexicons/nrc_emotion_lexicon.txt"),
        ("Signal Lexicon", "src/emotional_os_parser/signal_lexicon.json"),
        ("Trauma Lexicon", "src/emotional_os_safety/trauma_lexicon.json"),
    ],
    "❌ Needs Fix": [
        ("Glyph JSON", "data/glyph_lexicon_rows.json", "→ emotional_os/glyphs/"),
        ("Glyph CSV", "data/glyph_lexicon_rows.csv", "→ emotional_os/glyphs/"),
        ("Protocol", "src/emotional_os/core/suicidality_protocol.json", "→ emotional_os/core/"),
        ("Word Lexicon", "data/word_centric_emotional_lexicon_expanded.json", "→ emotional_os/lexicon/"),
        ("Antonym Index", "data/antonym_glyphs_indexed.json", "→ emotional_os/glyphs/"),
    ],
}

print("\n✅ FILES THAT WORK:")
for name, path in checks["✅ Working"]:
    exists = "✅" if Path(path).exists() else "⚠️ Missing"
    print(f"  {exists} {name}")

print("\n❌ FILES NEEDING ATTENTION:")
for item in checks["❌ Needs Fix"]:
    if len(item) == 2:
        name, path = item
        dest = "needs check"
    else:
        name, path, dest = item
    exists = "✅" if Path(path).exists() else "❌ Missing"
    print(f"  {exists} {name} {dest if '→' in str(dest) else ''}")
```

---

## 🚀 One-Line Quick Fix

```bash
mkdir -p emotional_os/{glyphs,core,lexicon} && cp data/glyph_lexicon_rows.* emotional_os/glyphs/ && cp data/antonym_glyphs_indexed.json emotional_os/glyphs/ && cp data/word_centric_emotional_lexicon_expanded.json emotional_os/lexicon/ && cp src/emotional_os/core/suicidality_protocol.json emotional_os/core/
```

---

## 📚 For More Information

- **DATA_FILES_AND_STARTUP_PATHS_AUDIT.md** - Complete analysis of every file
- **QUICK_REFERENCE_DATA_PATHS.md** - Reference table with diagnostic tools
- **CODE_LOCATIONS_NEEDING_FIXES.md** - Exact code locations that load files
- **DATA_FILES_STARTUP_AUDIT_SUMMARY.md** - Executive summary

---

## ✨ Status After Quick Fix

If you run the quick fix above and all checks pass:

✅ Glyph system will load  
✅ Suicidality protocol will activate  
✅ Word lexicon will work  
✅ Antonym system will function  
✅ App should start successfully

