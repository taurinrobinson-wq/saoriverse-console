# Glyph System Architecture & Current Status

**Date:** November 12, 2025
**Status:** ✅ Database Updated | ⚠️ Backend Configuration Needed

##

## 🔴 Current Issues Resolved

### 1. **"Technical Difficulties" Error**

**Root Cause:** The `CURRENT_SAORI_URL` environment variable is not configured in your `.env` file

**Location:** `/workspaces/saoriverse-console/emotional_os/deploy/fastapi_app.py` (lines 88-89)

**Error Flow:**

```
User sends message → UI calls run_hybrid_pipeline() →
Tries to POST to saori_url → saori_url is None →
API returns 200+ status code →
Returns: "I'm experiencing some technical difficulties, but I'm still here for you."
```


**Solution:** Add to your `.env` file:

```bash
CURRENT_SAORI_URL=https://your-supabase-project.supabase.co/functions/v1/saori-fixed
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```


##

## ✅ Database Update Complete

### Glyph Lexicon Database

- **Location:** `/workspaces/saoriverse-console/emotional_os/glyphs/glyphs.db`
- **Table:** `glyph_lexicon`
- **Previous Count:** 159 glyphs
- **New Count:** **6,434 glyphs** ✅
- **Source:** `glyph_lexicon_rows_validated.json` (129,693 lines)

### Gate Distribution

```
Gate 2:    22 glyphs (Containment)
Gate 3:  2,682 glyphs (Recognition/Awareness)
Gate 4:     5 glyphs (Longing/Ache)
Gate 5:    16 glyphs (Joy/Yearning)
Gate 6:    17 glyphs (Devotion)
Gate 7:  3,494 glyphs (Collapse/Transformation)
Gate 8:   174 glyphs (Boundary/Shielding)
Gate 9:    23 glyphs (Stillness)
Gate 10:    1 glyph (Surrender)
```


##

## 📊 How Glyphs Generate Responses

### Response Generation Pipeline

```
User Input
    ↓
emotional_os/core/signal_parser.py (parse_input())
    ├─ Load signal lexicon (JSON)
    ├─ Parse signals (3-phase: exact → NRC → fuzzy)
    ├─ Evaluate gates
    └─ Fetch glyphs from glyphs.db
    ↓
SELECT * FROM glyph_lexicon WHERE gate IN (...)
    ↓
[FOUND GLYPHS]
    ├─ select_best_glyph_and_response()
    └─ generate_contextual_response()
        ↓
    emotional_os/glyphs/dynamic_response_composer.py
      ├─ _build_glyph_aware_response()
      ├─ Use glyph.description as anchor
      ├─ Use glyph.gates / activation_signals for intensity (intensity ~= gate count)
      ├─ Support multi-glyph composition via `compose_multi_glyph_response()` (default `top_n=5`)
      └─ Map glyph name to poetry category
    ↓
[NO GLYPHS FOUND]
    ↓
emotional_os/glyphs/glyph_learner.py
    ├─ analyze_input_for_glyph_generation()
    ├─ Generate candidate glyph
    └─ Log to glyph_candidates table
    ↓
emotional_os/glyphs/learning_response_generator.py
    ├─ generate_learning_response()
    ├─ Select response template by emotional tone
    ├─ Insert key emotional terms
    └─ Add validation prompt
    ↓
Response delivered to user
```


## 🟢 Recent Local-only Integration (Nov 16, 2025)

- The UI and main entry now enforce a local-first, local-only processing model by default. Remote/hybrid AI is disabled in the standard app flow; any remote calls are optional and have robust fallbacks.
- When remote AI is unavailable or configured off, `run_hybrid_pipeline()` will now prefer a locally-composed reply using:
  - `emotional_os/glyphs/dynamic_response_composer.py:DynamicResponseComposer.compose_multi_glyph_response()`
  - Default behavior: combine the top-N glyphs (default `top_n=5`) and produce a single layered response that reflects relative intensities and gates.
- Intensity heuristic: the composer uses gate count and `activation_signals` as a proxy for glyph intensity/voltage. If your glyphs include an explicit numeric `voltage` field, the composer can be tuned to use that instead.
- Deduplication & staging: candidate glyphs are checked against an existing lexicon and `relational_memory` (when available). Near-duplicates are staged to `learning/near_duplicate_staging.jsonl` (append-only) and the emitted candidate includes `dedup` and `dedup_reason` metadata.
- Main app docstring now documents the full startup → auth → opt-in persistence → parse → response flow. See `main_v2.py` for the succinct runtime summary.

Use this document as the canonical reference for the response flow while you continue improving the
system. If you update selection heuristics (weights, `top_n`, or intensity calculations), update
this file so the team's expectations stay aligned.

##

## 🗂️ Key Files That Generate Responses

### 1. **Signal Parser** (Entry Point)

- **File:** `emotional_os/core/signal_parser.py`
- **Function:** `parse_input(input_text, lexicon_path, db_path='glyphs.db', ...)`
- **What it does:**
  - Loads signal lexicon
  - Parses emotional signals
  - Maps signals to ECM gates
  - Queries glyphs.db
  - Returns best glyph + response

### 2. **Glyph Database** (Data Source)

