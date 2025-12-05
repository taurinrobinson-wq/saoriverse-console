# 📊 Data Files & Startup - Visual Reference

---

## 🔴 CURRENT STATE: Files in Multiple Locations

```
┌─────────────────────────────────────────────────────────────────┐
│                  SAORIVERSE CONSOLE REPO                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐  ┌──────────┐  │
│  │   data/ (ACTUAL)   │  │   src/ (ACTUAL)    │  │ emotional_os/ │
│  │                    │  │                    │  │ (EXPECTED)    │
│  │ ✓ glyph_*.json     │  │ emotional_os/      │  │ DOESN'T EXIST │
│  │ ✓ glyph_*.csv      │  │ └─ core/           │  │               │
│  │ ✓ antonym_*.json   │  │    └─ suicidality  │  │ ✗ glyphs/     │
│  │ ✓ word_*.json      │  │                    │  │ ✗ core/       │
│  │ lexicons/          │  │ emotional_os_*/    │  │ ✗ lexicon/    │
│  │ └─ nrc_*.txt       │  │ ├─ glyphs/         │  │ ✗ parser/     │
│  │                    │  │ ├─ parser/         │  │ ✗ safety/     │
│  └────────────────────┘  │ ├─ lexicon/        │  │               │
│                          │ └─ safety/         │  └──────────────┘
│                          │    └─ trauma_*.json│
│                          │                    │
│                          └────────────────────┘
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🟢 AFTER QUICK FIX: All Files Where Code Expects Them

```
┌─────────────────────────────────────────────────────────────────┐
│                  SAORIVERSE CONSOLE REPO                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           emotional_os/ (CREATED)                        │   │
│  │                                                          │   │
│  │  ├─ core/                                               │   │
│  │  │  └─ ✅ suicidality_protocol.json (copied from src/)  │   │
│  │  │                                                       │   │
│  │  ├─ glyphs/                                             │   │
│  │  │  ├─ ✅ glyph_lexicon_rows.json (copied from data/)   │   │
│  │  │  ├─ ✅ glyph_lexicon_rows.csv (copied from data/)    │   │
│  │  │  └─ ✅ antonym_glyphs_indexed.json (copied)         │   │
│  │  │                                                       │   │
│  │  ├─ lexicon/                                            │   │
│  │  │  └─ ✅ word_centric_*.json (copied from data/)       │   │
│  │  │                                                       │   │
│  │  ├─ parser/                                             │   │
│  │  │  ├─ ✅ signal_lexicon.json (copied from src/)        │   │
│  │  │  └─ ✅ runtime_fallback_lexicon.json (copied)        │   │
│  │  │                                                       │   │
│  │  └─ safety/                                             │   │
│  │     └─ ✅ trauma_lexicon.json (copied from src/)        │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  RESULT: ✅ All critical files in expected locations            │
│          ✅ App can now load all modules                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 File Status Matrix

```
FILE NAME                              ACTUAL LOCATION      EXPECTED LOCATION       STATUS
──────────────────────────────────────────────────────────────────────────────────────────────
glyph_lexicon_rows.json               data/                emotional_os/glyphs/    ❌ BROKEN
glyph_lexicon_rows.csv                data/                emotional_os/glyphs/    ❌ BROKEN
antonym_glyphs_indexed.json           data/                emotional_os/glyphs/    ❌ BROKEN
word_centric_*.json                   data/                emotional_os/lexicon/   ❌ BROKEN
suicidality_protocol.json             src/emotional_os/    emotional_os/core/      ⚠️ PARTIAL
nrc_emotion_lexicon.txt               data/lexicons/       Via search              ✅ WORKS
signal_lexicon.json                   src/emotional_os_/   Via PathManager         ✅ WORKS
trauma_lexicon.json                   src/emotional_os_/   Relative path           ✅ WORKS
learned_lexicon.json                  src/emotional_os_/   Via PathManager         ✅ WORKS
runtime_fallback_lexicon.json         src/emotional_os_/   emotional_os/parser/    ❌ BROKEN
──────────────────────────────────────────────────────────────────────────────────────────────
```

---

## 🔄 Startup Sequence Diagram

```
START APP
  │
  ├─> Load NRC Lexicon (data/lexicons/nrc_emotion_lexicon.txt)
  │   └─> ✅ FOUND via search
  │
  ├─> Load Signal Lexicon (src/emotional_os_parser/signal_lexicon.json)
  │   └─> ✅ FOUND via PathManager
  │
  ├─> Load Glyph Lexicon (emotional_os/glyphs/glyph_lexicon_rows.json)
  │   └─> ❌ NOT FOUND - causes glyph system to fail
  │
  ├─> Load Suicidality Protocol (emotional_os/core/suicidality_protocol.json)
  │   └─> ⚠️ PARTIAL - works from src/ only
  │
  ├─> Load Word Lexicon (emotional_os/lexicon/word_centric_*.json)
  │   └─> ❌ NOT FOUND - causes lexicon system to fail
  │
  ├─> Load Antonym Index (emotional_os/glyphs/antonym_*.json)
  │   └─> ❌ NOT FOUND - causes antonym system to fail
  │
  └─> APP PARTIALLY INITIALIZED
      (some features work, others fail)
```

---

## 🎯 Impact of Missing Files

