# Velinor → Unity: Detailed File Inventory & Categorization

**Quick Reference for Migration Planning**

---

## TABLE OF CONTENTS
1. [Game Engine Files](#game-engine-files)
2. [Data Model Files](#data-model-files)
3. [Streamlit UI Files (REWRITE)](#streamlit-ui-files-rewrite)
4. [Asset & Configuration Files](#asset--configuration-files)
5. [Test & Utility Files](#test--utility-files)
6. [Documentation Index](#documentation-index)

---

## GAME ENGINE FILES

### CRITICAL (Core Logic - Must Translate to C#)

```
velinor/engine/core.py
├─ Purpose: Main game state machine
├─ Priority: 🔴 CRITICAL
├─ Size: ~400 lines
├─ Dependencies: game_state.py, orchestrator.py
├─ Portability: ✅ Direct C# translation
├─ Key Classes: GameCore, StateManager
└─ Notes: Central orchestration point
   → To C#: GameCore.cs, StateManager.cs

velinor/engine/orchestrator.py
├─ Purpose: Game loop orchestration & turn management
├─ Priority: 🔴 CRITICAL
├─ Size: ~350 lines
├─ Portability: ✅ Direct translation (callback → coroutine)
├─ Key Method: next_turn(), process_choice()
└─ Migration Note: Streamlit callback → Unity Update/Coroutine

velinor/engine/game_state.py
├─ Purpose: GameState class, session persistence
├─ Priority: 🔴 CRITICAL
├─ Size: ~300 lines
├─ Portability: ✅ Direct C# translation
├─ Key Classes: GameState, PlayerState, WorldState
├─ Serialization: JSON (save/load)
└─ Migration Path: GameState.cs + JSON serializer

velinor/engine/scene_manager.py
├─ Purpose: Scene transitions, location management
├─ Priority: 🔴 CRITICAL
├─ Size: ~250 lines
├─ Portability: ✅ Direct translation (Python scenes → Unity scenes)
├─ Key Methods: load_scene(), transition()
└─ Migration Note: Adapt to Unity Scene Manager API

velinor/engine/event_timeline.py
├─ Purpose: Event sequencing, narrative timeline
├─ Priority: 🔴 HIGH
├─ Size: ~200 lines
├─ Portability: ✅ Direct translation
├─ Key Classes: EventTimeline, Event
└─ Notes: Tracks story progression milestones
```

### EMOTIONAL OS SYSTEM

```
velinor/engine/trait_system.py
├─ Purpose: TONE stat tracking (Empathy, Skepticism, Integration, Awareness)
├─ Priority: 🔴 CRITICAL
├─ Size: ~280 lines
├─ Portability: ✅ 100% - Direct C# translation
├─ Key Classes: ToneState, TraitManager
├─ Algorithm: Stat modification with clamping (0-100)
└─ Migration: TraitSystem.cs (identical logic)
   ┌─ Empathy: 0-100 (compassion)
   ├─ Skepticism: 0-100 (questioning)
   ├─ Integration: 0-100 (acceptance)
   └─ Awareness: 0-100 (self-understanding)

velinor/engine/coherence_calculator.py
├─ Purpose: Emotional harmony/coherence calculation
├─ Priority: 🔴 CRITICAL
├─ Size: ~150 lines
├─ Portability: ✅ 100% - Pure math
├─ Algorithm: coherence = 100 - avg_deviation(all_stats)
├─ Range: 0-100
└─ Migration: Single method in TraitSystem.cs

velinor/engine/resonance.py
├─ Purpose: Emotional resonance between player & NPCs
├─ Priority: 🔴 HIGH
├─ Size: ~200 lines
├─ Portability: ✅ Direct translation
├─ Key Method: calculate_resonance(player_tone, npc_profile)
└─ Notes: Affects dialogue depth & unlocks
```

### NPC & DIALOGUE SYSTEMS

```
velinor/engine/npc_manager.py
├─ Purpose: NPC instantiation, state, interaction
├─ Priority: 🔴 CRITICAL
├─ Size: ~280 lines
├─ Portability: ✅ Direct translation
├─ Key Classes: NpcManager, NpcInstance, NpcState
├─ Manages: 21+ NPC instances
└─ Dependencies: npc_response_engine.py, trait_system.py

velinor/engine/npc_response_engine.py
├─ Purpose: Generate NPC dialogue based on coherence, gates
├─ Priority: 🔴 CRITICAL
├─ Size: ~300 lines
├─ Portability: ✅ Direct translation
├─ Key Method: get_response(state, trigger)
├─ Logic: Gate checking → Response selection
└─ ⚠️ Note: Currently uses LLM (decide: API/local/pre-written)

velinor/engine/npc_encounter.py
├─ Purpose: NPC encounter flow & dialogue trees
├─ Priority: 🔴 HIGH
├─ Size: ~220 lines
├─ Portability: ✅ Direct translation
├─ Key Classes: Encounter, DialogueTree
└─ Notes: Manages single NPC conversation

velinor/engine/dialogue_context.py
├─ Purpose: Maintain dialogue context, history
├─ Priority: 🔴 HIGH
├─ Size: ~180 lines
├─ Portability: ✅ Direct translation
├─ Tracks: Previous dialogue, emotional state during conversation
└─ Notes: Important for dynamic dialogue
```

### STORY & ENDING SYSTEM

```
velinor/engine/ending_system.py
├─ Purpose: 6 distinct endings based on TONE state
├─ Priority: 🔴 CRITICAL
├─ Size: ~200 lines
├─ Portability: ✅ 100% - Pure decision logic
├─ Endings: 6 conditions based on TONE trajectory
├─ Key Method: calculate_ending(final_tone_state)
└─ Migration: EndingSystem.cs
   Ending 1: High Empathy, High Integration
   Ending 2: High Skepticism, Low Empathy
   Ending 3: High Awareness (self-knowledge)
   Ending 4: Balanced all stats (harmony)
   Ending 5: Low Coherence (fragmentation)
   Ending 6: Collapse event path (catastrophe)

velinor/stories/story_definitions.py
├─ Purpose: Story structure, scene definitions
├─ Priority: 🔴 CRITICAL
├─ Size: ~250 lines
├─ Portability: ✅ Convert to ScriptableObject/JSON
├─ Defines: 30+ scenes, choice consequences
└─ Migration: Parse → C# data models

velinor/stories/build_story.py
├─ Purpose: Story builder/validator utility
├─ Priority: 🟡 MEDIUM
├─ Size: ~180 lines
├─ Portability: ✅ Can rebuild in C# or use as reference
└─ Notes: For content creation, not runtime

velinor/stories/story_validator.py
├─ Purpose: Validate story consistency
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ Convert or use as reference
└─ Useful: During development for data validation
```

### MECHANICS SYSTEMS

```
velinor/engine/skill_system.py
├─ Purpose: Skill checks, ability resolution
├─ Priority: 🟡 MEDIUM
├─ Size: ~150 lines
├─ Portability: ✅ Direct translation
├─ Mechanics: DC, roll, modifiers
└─ Migration: SkillSystem.cs

velinor/game_mechanics/characters.py
├─ Purpose: Character & ToneState classes
├─ Priority: 🔴 HIGH
├─ Size: ~150 lines
├─ Portability: ✅ 100% - Simple dataclasses
├─ Key Classes: ToneState (0-100 scale), GameMechanics
└─ Migration: Character.cs, ToneState.cs (trivial)

velinor/engine/marketplace_scenes.py
├─ Purpose: Marketplace scene logic
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ Direct translation
└─ Notes: NPC gathering mechanics

velinor/engine/collapse_scene.py
├─ Purpose: Collapse event (pivotal narrative moment)
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ Direct translation
└─ Notes: Story branch point
```

### SUPPORT SYSTEMS

```
velinor/engine/save_system.py
├─ Purpose: Save/load game state
├─ Priority: 🔴 HIGH
├─ Portability: ⚠️ Needs rewrite for Unity
├─ Notes: Python pickle → C# JSON/binary
└─ Migration: SaveManager.cs + serialization

velinor/engine/load_system.py
├─ Purpose: Load saved games
├─ Priority: 🔴 HIGH
├─ Portability: ⚠️ Needs rewrite
└─ Migration: Part of SaveManager.cs

velinor/engine/assets_config.py
├─ Purpose: Asset path configuration
├─ Priority: 🟡 MEDIUM
├─ Portability: ⚠️ Adapt to Unity Resources/Addressables
└─ Notes: Will differ in Unity
```

---

## DATA MODEL FILES

### NPC & CHARACTER DATA

```
velinor/npc_profiles.py
├─ Purpose: NPC profile definitions (Python)
├─ Priority: 🔴 HIGH
├─ Portability: ⚠️ Convert to JSON (done in data/)
├─ Records: 21+ NPCs
├─ Status: Legacy - use JSON versions instead
└─ Migration: See npc_profiles.json

velinor/data/npc_profiles.json
├─ Purpose: NPC definitions in JSON
├─ Priority: 🔴 CRITICAL
├─ Portability: ✅ 100% portable
├─ Records: 21+ NPCs
├─ Fields: name, role, tone_gates, glyphs, dialogue_patterns
├─ Size: ~150 KB
└─ Migration: Direct import → C# models

velinor/data/npc_registry.json
├─ Purpose: NPC registry & relationships
├─ Priority: 🔴 HIGH
├─ Portability: ✅ 100% portable
├─ Size: ~80 KB
└─ Migration: NpcRegistry.cs + JSON deserialize

velinor/data/npc_remnants_profiles.json
├─ Purpose: NPC emotional profiles (Remnants system)
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
└─ Notes: Emotional state tracking per NPC

velinor/stories/npc_state.json
├─ Purpose: Current NPC states
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ Portable (session-specific)
└─ Notes: Used for persistence
```

### GLYPH DATA

```
velinor/data/glyph_lexicon_rows.json
├─ Purpose: Master glyph definitions
├─ Priority: 🔴 CRITICAL
├─ Portability: ✅ 100% portable
├─ Records: 118 glyphs
├─ Size: ~350 KB
├─ Fields: id, name, domain, npc, location, layers, gates
└─ Migration: Direct import → ScriptableObjects

velinor/markdowngameinstructions/glyphs/Glyph_Organizer.json
├─ Purpose: Structured glyph data
├─ Priority: 🔴 CRITICAL
├─ Portability: ✅ 100% portable
├─ Records: 118 glyphs
├─ Format: Hierarchical (domain → glyph → fields)
└─ Migration: Use instead of lexicon_rows if more detailed

velinor/data/cipher_seeds.json
├─ Purpose: Cipher seed definitions (unlock requirements)
├─ Priority: 🔴 CRITICAL
├─ Portability: ✅ 100% portable
├─ Records: 118 seeds
├─ Fields: id, glyph_name, npc, required_gates
└─ Migration: CipherSeed.cs + data import

velinor/data/cleaned_glyphs.json
├─ Purpose: Validated glyph set (production)
├─ Priority: 🔴 CRITICAL
├─ Portability: ✅ 100% portable
├─ Records: 118 glyphs
└─ Notes: Use this version (clean)

velinor/data/antonym_glyphs_indexed.json
├─ Purpose: Antonym relationships between glyphs
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Records: Antonym pairs
└─ Notes: For advanced glyph mechanics
```

### STORY DATA

```
velinor/stories/Glyph_of_Legacy.json
├─ Purpose: Complete story arc example
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Size: ~50 KB
└─ Notes: Reference implementation

velinor/stories/sample_story.json
├─ Purpose: Sample story structure
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
└─ Notes: Template for story creation

velinor/stories/swamp_trickster_scene.json
├─ Purpose: Single scene definition
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Size: ~20 KB
└─ Notes: Example scene structure
```

### EMOTION & TRAIT DATA

```
velinor/data/lexicons/lexicon_enhanced.json
├─ Purpose: Emotional word mapping
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Records: 3000+ emotion-word pairs
├─ Usage: Dialogue emotion tagging
└─ Size: ~200 KB

velinor/data/lexicons/nrc_lexicon_cleaned.json
├─ Purpose: NRC emotion lexicon (standardized)
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Records: 13,000+ words
├─ Emotions: 10 basic emotions + polarities
└─ Size: ~400 KB

velinor/data/lexicons/word_centric_emotional_lexicon.json
├─ Purpose: Word-centric emotion mapping
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Records: 10,000+ words
└─ Size: ~300 KB

velinor/markdowngameinstructions/systems/TONE_STAT_SYSTEM.md
├─ Purpose: TONE system specification (documented)
├─ Priority: 📖 REFERENCE
├─ Portability: ✅ Use for implementation guide
└─ Contains: Formulas, mechanics, integration points
```

### SUPPORT DATA

```
velinor/data/emotion_map.json
├─ Purpose: TONE ↔ emotion mapping
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Maps: 4 TONE stats to emotions
└─ Size: ~20 KB

velinor/data/influence_map.json
├─ Purpose: NPC influence relationships
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
├─ Defines: How NPCs affect each other
└─ Size: ~30 KB

velinor/data/Glyph_Fragments.csv
├─ Purpose: Glyph layer fragments (CSV)
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable (convert to JSON)
├─ Records: 118 glyphs × 3 layers
└─ Size: ~100 KB

velinor/data/Glyph_Rules.json
├─ Purpose: Glyph mechanics rules
├─ Priority: 🟡 MEDIUM
├─ Portability: ✅ 100% portable
└─ Notes: Rule engine definitions
```

---

## STREAMLIT UI FILES (REWRITE)

```
velinor/streamlit_ui.py
├─ Purpose: All Streamlit UI rendering
├─ Priority: 🔴 CRITICAL
├─ Size: ~600+ lines
├─ Portability: 🔴 COMPLETE REWRITE
├─ Components:
│   ├─ Sidebar (TONE, Remnants, Glyphs, Skills)
│   ├─ Background + NPC rendering
│   ├─ Dialogue box
│   ├─ Choice buttons (2×2 + action)
│   ├─ Scene transitions
│   └─ Glyph codex overlay
│
└─ Migration Path:
    UIManager.cs (canvas management)
    ├── DialogueBoxUI.cs
    ├── ChoiceButtonPanel.cs
    ├── SidebarUI.cs
    ├── CharacterRenderer.cs
    ├── BackgroundRenderer.cs
    └── GlyphCodexOverlay.cs

velinor/streamlit_state.py
├─ Purpose: Streamlit state management
├─ Priority: 🔴 CRITICAL
├─ Size: ~200 lines
├─ Portability: 🔴 REWRITE
├─ Streamlit Features:
│   ├─ st.session_state[] persistence
│   ├─ Callback system
│   └─ Rerun mechanism
├─ Migration Path:
    GameStateManager.cs (replace with Unity state)
    ├── Player settings (PlayerPrefs)
    ├── Session state (GameState)
    └── Event callbacks (Unity Events)
└─ Notes: Unity handles state differently

app.py
├─ Purpose: Streamlit entry point
├─ Priority: 🔴 CRITICAL
├─ Size: ~300 lines
├─ Portability: 🔴 REWRITE
├─ Streamlit Setup:
│   ├─ Page config
│   ├─ Logo/icon
│   ├─ Layout configuration
│   └─ Module imports
└─ Migration: Unity Main scene + GameManager
```

---

## ASSET & CONFIGURATION FILES

### Graphics Assets (Ready for Import)

```
velinor/backgrounds/ [45+ files]
├─ Total: ~200 MB PNG/JPG
├─ Portability: ✅ 100% - Direct import
├─ Format: PNG (transparent), JPG (optimized)
├─ Aspect Ratios: 16:9, 4:3
├─ Resolution: Variable (1024px-4K)
│
└─ By Location:
    ├─ Desert variants (5)
    ├─ Forest variants (4)
    ├─ Lake variants (3)
    ├─ City/Market (5)
    ├─ Swamp variants (4)
    ├─ Boss chamber (1)
    ├─ Title screens (3)
    ├─ Special locations (5)
    └─ Ending screens (10)

velinor/npcs/ [40+ files]
├─ Total: ~150 MB PNG
├─ Portability: ✅ 100% - Direct import as sprites
├─ Format: PNG with transparency
├─ Resolution: Variable (800px-2K)
├─ Variants: Full-body, headshot, pixel art, variants
│
└─ By Character (40+ total):
    ├─ Kaelen (4 variants)
    ├─ Ravi (3 variants, pixel)
    ├─ Nima (3 variants, pixel)
    ├─ Saori (5 poses)
    ├─ Tessa (4 variants)
    ├─ Veynar (3 variants)
    └─ Others (20+ more)

velinor/glyph_images/ [118+ files]
├─ Total: ~300 MB PNG
├─ Portability: ✅ 100% - Direct import
├─ Format: PNG with transparency
├─ Resolution: Variable
├─ Organization:
│   ├─ archived_full-color_glyphs/
│   ├─ codex_glyphs/ (current)
│   ├─ full-color_glyphs/
│   └─ transcendance/ (special)
└─ Count: 118 unique glyphs (1 per emotional category)

velinor/overlays/ [10+ files]
├─ Portability: ✅ 100% - Direct import
├─ Format: PNG, SVG
├─ Usage: UI overlays, page elements
└─ Files:
    ├─ Glyph codex frames
    ├─ Page curl effects
    ├─ Environmental overlays
    └─ Title elements

velinor/assets/ [3D models]
├─ brickhouse-entrance_velinorian.obj
├─ brickhouse-entrance_velinorian.mtl
├─ brickhouse-entrance_velinorian.glb
├─ Portability: ✅ OBJ/MTL/GLB - Needs conversion
├─ Format: OBJ (ASCII), MTL (material), GLB (binary)
├─ Usage: Environment building
└─ Migration: OBJ→FBX→Unity (use Blender)

velinor/video/ [5 files + pose data]
├─ Portability: ✅ Direct import (MP4/WebM)
├─ Files:
│   ├─ Tessa_Greeting.mp4
│   ├─ Sealina_street_performance.mp4
│   └─ Multiple quality grades
├─ Pose Data:
│   ├─ pose_landmarks.json (MediaPipe)
│   ├─ *.bvh (mocap format)
│   └─ pose_landmarker.task (ML model)
└─ Usage: Character intros, motion reference
```

### Configuration Files

```
velinor/config/config.py
├─ Purpose: Game configuration
├─ Portability: ⚠️ Needs adaptation
├─ Settings: Paths, defaults, API keys
└─ Migration: GameConfig.cs + ConfigData.json

velinor/engine/assets_config.py
├─ Purpose: Asset path mapping
├─ Portability: ⚠️ Adapt to Unity
├─ Notes: Will use Resources/Addressables
└─ Migration: AssetManager.cs

.streamlit/config.toml [if exists]
├─ Purpose: Streamlit configuration
├─ Portability: 🔴 Not needed
└─ Notes: Discard - Unity handles this

requirements_streamlit.txt
├─ Purpose: Python dependencies
├─ Portability: 🔴 Not needed
└─ Notes: Replace with Unity packages
```

---

## TEST & UTILITY FILES

### Testing Files

```
velinor/engine/test_skill_dialogue_integration.py
├─ Purpose: Skill + dialogue integration tests
├─ Portability: ✅ Can adapt to Unity test framework
├─ Size: ~200 lines
└─ Migration: Use as reference for C# unit tests

velinor/stories/test_dialogue_generation.py
├─ Purpose: Dialogue generation testing
├─ Portability: ✅ Adapt to C#/NUnit
└─ Notes: Important for LLM integration testing

velinor/stories/test_remnants_advanced.py
├─ Purpose: Remnants system testing
├─ Portability: ✅ Adapt to C#
└─ Notes: Test emotional gate logic

velinor/stories/test_remnants_simulation.py
├─ Purpose: Simulation testing
├─ Portability: ✅ Adapt to C#
└─ Notes: Test full game flows

velinor/stories/test_veynar_kaelen_dual_arc.py
├─ Purpose: Complex story arc testing
├─ Portability: ✅ Adapt to C#
└─ Notes: Test branching narrative

velinor/engine/sample_story.py
├─ Purpose: Example story
├─ Portability: ⚠️ Reference only
└─ Notes: Use as template
```

### Utility & Tool Scripts

```
velinor/glyph_cipher_engine.py
├─ Purpose: Glyph cipher query utility
├─ Portability: ✅ Translate to C#
├─ Usage: Development/debugging
└─ Migration: Part of GlyphSystem.cs

velinor/micro_loop.py
├─ Purpose: Interactive glyph tutorial
├─ Portability: ✅ Can adapt to Unity
├─ Usage: Educational/testing
└─ Notes: CLI tool - not needed in game

velinor/assign_seeds_to_npcs.py
├─ Purpose: Cipher seed assignment
├─ Portability: ⚠️ Development tool
├─ Usage: Content creation
└─ Notes: Not needed for shipped game

velinor/generate_cipher_seeds.py
├─ Purpose: Generate cipher seeds
├─ Portability: ⚠️ Development tool
└─ Notes: One-time use

velinor/generate_seeds_from_corpus.py
├─ Purpose: Generate seeds from text corpus
├─ Portability: ⚠️ Development tool
└─ Notes: Content generation

tools/glyph_tools/
├─ Purpose: Glyph creation & management tools
├─ Portability: ⚠️ Development utilities
├─ Usage: Create new glyphs
└─ Notes: Useful for content creators

velinor/stories/build_story.py
├─ Purpose: Story builder
├─ Portability: ⚠️ Development tool
└─ Notes: Content creation aid

velinor/stories/story_validator.py
├─ Purpose: Validate story structure
├─ Portability: ⚠️ Development tool
├─ Usage: QA/testing
└─ Notes: Run during development
```

---

## DOCUMENTATION INDEX

### Master Documents (Read First)

```
velinor/VELINOR_MASTER_DOC.md ⭐
├─ Lines: ~2000
├─ Authority: Canonical reference
├─ Covers: All game systems, mechanics, logic
├─ Essential: YES
└─ Use: Main implementation guide

velinor/VELINOR_INTEGRATION_CONTRACT.md
├─ Lines: ~500
├─ Purpose: System interface definitions
├─ Covers: How systems communicate
├─ Essential: YES
└─ Use: Architecture planning

velinor/VELINOR_NARRATIVE_SOURCE_MATERIAL.md
├─ Lines: ~1500
├─ Purpose: Story bible & character arcs
├─ Covers: All 6 endings, character development
├─ Essential: YES
└─ Use: Story implementation
```

### Game Systems Documentation

```
velinor/markdowngameinstructions/systems/TONE_STAT_SYSTEM.md
├─ Covers: Complete TONE mechanics
├─ Essential: YES
└─ Use: TraitSystem.cs implementation

velinor/markdowngameinstructions/systems/04_collapse_mechanics.md
├─ Covers: Collapse event mechanics
├─ Essential: YES
└─ Use: Story trigger design

velinor/markdowngameinstructions/systems/05_EMOTIONAL_OS_MECHANICS_INTEGRATION.md
├─ Covers: Emotional OS integration
├─ Essential: YES
└─ Use: System integration reference

velinor/markdowngameinstructions/systems/05_npc_reaction_library.md
├─ Covers: NPC response patterns
├─ Essential: YES
└─ Use: Dialogue system design

velinor/markdowngameinstructions/systems/skill_tree_lying.md
├─ Covers: Skill deception mechanics
├─ Essential: NO
└─ Use: Optional subsystem
```

### Glyph System Documentation

```
velinor/markdowngameinstructions/glyphs/Glyph_Fragments_System.md
├─ Covers: 3-tier cipher explanation
├─ Essential: YES
└─ Use: Glyph unlock system

velinor/markdowngameinstructions/glyphs/BUILDING_DEBATE_GLYPHS_QUICK_REFERENCE.md
├─ Covers: Glyph creation process
├─ Essential: NO (content creation)
└─ Use: For creating new glyphs

velinor/markdowngameinstructions/glyphs/Glyph_Rules.json
├─ Covers: Glyph mechanics rules
├─ Essential: YES
└─ Use: Rules implementation

velinor/markdowngameinstructions/glyphs/Glyph_Organizer_REMNANTS.md
├─ Covers: Remnants integration
├─ Essential: YES
└─ Use: Understand Remnants system
```

### Character & NPC Documentation

```
velinor/markdowngameinstructions/characters/CHARACTER_CREATION_MASTER_REFERENCE.md ⭐
├─ Covers: Player character system
├─ Essential: YES
└─ Use: Player progression system

velinor/markdowngameinstructions/characters/Ravi_Nima_Ophina.md
├─ Covers: Character arc definitions
├─ Essential: YES
└─ Use: Story arc implementation

velinor/markdowngameinstructions/npcs/NPC_SPHERE_SYSTEM.md
├─ Covers: NPC relationship system
├─ Essential: YES
└─ Use: NPC interaction design

velinor/markdowngameinstructions/npcs/MARKETPLACE_NPC_ROSTER.md
├─ Covers: NPC catalog & roles
├─ Essential: YES
└─ Use: NPC definitions

velinor/markdowngameinstructions/npcs/npcs.md
├─ Covers: NPC reference guide
├─ Essential: YES
└─ Use: NPC quick reference
```

### Story & Narrative Documentation

```
velinor/markdowngameinstructions/story/01_NARRATIVE_SPINE_AND_STRUCTURE.md
├─ Covers: Main story structure
├─ Essential: YES
└─ Use: Story architecture

velinor/markdowngameinstructions/story/02_SIX_ENDINGS_EXPLICIT_MAP.md ⭐
├─ Covers: All 6 ending conditions
├─ Essential: YES
└─ Use: Ending system implementation

velinor/markdowngameinstructions/story/story_arcs.md
├─ Covers: Character story arcs
├─ Essential: YES
└─ Use: Narrative design

velinor/markdowngameinstructions/story/the_fourth_layer.md
├─ Covers: Advanced layer mechanics
├─ Essential: YES
└─ Use: Depth system implementation

velinor/markdowngameinstructions/story/VELINOR_SAORI_FINAL_ARC.md
├─ Covers: Final character arc
├─ Essential: YES
└─ Use: Endgame implementation

velinor/markdowngameinstructions/story/overarching_game_story.md
├─ Covers: World structure
├─ Essential: YES
└─ Use: Overall narrative framework
```

### Quick Reference Guides

```
velinor/QUICKSTART.md
├─ Purpose: Quick setup guide
├─ Size: Small
└─ Use: Initial orientation

velinor/STORY_MAP_GUIDE.md
├─ Purpose: Story map reference
├─ Size: Small
└─ Use: Narrative navigation

velinor/README.md
├─ Purpose: Project overview
├─ Size: Medium
└─ Use: Project orientation
```

### Implementation Guides (Streamlit-Specific)

```
velinor/VELINOR_STREAMLIT_IMPLEMENTATION_GUIDE.md
├─ Purpose: Current implementation in Streamlit
├─ Size: ~1000 lines
├─ Use: Reference only (don't port to Unity)
└─ Notes: Understand current architecture

docs/VELINOR_WEB_QUICK_START.md
├─ Purpose: Web implementation reference
├─ Use: Optional - different platform
└─ Notes: Not directly applicable
```

---

## QUICK CATEGORIZATION SUMMARY

### By Effort Type

**TRANSLATE (Direct C# conversion):**
- ✅ All game logic files (engine/*.py)
- ✅ All data model files (*.json, *.csv)
- ✅ All glyph/cipher logic
- ✅ All NPC/dialogue logic (except LLM calls)
- ✅ All story/ending logic

**REWRITE (Framework-specific):**
- 🔴 All Streamlit UI files
- 🔴 Game loop & orchestration
- 🔴 State management
- 🔴 Save/load system
- 🔴 Scene management

**CONVERT (Format change):**
- ⚠️ SVG → PNG (overlays)
- ⚠️ OBJ → FBX (3D models)
- ⚠️ CSV → JSON (if needed)
- ⚠️ SQLite → JSON (databases)

**IMPORT (Direct use):**
- ✅ All image assets (PNG, JPG)
- ✅ All video assets (MP4, WebM)
- ✅ All JSON data files
- ✅ All documentation

**DECIDE:**
- ❓ LLM dialogue integration
  - Option 1: Keep OpenAI/Claude API
  - Option 2: Use local LLM (Ollama)
  - Option 3: Pre-write dialogue trees
- ❓ Audio system
  - Option 1: Add music + SFX
  - Option 2: Skip audio initially
- ❓ Graphics upgrades
  - Option 1: Use existing assets
  - Option 2: Improve visual style

---

## MIGRATION PRIORITY BY FILE

### PHASE 1: Data Layer (Weeks 1-2)

**MUST HAVE:**
1. ✅ glyph_lexicon_rows.json → GlyphData.cs
2. ✅ npc_profiles.json → NpcProfile.cs
3. ✅ cipher_seeds.json → CipherSeed.cs
4. ✅ TONE_STAT_SYSTEM.md (understand mechanics)
5. ✅ VELINOR_MASTER_DOC.md (reference)

### PHASE 2: Core Logic (Weeks 3-6)

**MUST HAVE:**
1. trait_system.py → TraitSystem.cs
2. coherence_calculator.py → CoherenceCalculator.cs
3. glyph_cipher_engine.py → GlyphCipherEngine.cs
4. npc_response_engine.py → NpcResponseEngine.cs
5. ending_system.py → EndingSystem.cs
6. game_state.py → GameState.cs

### PHASE 3: Game Loop (Weeks 7-10)

**MUST HAVE:**
1. orchestrator.py → GameManager.cs
2. core.py → GameCore.cs
3. scene_manager.py → SceneManager.cs (adapt)
4. event_timeline.py → EventTimeline.cs
5. npc_manager.py → NpcManager.cs

### PHASE 4: UI & Rendering (Weeks 11-18)

**MUST HAVE:**
1. streamlit_ui.py → UIManager.cs (REWRITE)
2. streamlit_state.py → GameStateManager.cs (REWRITE)
3. app.py → MainScene.cs (REWRITE)

### PHASE 5: Finishing (Weeks 19-30)

- Save/load system
- Input handling
- Asset integration
- Audio system
- Testing & optimization

---