- **File:** `emotional_os/glyphs/glyphs.db`
- **Table:** `glyph_lexicon`
- **Schema:**

  ```sql
  CREATE TABLE glyph_lexicon (
    id INTEGER PRIMARY KEY,
    voltage_pair TEXT,
    glyph_name TEXT,
    description TEXT,
    gate TEXT,
    activation_signals TEXT,
    display_name TEXT,
    response_template TEXT
  );
  ```

### 3. **Dynamic Response Composer** (Response Builder)

- **File:** `emotional_os/glyphs/dynamic_response_composer.py`
- **Class:** `DynamicResponseComposer`
- **Key Methods:**
  - `compose_response()` - Main entry point
  - `_build_glyph_aware_response()` - Uses glyph metadata
  - `_weave_poetry()` - Adds poetic elements

### 4. **Learning Response Generator** (Fallback)

- **File:** `emotional_os/glyphs/learning_response_generator.py`
- **Class:** `LearningResponseGenerator`
- **Key Methods:**
  - `generate_learning_response()` - When no glyph found
  - `generate_multi_glyph_response()` - Multiple matches
  - `craft_insufficient_glyph_response()` - Partial match

### 5. **Glyph Learner** (Learning System)

- **File:** `emotional_os/glyphs/glyph_learner.py`
- **Class:** `GlyphLearner`
- **What it does:**
  - Analyzes inputs when no glyph matches
  - Generates new candidate glyphs
  - Stores in `glyph_candidates` table
  - Learns from user interactions

##

## 🔄 Response Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Message                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │ signal_parser  │
                   │  parse_input() │
                   └────────┬───────┘
                            │
        ┌───────────────────┴────────────────────┐
        │                                        │
        ▼                                        ▼
┌───────────────┐                        ┌──────────────┐
│ Parse Signals │                        │ Fetch Glyphs │
│   - Exact     │                        │ from glyphs  │
│   - NRC       │                        │    .db       │
│   - Fuzzy     │                        └──────┬───────┘
└───────┬───────┘                               │
        │                                       │
        ▼                                       ▼
┌───────────────┐                     ┌──────────────────┐
│ Evaluate Gates│                     │  Glyphs Found?   │
└───────┬───────┘                     └────────┬─────────┘
        │                                      │
        └──────────────────┬───────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼ YES                                 ▼ NO
┌────────────────────┐            ┌─────────────────────┐
│ select_best_glyph  │            │   glyph_learner     │
│   _and_response()  │            │ analyze_input_for   │
└─────────┬──────────┘            │ _glyph_generation() │
          │                       └──────────┬──────────┘
          ▼                                  │
┌────────────────────┐                      ▼
│ dynamic_response   │            ┌─────────────────────┐
│    _composer       │            │ learning_response   │
│ compose_response() │            │    _generator       │
└─────────┬──────────┘            │ generate_learning   │
          │                       │    _response()      │
          │                       └──────────┬──────────┘
          │                                  │
          └──────────────┬───────────────────┘
                         │
                         ▼
              ┌────────────────────┐
              │  Response to User  │
              └────────────────────┘
```


##

## 🛠️ Configuration Requirements

### Environment Variables (.env file)

```bash

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here

# Saori Function URL (AI Backend)
CURRENT_SAORI_URL=https://your-project.supabase.co/functions/v1/saori-fixed

# Alternative naming (supported)
SUPABASE_KEY=your_anon_key_here
SUPABASE_FUNCTION_URL=https://your-project.supabase.co/functions/v1/saori-fixed
```


### Processing Modes

1. **Hybrid Mode** (default)
   - Local signal parsing
   - Remote AI enhancement via SAORI function
   - Requires CURRENT_SAORI_URL configured

2. **Local Mode** (fallback)
   - All processing happens locally
   - No external API calls
   - Works without SAORI configuration

##

## 📁 Database Tables

### Core Tables

1. **glyph_lexicon** - Production glyphs (6,434 glyphs) 2. **glyph_candidates** - Learning pipeline
candidates 3. **glyph_versions** - Track glyph evolution 4. **glyph_usage_log** - Track usage across
users 5. **user_glyph_preferences** - Per-user glyph adoption 6. **glyph_consensus** - Shared
learning consensus 7. **emotional_territory** - Coverage gap analysis

### Supporting Tables

- **consolidation_map** - Duplicate tracking
- **glyph_lexicon_archived** - Historical glyphs
- **trace_log** - System telemetry

##

## 🔍 Quick Diagnostics

### Check Database Status

```python
import sqlite3
conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM glyph_lexicon")
count = cursor.fetchone()[0]
print(f"Total glyphs: {count}")
conn.close()
```


### Test Signal Parser

```python
from emotional_os.core.signal_parser import parse_input

result = parse_input(
    "I feel caught between who I am and who I pretend to be",
    "emotional_os/parser/signal_lexicon.json",
    db_path="emotional_os/glyphs/glyphs.db"
)

print(f"Best glyph: {result['best_glyph']}")
print(f"Response: {result['voltage_response'][:100]}...")
```


##

## 📝 Summary

✅ **Database Updated:** 6,434 glyphs now loaded ⚠️ **Action Required:** Configure
`CURRENT_SAORI_URL` in `.env` 📊 **Response System:** Multi-layered with learning capabilities 🔄
**Flow:** signal_parser → glyphs.db → response composers

The system is now ready to provide rich emotional responses once the backend API is configured.