```
┌─────────────────────────────────────────────────────────────────┐
│  MISSING FILE: glyph_lexicon_rows.json                          │
├─────────────────────────────────────────────────────────────────┤
│  IMPACT: 🔴 CRITICAL                                            │
│  AFFECTED SYSTEMS:                                              │
│    • Glyph Factorial Engine - Can't generate glyphs             │
│    • Advanced Pruning Engine - Can't select responses           │
│    • All response generation - No emotional vocabulary          │
│  RESULT: System defaults to generic responses                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MISSING FILE: suicidality_protocol.json                        │
├─────────────────────────────────────────────────────────────────┤
│  IMPACT: 🟠 HIGH                                                │
│  AFFECTED SYSTEMS:                                              │
│    • Suicidality Handler - Crisis protocol disabled             │
│    • Crisis detection - Won't activate consent-based handling   │
│  RESULT: Crisis handling falls back to generic response         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MISSING FILE: word_centric_emotional_lexicon_expanded.json     │
├─────────────────────────────────────────────────────────────────┤
│  IMPACT: 🔴 CRITICAL                                            │
│  AFFECTED SYSTEMS:                                              │
│    • Word-Centric Lexicon - Word lookup fails                  │
│    • Emotional tagging - Can't identify emotional words        │
│  RESULT: Limited emotional understanding                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MISSING FILE: antonym_glyphs_indexed.json                      │
├─────────────────────────────────────────────────────────────────┤
│  IMPACT: 🟠 HIGH                                                │
│  AFFECTED SYSTEMS:                                              │
│    • Antonym Indexer - Can't find opposite emotions             │
│  RESULT: Opposite emotion expressions unavailable              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Quick Fix Process

```
START
  │
  ├─> Step 1: Create directories
  │   └─ mkdir -p emotional_os/{glyphs,core,lexicon,parser}
  │
  ├─> Step 2: Copy glyph files
  │   ├─ cp data/glyph_lexicon_rows.json → emotional_os/glyphs/
  │   ├─ cp data/glyph_lexicon_rows.csv → emotional_os/glyphs/
  │   └─ cp data/antonym_glyphs_indexed.json → emotional_os/glyphs/
  │
  ├─> Step 3: Copy config files
  │   ├─ cp src/.../suicidality_protocol.json → emotional_os/core/
  │   ├─ cp src/.../word_centric_*.json → emotional_os/lexicon/
  │   └─ cp src/.../signal_lexicon.json → emotional_os/parser/
  │
  ├─> Step 4: Verify
  │   └─ ls -la emotional_os/{glyphs,core,lexicon}/*
  │
  └─> DONE ✅
      All files in expected locations
      App should start successfully
```

---

## 📈 Fix Complexity vs. Time

```
COMPLEXITY

HIGH  │                                    ┌─ Option C: PathManager
      │                                    │ (Full refactor)
      │                                    │ 1-2 hours
      │
      │                      ┌─ Option B: Update Paths
      │                      │ (Code changes)
MEDIUM│                      │ 30 minutes
      │
      │  ┌─ Option A: Create Directory
LOW   │  │ (Quick fix)
      │  │ 5 minutes
      │
      └──┴──────────────────────────────────────────→ TIME

RECOMMENDED: Option A (Create Directory)
• Fastest solution
• No code changes needed
• Works immediately
• Can do Option B/C later for cleanup
```

---

## ✅ Verification Checklist

```
Before Startup:
  ├─ ✅ emotional_os/glyphs/glyph_lexicon_rows.json
  ├─ ✅ emotional_os/glyphs/glyph_lexicon_rows.csv
  ├─ ✅ emotional_os/glyphs/antonym_glyphs_indexed.json
  ├─ ✅ emotional_os/core/suicidality_protocol.json
  ├─ ✅ emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json
  ├─ ✅ data/lexicons/nrc_emotion_lexicon.txt
  └─ ✅ src/emotional_os_safety/trauma_lexicon.json

After Fix:
  └─ If all show ✅: Ready to start app!
```

---

## 🎯 Success Indicators

```
BEFORE FIX:
  • App starts but fails to load glyphs
  • Suicidality protocol not activating
  • Generic responses instead of emotional glyphs
  • No word-to-emotion mappings
  • Antonym system unavailable

AFTER FIX:
  • All data files load successfully ✅
  • Glyph system functional ✅
  • Suicidality protocol active ✅
  • Emotional responses working ✅
  • Word lexicon available ✅
  • Antonym system ready ✅
```

---

## 📋 File Dependency Map

```
glyph_lexicon_rows.json
├─ GlyphFactorialEngine
├─ AntonymGlyphsIndexer
└─ AdvancedPruningEngine

suicidality_protocol.json
└─ SuicidalityHandler
   └─ Crisis Response System

word_centric_emotional_lexicon_expanded.json
└─ WordCentricLexicon
   └─ Word Tagging System

nrc_emotion_lexicon.txt
└─ NRCLexicon
   └─ Baseline Emotions

signal_lexicon.json
├─ SignalParser
├─ HybridLearner
└─ Response Selection

trauma_lexicon.json
└─ SanctuaryHandler
   └─ Safety System
```

---

## 🚀 One-Command Fix

```bash
mkdir -p emotional_os/{glyphs,core,lexicon,parser,safety} && \
cp data/glyph_lexicon_rows.* emotional_os/glyphs/ 2>/dev/null && \
cp data/antonym_glyphs_indexed.json emotional_os/glyphs/ 2>/dev/null && \
cp data/word_centric_emotional_lexicon_expanded.json emotional_os/lexicon/ 2>/dev/null && \
cp src/emotional_os/core/suicidality_protocol.json emotional_os/core/ 2>/dev/null && \
cp src/emotional_os_parser/signal_lexicon.json emotional_os/parser/ 2>/dev/null && \
cp src/emotional_os_parser/runtime_fallback_lexicon.json emotional_os/parser/ 2>/dev/null && \
echo "✅ All files copied. Ready to start app!" || echo "⚠️ Some files may not have copied"
```

---

**Remember:** After running the one-command fix, verify that the emotional_os/ directory has all subdirectories with files!

