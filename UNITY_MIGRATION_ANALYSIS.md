# Velinor → Unity Migration: Complete Repository Inventory

**Analysis Date:** 2026-06-12  
**Repository:** saoriverse-console  
**Current Platform:** Streamlit (Python)  
**Target Platform:** Unity (C#)

---

## 📊 EXECUTIVE SUMMARY

The Velinor game consists of **~60 Python game files**, **118 glyphs**, **21+ NPCs**, **50+ background assets**, **25+ character sprites**, extensive JSON-based game data, and comprehensive design documentation. The game is organized into **4 major systems**: Emotional OS (TONE tracking), Glyph Cipher Engine, NPC Response System, and Story/Ending System.

**Estimated Portability:**
- **Directly Portable:** 40-50% (game data, glyph definitions, story scripts)
- **Needs Conversion:** 30-40% (Streamlit UI → Unity UI, asset formats)
- **Rewrite Required:** 20-30% (game loop, input handling, physics/rendering)

---

## 1. CURRENT GAME CODE

### 1.1 Core Game Systems

#### A. Game Mechanics & State Management
| File Path | Purpose | Lines | Type | Priority |
|-----------|---------|-------|------|----------|
| `velinor/engine/core.py` | Main game state machine | ~400 | Core Logic | **CRITICAL** |
| `velinor/engine/game_state.py` | GameState class, session persistence | ~300 | Data Model | **CRITICAL** |
| `velinor/engine/orchestrator.py` | Game loop orchestration | ~350 | Core Logic | **CRITICAL** |
| `velinor/game_mechanics/characters.py` | Character & ToneState classes | ~150 | Game Logic | **HIGH** |
| `velinor/engine/scene_manager.py` | Scene transitions & management | ~250 | Core Logic | **HIGH** |
| `velinor/engine/event_timeline.py` | Event sequencing system | ~200 | System | **HIGH** |

#### B. Emotional OS (TONE System)
| File Path | Purpose | Type | Details |
|-----------|---------|------|---------|
| `velinor/engine/trait_system.py` | TONE stat tracking (Empathy, Skepticism, Integration, Awareness) | System | ⚙️ Maps player choices to stat changes |
| `velinor/engine/coherence_calculator.py` | Coherence calculation (emotional harmony) | Algorithm | 📐 Determines NPC response depth |
| `velinor/engine/resonance.py` | Emotional resonance between player & NPCs | System | 🔗 Affects dialogue availability |
| `velinor/game_mechanics/characters.py` | ToneState dataclass (0-100 scale) | Data | 📊 Four-dimensional state space |

**Key Metrics:**
- 4 TONE dimensions tracked simultaneously
- Coherence = 100 - average_deviation(all TONE stats)
- Range: 0-100 for each stat
- Directly portable as data model

#### C. Glyph Cipher System
| File Path | Purpose | Type | Scale |
|-----------|---------|------|-------|
| `velinor/glyph_cipher_engine.py` | Core glyph unlock logic | **CRITICAL** | 118 glyphs total |
| `velinor/engine/npc_dialogue.py` | NPC-glyph interaction logic | System | Dialogue parsing |
| `velinor/velinor_api.py` | API for querying glyph data | Interface | Data access layer |

**Glyph System Details:**
- **118 Total Glyphs** across 7 emotional domains:
  - Collapse (13 glyphs)
  - Sovereignty (16 glyphs)
  - Ache (18 glyphs)
  - Presence (15 glyphs)
  - Joy (14 glyphs)
  - Trust (15 glyphs)
  - Legacy (14 glyphs)

**3-Tier Cipher Structure (PORTABLE):**
```
Layer 0: Poetic Fragment (always visible)
Layer 1: NPC Perspective (always visible)
Layer 2: Plaintext Truth (emotionally gated)
```

**Gate Requirements:**
- Emotional state must meet specific TONE thresholds
- Coherence level affects depth of unlock
- Presence in location required

#### D. NPC System
| File Path | Purpose | Type | Scale |
|-----------|---------|------|-------|
| `velinor/engine/npc_manager.py` | NPC state & behavior management | System | 21+ NPCs |
| `velinor/engine/npc_response_engine.py` | NPC dialogue generation | Logic | Dynamic responses |
| `velinor/engine/npc_encounter.py` | NPC encounter flow | Scene | Dialogue trees |
| `velinor/npc_profiles.py` | NPC data definitions | Data | Profile data |

**NPC Count & Types:**
- **Malrik** (Archivist) — Memory & Collapse
- **Elenya** (High Seer) — Joy, Trust, Sacred Presence
- **Veynar** (Captain) — Sovereignty, Authority
- **Dalen** (Guide) — Ache, Reckless Trial
- **Ravi** (Father) — Legacy, Loss
- **Nima** (Survivor) — Ache, Sorrow
- **Kaelen** (Thief) — Trust, Hidden Passages
- **Sera** (Herb Novice) — Joy, Presence, Care
- **Mariel** (Weaver) — Ache, Legacy, Binding
- **Tala** (Market Cook) — Joy, Shared Feast
- **Plus 11+ others** (Korrin, Sanor, Tariq, Tovren, Inodora, Dalen, etc.)

**NPC Data Portable Elements:**
- Personality profiles (JSON/YAML)
- Emotional gate thresholds
- Dialogue trees (story-based)
- NPC-specific glyph relationships

#### E. Story & Ending System
| File Path | Purpose | Type | Scale |
|-----------|---------|------|-------|
| `velinor/engine/ending_system.py` | 6 distinct endings logic | Core | 6 variations |
| `velinor/stories/story_definitions.py` | Story structure definitions | Data | Branching logic |
| `velinor/stories/build_story.py` | Story builder utility | Tool | Narrative construction |
| `velinor/engine/scene_manager.py` | Scene transitions | Logic | Flow control |

**Story Structure:**
- **6 Major Endings** determined by TONE trajectory
- **30+ Scenes/Locations** (marketplace, forest, swamp, desert, ruins, etc.)
- **Collapse Event** as pivotal narrative moment
- **Choice Consequences** tracked across sessions
- **Remnants System** (corrupted Corelink data) as thematic element

#### F. Dialogue & Interaction Systems
| File Path | Purpose | Type |
|-----------|---------|------|
| `velinor/engine/llm_dialogue.py` | Dynamic dialogue generation (currently LLM-based) | Logic |
| `velinor/engine/dialogue_context.py` | Dialogue context management | State |
| `velinor/engine/npc_response_engine.py` | NPC response selection logic | Algorithm |
| `velinor/engine/skill_system.py` | Skill checks & attribute system | Mechanics |

### 1.2 Streamlit UI Layer (REQUIRES REWRITE)
| File Path | Purpose | Impact |
|-----------|---------|--------|
| `velinor/streamlit_ui.py` | UI rendering components | 🔴 Completely rewrite for Unity |
| `velinor/streamlit_state.py` | Streamlit state management | 🔴 Replace with Unity state management |
| `app.py` | Streamlit entry point | 🔴 Replace with Unity main loop |

### 1.3 Asset Configuration
| File Path | Purpose | Type |
|-----------|---------|------|
| `velinor/engine/assets_config.py` | Asset path configuration | Config |
| `velinor/overlays/` | UI overlay images | Assets |

### 1.4 Testing & Validation
| File Path | Purpose | Type | Count |
|-----------|---------|------|-------|
| `velinor/engine/test_*.py` | Unit tests | Tests | 5+ files |
| `velinor/stories/test_*.py` | Story validation tests | Tests | 3+ files |

**Test Coverage Includes:**
- Story consistency validation
- Dialogue generation
- Remnants system
- Veynar-Kaelen dual arc
- Simulation testing

---

## 2. GRAPHICS ASSETS

### 2.1 Background Artwork (~45 files)
**Location:** `velinor/backgrounds/`

| Type | Count | Format | Aspect Ratios | Notes |
|------|-------|--------|----------------|-------|
| Environment Backgrounds | 45+ | PNG, JPG | 16:9, 4:3 | Multiple variants per location |

**Locations (Scene Backgrounds):**
- **Desert** (5 variants): desert.png, desert_16-9.JPG, desert_pass_16-9.JPG
- **Forest** (4 variants): forest.png, forest_16-9.JPG, forest_lake_city.JPG
- **Lake** (3 variants): lake.png, lake2.png, lake_bog.JPG
- **Market/City** (5 variants): city_market.png, market_ruins.JPG, rural_city.png
- **Swamp** (4 variants): swamp(16-9).png, swamp_dock.png
- **Boss Chamber**: boss_chamber01.png
- **Special Locations**: thieves_gang_lair.png, Tessa_house_interior.png
- **Title/Ending Screens**: Velinor_Ideal.png, Saori_Velinor_End_Reveal.png, velinor_title_eyes_closed.png

**Technical Details:**
- Mixed resolution (variable)
- PNG (transparency) and JPG (optimized)
- Multiple 16:9 variants for UI scaling
- Ready for Unity Sprite import

### 2.2 Character Sprites (~40 files)
**Location:** `velinor/npcs/`

| Character | Sprites | Variants | Format |
|-----------|---------|----------|--------|
| **Kaelen** | 4-5 | Normal, Trickster, Headshot | PNG |
| **Ravi** | 2 | Normal, Headshot, Pixel | PNG |
| **Nima** | 3 | Normal, Headshot, Pixel | PNG |
| **Saori** | 5 | Device left/right, Paper, Stick, Worried | PNG |
| **Tessa** | 4 | Young, Old (2 variants), Sad | PNG |
| **Veynar** | 3 | Sitting (3 views), Standing | PNG, AI |
| **Others** | 20+ | Single or 2-pose variants | PNG |

**Character List (40+ sprites):**
Captain_Veynar, Dalen, Drossel, Inodora, Kaelen, Korrin, Mariel, Nima, Ravi, Sanor, Saori, Sera, Tala, Tariq, Tessa, Tovren, Velinor, Swamp_trickster

**Technical Details:**
- Most with transparent backgrounds (PNG)
- Ravi & Nima have pixel-art variants
- Kaelen has 3 color variants (trickster states)
- Turntable/sprite sheets available (some)
- Ready for Unity sprite import

### 2.3 Glyph Artwork (~80+ files)
**Location:** `velinor/glyph_images/`

**Subdirectories:**
- `archived_full-color_glyphs/` — Previous glyph art
- `codex_glyphs/` — Current codex-style glyphs
- `full-color_glyphs/` — High-quality color versions
- `transcendance/` — Special glyph variants

**Details:**
- 118 unique glyph illustrations
- Multiple artistic styles
- PNG format with transparency
- Used in UI/glyph codex overlay
- Texture-rich (suitable for UI panels)

### 2.4 UI Overlay Assets
**Location:** `velinor/overlays/`

| Asset | Type | Purpose |
|-------|------|---------|
| Glyph_Codex_tablet.png | PNG | Glyph display interface |
| Glyph_Codex2.svg | SVG | Codex UI frame |
| Page_curl overlays | PNG | Book-style transitions |
| Glowing_swamp_overlay | PNG | Environmental effect |
| velinor_title_transparent2.png | PNG | Title overlay |

### 2.5 3D Assets (Limited)
**Location:** `velinor/assets/`

| File | Type | Format | Scale | Status |
|------|------|--------|-------|--------|
| brickhouse-entrance_velinorian.* | 3D Model | OBJ, MTL, GLB | Full | ✅ Ready |

**Details:**
- 1 main 3D model (building entrance)
- Multiple formats available (OBJ, MTL, GLB)
- Could be used as environment/prop
- Limited 3D asset library overall

### 2.6 Video Assets (5 files)
**Location:** `velinor/video/`

| Asset | Type | Purpose | Formats | Size |
|-------|------|---------|---------|------|
| Tessa_Greeting | Video | Character intro | MP4, WebM | Multiple grades |
| Sealina_street_performance | Video | Character animation | MP4, WebM | Multiple grades |
| Sealina_pose_out/ | Motion Capture | BVH + metadata | BVH, JSON, MP4 | Pose landmarks |
| pose_landmarker.task | ML Model | MediaPipe landmark detection | .task | For pose analysis |

---

## 3. DATA FILES (DIRECTLY PORTABLE)

### 3.1 Glyph Data
**Location:** `velinor/data/` and `data/glyphs/`

| File | Records | Format | Type | Portable |
|------|---------|--------|------|----------|
| `glyph_lexicon_rows.json` | 118+ | JSON | Master glyph list | ✅ **YES** |
| `Glyph_Organizer.json` | 118 | JSON | Structured glyph data | ✅ **YES** |
| `cipher_seeds.json` | 118 | JSON | Emotional gate requirements | ✅ **YES** |
| `cleaned_glyphs.json` | All | JSON | Validated glyph set | ✅ **YES** |
| `antonym_glyphs_indexed.json` | 118 | JSON | Antonym relationships | ✅ **YES** |
| `Glyph_Rules.json` | — | JSON | Glyph mechanics rules | ✅ **YES** |
| `phase_*_glyphs.json` | Various | JSON | Development iterations | ⚠️ Reference only |

**Data Structure Sample:**
```json
{
  "id": 62,
  "glyph_name": "Glyph of Fractured Memory",
  "domain": "Collapse",
  "npc": "Archivist Malrik",
  "location": "Archive Chamber",
  "layer_0": "Poetic fragment",
  "layer_1": "NPC perspective",
  "layer_2": "Plaintext truth",
  "required_gates": ["coherence > 70", "empathy > 50"],
  "tags": ["collapse", "memory", "fear", "fracture"]
}
```

### 3.2 NPC & Character Data
**Location:** `velinor/data/` and `velinor/npcs/`

| File | Records | Format | Type | Portable |
|------|---------|--------|------|----------|
| `npc_profiles.json` | 21+ | JSON | NPC definitions | ✅ **YES** |
| `npc_registry.json` | 21+ | JSON | NPC registry | ✅ **YES** |
| `npc_remnants_profiles.json` | 21+ | JSON | NPC emotional profiles | ✅ **YES** |
| `npc_state.json` | State | JSON | Current NPC states | ✅ **YES** |
| `npc_profiles.py` | 21+ | Python | Legacy NPC definitions | ⚠️ Convert to JSON |

**Key NPC Fields:**
- Character name & role
- Emotional gates (TONE thresholds)
- Glyph affiliations (5-7 per NPC)
- Location associations
- Dialogue response patterns

### 3.3 Story & Scene Data
**Location:** `velinor/stories/`

| File | Records | Format | Type | Portable |
|------|---------|--------|------|----------|
| `Glyph_of_Legacy.json` | 1 story | JSON | Full story arc | ✅ **YES** |
| `sample_story.json` | 1 story | JSON | Story structure | ✅ **YES** |
| `swamp_trickster_scene.json` | 1 scene | JSON | Single scene data | ✅ **YES** |
| `ravi_nima/` | Multiple | JSON | Character arc data | ✅ **YES** |

### 3.4 Emotional Lexicon & Tagging Data
**Location:** `data/lexicons/` and `data/`

| File | Records | Format | Type | Purpose | Portable |
|------|---------|--------|------|---------|----------|
| `lexicon_enhanced.json` | 3000+ | JSON | Emotional word mapping | Dialogue tagging | ✅ **YES** |
| `nrc_lexicon_cleaned.json` | 13,000+ | JSON | NRC emotion lexicon | Word-emotion mapping | ✅ **YES** |
| `word_centric_emotional_lexicon.json` | 10,000+ | JSON | Semantic mapping | Emotion inference | ✅ **YES** |
| `openstax_psych_phrases.csv` | 500+ | CSV | Psychology phrases | Context lexicon | ✅ **YES** |
| `nhs_bereavement_phrases.csv` | 200+ | CSV | Grief phrases | Special context | ✅ **YES** |

### 3.5 Glyph Cipher & Seeds
**Location:** `velinor/data/` and `velinor/markdowngameinstructions/glyphs/`

| File | Records | Format | Type | Portable |
|------|---------|--------|------|----------|
| `cipher_seeds.json` | 118 | JSON | Cipher seed definitions | ✅ **YES** |
| `cipher_seeds.csv` | 118 | CSV | Seed reference table | ✅ **YES** |
| `Glyph_Fragments.csv` | 118 | CSV | Layer 0 & 1 fragments | ✅ **YES** |
| `Glyph_Fragments_System.md` | — | MD | System documentation | 📖 Reference |
| `Glyph_Transcendence.csv` | 118 | CSV | Advanced unlock data | ✅ **YES** |

### 3.6 Trait & Stat Systems
**Location:** `velinor/markdowngameinstructions/systems/`

| File | Format | Type | Portable |
|------|--------|------|----------|
| `TONE_STAT_SYSTEM.md` | Markdown | System definition | ✅ **YES** |
| `Glyph_Rules.json` | JSON | Rule definitions | ✅ **YES** |
| `influence_map.json` | JSON | NPC influence relationships | ✅ **YES** |
| `emotion_map.json` | JSON | TONE ↔ emotion mapping | ✅ **YES** |

### 3.7 Save/Load System Data
**Location:** `velinor/` (runtime)

| File | Purpose | Format | Portable |
|------|---------|--------|----------|
| Game save states | Session persistence | JSON | ✅ **YES** |
| Player TONE history | Progress tracking | JSON | ✅ **YES** |
| NPC state snapshots | Relationship tracking | JSON | ✅ **YES** |
| Glyph unlock history | Achievement tracking | JSON | ✅ **YES** |

### 3.8 Database Files
**Location:** `velinor/data/` and root

| File | Type | Purpose | Portable |
|------|------|---------|----------|
| `glyphs.db` | SQLite | Glyph metadata (legacy) | ⚠️ Export & convert |
| `synonyms.db` | SQLite | Lexicon synonyms | ⚠️ Export & convert |

---

## 4. DOCUMENTATION (DESIGN SPECIFICATIONS)

### 4.1 Master Design Documents
**Location:** `velinor/` (root files)

| Document | Purpose | Length | Key Content | Portability |
|-----------|---------|--------|------------|------------|
| `VELINOR_MASTER_DOC.md` | **Authoritative game spec** | ~2000 lines | All game systems, mechanics, NPC logic | 📖 **REFERENCE** |
| `VELINOR_INTEGRATION_CONTRACT.md` | System interface contract | ~500 lines | How systems interact | 📖 **REFERENCE** |
| `VELINOR_STREAMLIT_IMPLEMENTATION_GUIDE.md` | Current implementation | ~1000 lines | Streamlit-specific (for reference) | 📖 **REFERENCE** |
| `VELINOR_NARRATIVE_SOURCE_MATERIAL.md` | Story bible | ~1500 lines | Character arcs, themes, endings | 📖 **REFERENCE** |

### 4.2 Game Systems Documentation
**Location:** `velinor/markdowngameinstructions/systems/`

| Document | Covers | Portable Content |
|-----------|--------|------------------|
| `TONE_STAT_SYSTEM.md` | TONE mechanics (4-dimensional emotional space) | ✅ Core mechanics definition |
| `04_collapse_mechanics.md` | Collapse event mechanics | ✅ Story trigger system |
| `05_EMOTIONAL_OS_MECHANICS_INTEGRATION.md` | Emotional OS integration | ✅ System design |
| `05_npc_reaction_library.md` | NPC response patterns | ✅ Dialogue patterns |
| `skill_tree_lying.md` | Skill deception mechanics | ✅ Mechanic definition |

### 4.3 Glyph System Documentation
**Location:** `velinor/markdowngameinstructions/glyphs/`

| Document | Purpose |
|-----------|---------|
| `BUILDING_DEBATE_GLYPHS_QUICK_REFERENCE.md` | Glyph creation guide |
| `Glyph_Fragments_System.md` | 3-tier cipher explanation |
| `Glyph_Rules_SUGGESTIONS.md` | Glyph mechanic examples |
| `Glyph_Organizer_REMNANTS.md` | Remnants integration |

### 4.4 Character & NPC Documentation
**Location:** `velinor/markdowngameinstructions/characters/` & `npcs/`

| Document | Coverage |
|-----------|----------|
| `CHARACTER_CREATION_MASTER_REFERENCE.md` | Player character system |
| `Ravi_Nima_Ophina.md` | Character arc definitions |
| `NPC_SPHERE_SYSTEM.md` | NPC relationship system |
| `MARKETPLACE_NPC_ROSTER.md` | NPC catalog & roles |
| `npcs.md` | NPC reference guide |

### 4.5 Story & Narrative Documentation
**Location:** `velinor/markdowngameinstructions/story/`

| Document | Content | Key |
|-----------|---------|-----|
| `01_NARRATIVE_SPINE_AND_STRUCTURE.md` | Main story spine | 6 distinct endings |
| `02_SIX_ENDINGS_EXPLICIT_MAP.md` | Ending conditions | TONE-based ending selection |
| `story_arcs.md` | Character story arcs | 10+ interconnected arcs |
| `the_fourth_layer.md` | Advanced layer mechanics | Depth system |
| `VELINOR_SAORI_FINAL_ARC.md` | Final character arc | Endgame narrative |
| `overarching_game_story.md` | World structure | High-level narrative |

### 4.6 Integration & Architecture
**Location:** `docs/`

| Document | Covers |
|-----------|--------|
| `VELINOR_WEB_MASTER_DOC.md` (if exists) | Web implementation |
| `FIRSTPERSON_VELINOR_INTEGRATION_GUIDE.md` | AI companion integration |
| `PHASE_3_2_INTEGRATION_GUIDE.md` | System integration patterns |

---

## 5. TOOLS & UTILITIES

### 5.1 Content Creation Tools
**Location:** `velinor/` and `tools/`

| Tool | Purpose | Type | Portable |
|------|---------|------|----------|
| `velinor/glyph_cipher_engine.py` | Glyph cipher query | Utility | ✅ Convert to C# |
| `velinor/stories/build_story.py` | Story builder | Builder | ✅ Convert to C# |
| `velinor/stories/story_validator.py` | Story validation | Validator | ✅ Convert to C# |
| `velinor/stories/story_map_parser.py` | Story map parser | Parser | ✅ Convert to C# |
| `velinor/npc_profiles.py` | NPC profile loader | Loader | ✅ Convert to C# |

### 5.2 Data Management Tools
**Location:** `tools/`

| Tool | Purpose |
|------|---------|
| `glyph_tools/` | Glyph creation & management |
| `glyph_testing/` | Glyph validation suite |
| `analysis/` | Repository analysis |
| `document_processing/` | Content processing |

### 5.3 Diagnostic & Testing Tools
**Location:** `tools/`

| Tool | Purpose |
|------|---------|
| `self_diagnostic.py` | System diagnostics |
| `smoke_test_responder.py` | Quick validation |
| `simulate_transcript.py` | Dialogue simulation |
| `e2e_chat_test.py` | End-to-end testing |

### 5.4 Utility Scripts
**Location:** Root & `velinor/`

| Script | Purpose |
|--------|---------|
| `velinor/assign_seeds_to_npcs.py` | Cipher seed assignment |
| `velinor/generate_cipher_seeds.py` | Seed generation |
| `velinor/generate_seeds_from_corpus.py` | Corpus-based generation |
| `velinor/micro_loop.py` | Interactive glyph tutorial |

---

## 6. CATEGORIZATION BY PORTABILITY

### 6.1 ✅ DIRECTLY PORTABLE (40-50%)

**Can be imported as-is or with minimal conversion to Unity/C#:**

#### A. Game Data Files (100% portable)
- ✅ All JSON glyph definitions (`glyph_lexicon_rows.json`, `Glyph_Organizer.json`, `cipher_seeds.json`)
- ✅ All NPC profile data (`npc_profiles.json`, `npc_registry.json`)
- ✅ Story data files (`Glyph_of_Legacy.json`, `sample_story.json`)
- ✅ All emotional lexicon files (NRC, enhanced, word-centric)
- ✅ Trait & stat system definitions (JSON)
- ✅ Influence maps & emotion mappings

**Migration Path:** 
```
JSON → Parse in Unity → ScriptableObjects/Prefabs
CSV → Parse in Unity → Data structures
```

#### B. Graphics Assets (100% portable)
- ✅ **All background images** (45+ PNG/JPG files)
- ✅ **All character sprites** (40+ PNG files with transparency)
- ✅ **All glyph artwork** (118+ PNG files)
- ✅ **UI overlay assets** (PNG/SVG files)
- ✅ **3D model** (OBJ/MTL/GLB format)
- ✅ **Video assets** (MP4, WebM)

**Migration Path:**
```
PNG/JPG → Import directly as sprites/textures
OBJ/MTL → FBX conversion → Unity import
WebM/MP4 → Unity VideoPlayer
```

#### C. Game Logic (Mostly Portable)
- ✅ **Trait System logic** (TONE tracking algorithm)
  - 4-dimensional stat space
  - Clamping rules (0-100)
  - Stat modification math
  - Portable: Direct C# translation

- ✅ **Coherence Calculator**
  - Formula: `100 - avg_deviation(empathy, skepticism, integration, awareness)`
  - Portable: Direct implementation

- ✅ **NPC Response Engine logic**
  - Emotional gate checking
  - Coherence-based response selection
  - Portable: Direct translation

- ✅ **Glyph Cipher Engine logic**
  - Layer unlock mechanics
  - Gate requirement checking
  - Portable: Direct translation

- ✅ **Ending System**
  - 6 ending conditions based on TONE state
  - Portable: Decision tree implementation

- ✅ **Skill System mechanics**
  - Skill check logic
  - Difficulty calculation
  - Portable: Direct translation

#### D. Documentation (100% Reference)
- 📖 All design documents (complete specifications)
- 📖 Story bibles and character arcs
- 📖 System mechanics definitions
- 📖 Integration contracts

### 6.2 ⚠️ NEEDS CONVERSION (30-40%)

**Requires format conversion but logic is sound:**

#### A. Streamlit UI → Unity UI
| Current (Streamlit) | Target (Unity) | Effort |
|------------------|----------------|--------|
| `streamlit_ui.py` | UI Canvas system | Medium |
| Sidebar elements | UI Panel/HUD | Medium |
| Button grid (2x2+1) | Button layout system | Low |
| Dialogue box | Text panel + typewriter | Medium |
| NPC overlay rendering | Sprite + layering | Medium |
| Scene transitions | Unity Animator/Coroutines | Medium |
| Tone stats display | UI text/progress bars | Low |
| Glyph codex overlay | Canvas overlay | Medium |

**Estimate:** 2-3 weeks (intermediate developer)

#### B. Streamlit State Management → Unity State Management
| Current | Target | Conversion |
|---------|--------|-----------|
| `streamlit_state.py` | Scriptable Objects | Parse & recreate |
| Session persistence | PlayerPrefs/JSON save system | Reimplement |
| State callbacks | Unity events/Observer pattern | Reimplement |

#### C. Asset Format Conversions
| Source | Target | Tool |
|--------|--------|------|
| SVG overlays | PNG/WebP | Inkscape/ImageMagick |
| WebM video | MP4 (if needed) | FFmpeg |
| OBJ 3D model | FBX | Blender/FBX SDK |
| BVH motion capture | Animation curves | Blender/custom importer |

#### D. LLM Dialogue System → Dialog Integration
| Current | Status | Options |
|---------|--------|---------|
| `llm_dialogue.py` | Server-based LLM calls | 1. Integrate same API (OpenAI/Claude) |
| | | 2. Use local LLM (Ollama) |
| | | 3. Pre-generate dialogue (JSON trees) |

**Decision Point:** Will you keep dynamic dialogue or use pre-written dialogue trees?

#### E. Database Exports (SQLite → JSON/CSV)
| Database | Export Strategy |
|----------|-----------------|
| `glyphs.db` | Export tables → JSON |
| `synonyms.db` | Export tables → CSV/JSON |

### 6.3 🔴 REWRITE REQUIRED (20-30%)

**Core engine components that need full rewrite:**

#### A. Game Loop & Orchestration
| Component | Current | Required Rewrite |
|-----------|---------|------------------|
| Main game loop | Streamlit callback-based | Unity Update/Coroutine-based |
| Frame rate | Streamlit polling | Unity 60+ FPS |
| Scene management | Streamlit page routing | Unity Scene Manager |
| Input handling | Streamlit UI buttons | Unity Input System |
| Event system | Streamlit callbacks | Unity Event system |

**Effort:** 2-3 weeks (intermediate developer)

#### B. Rendering & Graphics
| Component | Current | Required Change |
|-----------|---------|-----------------|
| Background rendering | Streamlit image display | Unity Canvas/SpriteRenderer |
| Character rendering | PNG overlay compositing | Unity sprite layering system |
| Animation | Static sprites + transitions | Unity Animator + sprite animation |
| UI rendering | Streamlit components | Canvas UI system |
| Glyph display | Streamlit image overlay | Canvas overlay with animations |

**Effort:** 2-4 weeks (intermediate developer)

#### C. Audio System
| Component | Current Status | To Implement |
|-----------|-------|-------------|
| Dialogue audio | Not implemented | Text-to-speech or pre-recorded |
| Ambient music | MIDI prototypes exist | Audio import & playback |
| Sound effects | Not implemented | SFX system |
| Music system | `velinor_motif.mid` | Music manager |

**Effort:** 1-2 weeks

#### D. Input & Interaction System
| Current | Required |
|---------|----------|
| Streamlit buttons for choices | Dynamic choice button system |
| Sidebar interaction | Touch/mouse/keyboard input |
| Click-to-advance | Full input management |

**Effort:** 1-2 weeks

#### E. Save/Load System
| Current | Required |
|---------|----------|
| JSON-based (session files) | Persistent save slots |
| In-memory state | Serialization system |
| No versioning | Save file versioning |

**Effort:** 1-2 weeks

#### F. Scene/Location System
| Current | Required |
|---------|----------|
| Python data model | Unity GameObjects + scenes |
| Story branching | Unity scene loading + logic |
| NPC positioning | 2D/3D object placement |
| Environmental interaction | Colliders + interaction system |

**Effort:** 2-3 weeks

---

## 7. FILE STRUCTURE SUMMARY

### 7.1 Python Source Files
```
velinor/
├── engine/                           # Core game systems
│   ├── core.py                       # Main game state
│   ├── orchestrator.py               # Game loop
│   ├── game_state.py                 # State persistence
│   ├── trait_system.py               # TONE tracking ✅
│   ├── coherence_calculator.py       # Emotional harmony ✅
│   ├── npc_manager.py                # NPC management ✅
│   ├── npc_response_engine.py        # NPC dialogue ✅
│   ├── scene_manager.py              # Scene transitions
│   ├── ending_system.py              # 6 endings logic ✅
│   ├── skill_system.py               # Skill mechanics ✅
│   └── ... (20+ files)
├── game_mechanics/
│   ├── characters.py                 # Character classes ✅
│   └── frontend_api.ts               # TypeScript interface
├── glyph_cipher_engine.py            # Glyph unlock logic ✅
├── stories/
│   ├── build_story.py                # Story builder
│   ├── story_definitions.py          # Story structure
│   ├── story_validator.py            # Validation
│   └── ... (JSON story files)
├── markdowngameinstructions/         # Design documentation
│   ├── characters/                   # Character specs
│   ├── npcs/                         # NPC documentation
│   ├── systems/                      # System docs
│   ├── glyphs/                       # Glyph definitions
│   └── story/                        # Story specs
├── streamlit_ui.py                   # 🔴 REWRITE
├── streamlit_state.py                # 🔴 REWRITE
└── ... (60+ files total)
```

### 7.2 Data Files
```
data/
├── glyphs/
│   ├── glyph_lexicon_rows.json       # ✅ Master glyph data
│   ├── cipher_seeds.json             # ✅ Cipher definitions
│   ├── Glyph_Organizer.json          # ✅ Structured data
│   └── ... (10+ files)
├── lexicons/
│   ├── lexicon_enhanced.json         # ✅ Emotion mapping
│   ├── nrc_lexicon_cleaned.json      # ✅ Word emotions
│   └── ... (5+ files)
└── ... (30+ data files)

velinor/data/
├── npc_profiles.json                 # ✅ NPC definitions
├── npc_registry.json                 # ✅ NPC tracking
├── glyphs.db                         # ⚠️ Export to JSON
└── ... (CSV, JSON data)
```

### 7.3 Assets
```
velinor/
├── backgrounds/                      # ✅ 45+ PNG/JPG
├── npcs/                             # ✅ 40+ PNG sprites
├── glyph_images/                     # ✅ 118+ PNG glyphs
├── overlays/                         # ✅ UI overlays
├── assets/                           # ✅ 3D models
└── video/                            # ✅ MP4, WebM files
```

---

## 8. ESTIMATED MIGRATION EFFORT

### 8.1 Time Breakdown (Man-Weeks for Experienced Developer)

| Component | Effort | Type | Notes |
|-----------|--------|------|-------|
| **Data Layer** | 1-2 weeks | Conversion | JSON parsing, DB export |
| **Core Logic (Game Systems)** | 2-3 weeks | Translation | Direct C# translation |
| **Glyph/Cipher System** | 1 week | Translation | Well-defined logic |
| **NPC System** | 2 weeks | Translation | Logic + integration |
| **Story/Ending System** | 1-2 weeks | Translation | Decision trees |
| **Trait/Stat System** | 1 week | Translation | Simple algorithms |
| **Asset Integration** | 1 week | Import | Sprite sheets, textures |
| **UI/Canvas System** | 3-4 weeks | **REWRITE** | Largest effort item |
| **Game Loop/Scene Mgmt** | 2-3 weeks | **REWRITE** | Core engine diff |
| **Input System** | 1-2 weeks | **REWRITE** | Button/choice selection |
| **Save/Load System** | 1-2 weeks | **REWRITE** | Persistence layer |
| **Dialogue System** | 2 weeks | **Varies** | Depends on approach |
| **Audio (basic)** | 1 week | **Add** | Music + SFX |
| **Testing & Polish** | 2-3 weeks | QA | Integration testing |
| **TOTAL** | **20-30 weeks** | | ~5-7.5 months (1 developer) |

### 8.2 Parallelization Opportunity

**For a 2-person team:**
- Person A: Data layer + Logic conversion (parallel)
- Person B: UI/Canvas + Graphics integration (parallel)
- Combined: 10-15 weeks with integration overlap

---

## 9. MIGRATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
- [ ] Export all JSON/CSV data
- [ ] Create C# data models from JSON
- [ ] Implement TONE trait system
- [ ] Set up Unity project structure
- [ ] Import graphics assets

### Phase 2: Core Logic (Weeks 5-8)
- [ ] Implement coherence calculator
- [ ] Implement glyph cipher engine
- [ ] Implement NPC manager
- [ ] Implement skill system
- [ ] Implement ending system

### Phase 3: Game Loop & Rendering (Weeks 9-14)
- [ ] Create main game loop (Update-based)
- [ ] Implement scene management
- [ ] Build sprite rendering system
- [ ] Create dialogue box/text system
- [ ] Implement choice button system

### Phase 4: UI & UX (Weeks 15-20)
- [ ] Create Canvas UI for game
- [ ] Implement TONE stat display
- [ ] Create glyph codex overlay
- [ ] Build settings/menu UI
- [ ] Polish transitions

### Phase 5: Systems & Polish (Weeks 21-25)
- [ ] Audio system (music + dialogue)
- [ ] Save/load system
- [ ] Input handling
- [ ] Animation system
- [ ] Bug fixes & optimization

### Phase 6: Testing & Deployment (Weeks 26-30)
- [ ] Full play-through testing
- [ ] Platform-specific optimization
- [ ] Build & deployment setup
- [ ] Performance profiling
- [ ] Release prep

---

## 10. KEY DEPENDENCIES & RISKS

### 10.1 Dependency Mapping
```
Game Loop (REWRITE)
├── Input System (REWRITE)
├── Scene Manager (REWRITE)
├── NPC Manager (TRANSLATE)
│   ├── NPC Response Engine (TRANSLATE)
│   ├── Dialogue System (VARIES)
│   └── Glyph Cipher Engine (TRANSLATE)
├── Trait System (TRANSLATE)
├── Story/Ending System (TRANSLATE)
├── UI System (REWRITE)
│   ├── Canvas rendering
│   ├── Sprite rendering
│   └── Dialogue display
└── Asset system (IMPORT)
    ├── Sprite manager
    ├── Audio manager
    └── 3D object manager
```

### 10.2 Key Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **LLM Dialogue Dependency** | Can't proceed without strategy | Decide early: API vs Pre-written vs Local LLM |
| **Complex Story Logic** | Implementation bugs | Create comprehensive test suite during Phase 2 |
| **Asset Organization** | Import errors | Use consistent naming convention upfront |
| **Performance (mobile?)** | Gameplay issues | Profile early, optimize sprites/scenes |
| **Save File Format** | Data loss | Design versioning system in Phase 5 |

---

## 11. ASSET CHECKLIST FOR IMPORT

### Graphics (Ready to Import)
- [ ] 45 background images (organize by location)
- [ ] 40 character sprites (organize by NPC)
- [ ] 118 glyph illustrations (organize by domain)
- [ ] UI overlay assets
- [ ] 3D entrance model (convert OBJ→FBX)

### Data (Ready to Convert)
- [ ] 118 glyph definitions (JSON)
- [ ] 21+ NPC profiles (JSON)
- [ ] Story data (JSON)
- [ ] Emotional lexicon (JSON)
- [ ] Trait definitions (JSON)

### Documentation (For Reference)
- [ ] VELINOR_MASTER_DOC.md (game rules)
- [ ] Story bibles (6 endings, arcs)
- [ ] Design specifications
- [ ] System mechanics docs

---

## 12. QUICK START CONVERSION SCRIPT

```python
# Suggested order for C# implementation:

# 1. Data Models
ToneState.cs           # 4-stat emotional tracking
GameState.cs           # Session persistence
NpcProfile.cs          # NPC definitions
GlyphSeed.cs           # Glyph cipher definitions
CharacterArc.cs        # Story structure

# 2. Core Systems
TraitSystem.cs         # TONE modification
CoherenceCalculator.cs # Emotional harmony
GlyphCipherEngine.cs   # Glyph unlock logic
NpcResponseEngine.cs   # Dialogue selection
EndingSystem.cs        # 6 endings logic

# 3. Game Logic
GameManager.cs         # Main orchestrator
NpcManager.cs          # NPC instance management
StoryManager.cs        # Scene/story progression
SkillSystem.cs         # Skill checks

# 4. UI/Rendering
UIManager.cs           # Canvas management
DialogueBoxUI.cs       # Text display
CharacterRenderer.cs   # Sprite rendering
BackgroundRenderer.cs  # Scene rendering

# 5. Systems
InputManager.cs        # Button/choice handling
AudioManager.cs        # Music + SFX
SaveLoadManager.cs     # Persistence
SceneManager.cs        # Scene transitions
```

---

## 13. CONCLUSION

**Portability Summary:**
- **✅ 40-50%** of codebase is data/logic that translates directly to C#
- **⚠️ 30-40%** requires conversion (format, framework differences)
- **🔴 20-30%** needs rewriting (Streamlit UI → Unity UI, game loop)

**Recommended Approach:**
1. Start with data layer (JSON → C# models)
2. Translate core logic (algorithms remain identical)
3. Build Unity UI from Streamlit mockups
4. Integrate assets and test
5. Polish and optimize

**Success Factors:**
- Early decision on dialogue system (API vs. pre-written vs. local LLM)
- Comprehensive test coverage during logic translation
- Asset naming/organization from the start
- Regular playtesting throughout migration

