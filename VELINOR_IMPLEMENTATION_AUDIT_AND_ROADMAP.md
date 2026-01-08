# Velinor: Comprehensive Implementation Audit & Roadmap

**Date:** January 7, 2026  
**Status:** Design complete, partial implementation exists, needs full game build

---

## What Exists (Current Implementation)

### ✅ Backend/Engine Layer

**Location:** `velinor/engine/`

1. **core.py** - Game state management
   - Game states (MENU, LOADING, IN_GAME, DIALOGUE, CHOICE, TRANSITION, GAME_OVER)
   - Player stats system (Courage, Wisdom, Empathy, Resolve, Resonance)
   - Dice rolling mechanics with stat modifiers
   - Location tracking (6 locations defined)
   - Event system for UI callbacks
   - Session management with multiplayer support
   - **Status:** COMPLETE (foundational)

2. **npc_system.py** - NPC behavior & dialogue
   - NPC personality system (role, base_tone, dialogue_templates)
   - FirstPerson orchestrator integration
   - Dialogue history tracking
   - Relationship tracking
   - NPC registry and management
   - **Status:** COMPLETE (but not wired to new design yet)

3. **twine_adapter.py** - Story format loading
   - Twine 2 JSON format parsing
   - SugarCube markup handling
   - Skill check parsing
   - Command extraction (background, dice, NPC)
   - Story progression tracking
   - **Status:** COMPLETE (but not actively used)

4. **orchestrator.py** - Main game loop
   - Game loop controller
   - Player input processing (typed + choices)
   - FirstPerson dialogue generation
   - Save/load functionality
   - Multiplayer session tracking
   - **Status:** COMPLETE (but orchestrating Twine stories)

5. **scene_manager.py** - Scene system
   - SceneModule, SceneRenderer, SceneBuilder
   - Scene progression (DISTANT → APPROACH → CLOSE → DIALOGUE → CHOICES)
   - Asset management (background/foreground layering)
   - Glyph resonance display
   - Player choice capture
   - **Status:** COMPLETE (but not integrated into main game)

### ✅ Frontend/Web Layer

**Location:** `velinor-web/`

- Next.js boilerplate (app, components, data, lib structure)
- Asset pipeline (scripts for syncing images)
- Styling setup (PostCSS)
- **Status:** SKELETON ONLY - no game UI implemented yet

### ✅ Test/Demo Layer

**Location:** `velinor/` root

- **velinor_scenes_test.py** - Streamlit test interface
  - Interactive scene testing
  - Player name input
  - Trust level tracking
  - Dialogue history
  - **Status:** WORKS but demo-only

### ✅ Assets

**Location:** `velinor/`

- `backgrounds/` - ~20 background images (marketplace, desert, forest, etc.)
- `npcs/` - Character artwork
- `overlays/` - UI elements
- `glyph_images/` - Glyph visuals
- `video/` - Character videos
- `bosses/` - Boss artwork

**Status:** COMPREHENSIVE collection

### ✅ Documentation

**Location:** `velinor/markdowngameinstructions/`

- **00_COMPLETE_DESIGN_INTEGRATION_INDEX.md** - Master index (NEW)
- **01_NARRATIVE_SPINE_AND_STRUCTURE.md** - Fixed spine + fluid limbs (NEW)
- **02_SIX_ENDINGS_EXPLICIT_MAP.md** - All 6 endings (NEW)
- **03_MARKETPLACE_DEBATE_SCENE_BRANCHING.md** - Full dialogue tree (NEW)
- **04_BUILDING_COLLAPSE_TIMELINE.md** - Event progression (NEW)
- **05_EMOTIONAL_OS_MECHANICS_INTEGRATION.md** - Trait system (NEW)
- Legacy docs (player_backstory, npc_system, marketplace_scenes, collapse_mechanics, reaction_library)

**Status:** COMPREHENSIVE

---

## What's Missing (Needed for Full Game)

### ❌ Critical: Core Game Loop Integration

**Missing:** Nothing wires the new design to the existing engine

**What's needed:**
1. TraitProfiler - tracks player trait patterns (Empathy/Skepticism/Integration/Awareness)
2. CoherenceCalculator - measures consistency between declared traits and actual choices
3. NPC ResponseEngine - translates trait profiles into dialogue variants
4. StateProgression - maps player choices to BuildingCollapseTimeline states
5. EndingCalculator - determines which of 6 endings is accessible

**Impact:** Game is currently playable but doesn't reflect the narrative design

### ❌ Critical: Marketplace Debate Scene (Act II)

**Missing:** The first major player choice - Malrik/Elenya/Coren debate

**What's needed:**
1. Scene implementation using `scene_manager.py`
2. 3 entry points (direct, faction introduction, mediator introduction)
3. 3 branch paths (synthesis, skepticism, neutral)
4. Dialogue options with trait tags
5. NPC responses based on player trait profile
6. Relationship state updates (Rebuild Potential tracking)
7. Recurrence mechanics (returning to building shows evolution)

**Impact:** Can't test early relationship state or trait tests

### ❌ Critical: Building Collapse Event (Act III)

**Missing:** The mid-game turning point that locks in ending trajectory

**What's needed:**
1. 7-day timeline progression system
2. Visual deterioration sequence (crack → larger cracks → collapse)
3. NPC state transitions (independence → stress → separation/reunion)
4. Player intervention points (Days 1, 2, 3)
5. Three divergent paths with different NPC outcomes
6. Relationship state locking

**Impact:** Can't test how early choices affect endings

### ❌ Critical: Corelink Chamber Scene (Act V)

**Missing:** Final choice between system restart and people-first approach

**What's needed:**
1. Final scene implementation
2. Saori + Velinor presence (reflecting relationship state)
3. Corelink device visuals/interaction
4. System restart vs. abandon choice
5. Ending determination logic
6. Ending cinematics

**Impact:** Game has no actual ending yet

### ❌ Major: Trait-Based Dialogue Variation

**Missing:** NPC dialogue responds to player trait profile

**What's needed:**
1. Dialogue option system with trait tags (already partially in scene_manager)
2. NPC response lookup engine (trait profile → response selection)
3. Dialogue variants for all major scenes
4. Dynamic dialogue that references player's pattern of choices

**Impact:** World feels static, not responsive

### ❌ Major: Save/Load System

**Missing:** Player persistence

**What's needed:**
1. Trait profile serialization
2. Story state checkpoint system
3. Relationship state preservation
4. NPC memory preservation
5. Game-to-web data transmission

**Impact:** Can't resume games

### ❌ Major: Next.js Web Interface

**Missing:** Actual game UI (velinor-web is empty skeleton)

**What's needed:**
1. Game scene renderer component
2. Dialogue choice display
3. Player stats/traits display
4. NPC relationship meters
5. Asset integration (backgrounds, NPCs, glyphs)
6. Navigation/map system
7. Settings/save menu

**Impact:** No playable interface yet

### ❌ Major: API Integration

**Missing:** Backend ↔ Frontend communication

**What's needed:**
1. Game state endpoint (`/api/game/state`)
2. Action submission endpoint (`/api/game/action`)
3. Save endpoint (`/api/game/save`)
4. Load endpoint (`/api/game/load`)
5. Session management endpoints

**Impact:** Web UI can't control game

### ❌ Minor: Optional Side Content

**Missing but not critical:**
- Crime wave investigation arc
- Marketplace faction mechanics
- Side NPC encounters
- Optional dialogue chains
- Achievement/stat system

---

## Current Architecture vs. Needed Architecture

### **Current Architecture**

```
velinor/engine/ (5 modules)
├─ core.py (game state)
├─ npc_system.py (NPC dialogue)
├─ twine_adapter.py (story loading)
├─ orchestrator.py (main loop)
└─ scene_manager.py (scene rendering)

velinor_scenes_test.py (Streamlit demo)

velinor-web/ (Next.js skeleton)
    └─ (no connection to engine)
```

**Problem:** Modules exist but don't interconnect for the new design. Orchestrator handles Twine stories, not emotional OS trait system.

### **Needed Architecture**

```
velinor/engine/ (9 modules)
├─ core.py (game state) ✓
├─ npc_system.py (NPC dialogue) ✓
├─ twine_adapter.py (deprecated or archived)
├─ orchestrator.py (game loop) ✓ (needs modification)
├─ scene_manager.py (scene rendering) ✓
├─ trait_system.py (NEW - trait tracking & patterns)
├─ coherence_calculator.py (NEW - emotional authenticity)
├─ npc_response_engine.py (NEW - trait → dialogue mapping)
├─ state_progression.py (NEW - timeline tracking)
└─ ending_calculator.py (NEW - ending eligibility)

velinor_scenes_test.py (Streamlit demo) ✓
    └─ Connected to trait_system + orchestrator

velinor-web/ (Next.js with API)
    ├─ /api/game/state (NEW)
    ├─ /api/game/action (NEW)
    ├─ /api/game/save (NEW)
    ├─ /api/game/load (NEW)
    └─ Components for rendering game (NEW)
        ├─ SceneRenderer
        ├─ DialogueDisplay
        ├─ TraitMeter
        ├─ NPCRelationship
        └─ Navigation
```

---

## Roadmap: Build Toward Playable Game

### **Phase 1: Trait System Foundation (3-5 days)**

Goal: Get player trait tracking and NPC responsiveness working

**Tasks:**
1. Create `trait_system.py` - track trait patterns, not individual choices
2. Create `coherence_calculator.py` - measure consistency
3. Create `npc_response_engine.py` - map traits to dialogue
4. Modify `orchestrator.py` to use new systems
5. Update Streamlit test interface to show trait profiles
6. Test: Play through marketplace intro with different trait profiles, verify dialogue changes

**Files to create/modify:**
- `velinor/engine/trait_system.py` (NEW)
- `velinor/engine/coherence_calculator.py` (NEW)
- `velinor/engine/npc_response_engine.py` (NEW)
- `velinor/engine/orchestrator.py` (MODIFY)
- `velinor_scenes_test.py` (UPDATE)

**Output:** Game tracking player traits and responding dynamically

---

### **Phase 2: Marketplace Debate Scene (3-5 days)**

Goal: Implement Act II hinge encounter with all dialogue variants

**Tasks:**
1. Create dialogue database for Marketplace Debate (from 03_MARKETPLACE_DEBATE_SCENE_BRANCHING.md)
2. Implement 3 entry points using scene_manager
3. Wire trait tags to dialogue options
4. Implement NPC reactions based on trait profile
5. Track Rebuild Potential state
6. Implement recurrence mechanics (return visits show evolution)
7. Test: Play through all 3 entry points, verify different paths

**Files to create/modify:**
- `velinor/engine/scenes/marketplace_debate.py` (NEW)
- `velinor/engine/dialogue_database.py` (NEW)
- `velinor_scenes_test.py` (UPDATE)

**Output:** First major player choice is testable and variant-rich

---

### **Phase 3: Building Collapse Timeline (4-6 days)**

Goal: Implement mid-game turning point with 7-day progression

**Tasks:**
1. Create `state_progression.py` - timeline tracking system
2. Implement 7-day progression with 3 phases (pre, collapse, aftermath)
3. Create NPC state transitions
4. Implement 3 player intervention paths (synthesist, skeptic, neutral)
5. Create collapse visual sequence
6. Lock in Rebuild Path state (Together/Stalemate/Separation)
7. Test: Play through collapse with different interventions, verify states

**Files to create/modify:**
- `velinor/engine/state_progression.py` (NEW)
- `velinor/engine/scenes/building_collapse.py` (NEW)
- `velinor/engine/orchestrator.py` (UPDATE)
- `velinor_scenes_test.py` (UPDATE)

**Output:** Mid-game turning point locks in ending trajectory

---

### **Phase 4: Ending System (2-3 days)**

Goal: Implement 6 ending logic and final scene

**Tasks:**
1. Create `ending_calculator.py` - determine which ending is accessible
2. Implement final scene (Corelink chamber) using scene_manager
3. Create 6 ending cinematic templates
4. Wire system restart choice to ending state
5. Test: Verify all 6 endings are reachable with appropriate trait profiles

**Files to create/modify:**
- `velinor/engine/ending_calculator.py` (NEW)
- `velinor/engine/scenes/corelink_chamber.py` (NEW)
- `velinor/engine/orchestrator.py` (UPDATE)
- `velinor_scenes_test.py` (UPDATE)

**Output:** Game has complete story arc with 6 valid endings

---

### **Phase 5: Save/Load System (2-3 days)**

Goal: Player persistence

**Tasks:**
1. Extend core.py with serialization
2. Create checkpoint system
3. Implement JSON save format
4. Create load/restore logic
5. Test: Save at key points, verify accurate restoration

**Files to create/modify:**
- `velinor/engine/core.py` (UPDATE)
- `velinor/engine/persistence.py` (NEW)

**Output:** Games can be saved and resumed

---

### **Phase 6: API Layer (3-4 days)**

Goal: Backend ↔ Frontend communication

**Tasks:**
1. Create Flask/FastAPI endpoints for game actions
2. Implement `/api/game/state` - get current game state
3. Implement `/api/game/action` - process player action
4. Implement `/api/game/save` / `/api/game/load`
5. Add session management
6. Test: Web can call endpoints and get responses

**Files to create/modify:**
- `velinor/api.py` (NEW or UPDATE if exists)
- `velinor/engine/orchestrator.py` (UPDATE - add API serialization)

**Output:** Web frontend can communicate with game engine

---

### **Phase 7: Web UI (5-7 days)**

Goal: Playable game interface in Next.js

**Tasks:**
1. Create SceneRenderer component (TSX)
2. Create DialogueDisplay component
3. Create TraitMeter/NPC Relationship components
4. Create Navigation/Map component
5. Integrate asset loading (backgrounds, NPCs, glyphs)
6. Wire to API endpoints
7. Add settings/save menu
8. Test: Full playthrough in web browser

**Files to create/modify:**
- `velinor-web/src/components/SceneRenderer.tsx` (NEW)
- `velinor-web/src/components/DialogueDisplay.tsx` (NEW)
- `velinor-web/src/components/TraitMeter.tsx` (NEW)
- `velinor-web/src/components/NPCRelationship.tsx` (NEW)
- `velinor-web/src/components/Navigation.tsx` (NEW)
- `velinor-web/src/app/page.tsx` (UPDATE)
- `velinor-web/src/lib/api.ts` (NEW)

**Output:** Full game playable in web browser

---

## Timeline Summary

| Phase | Task | Est. Time | Total |
|-------|------|-----------|-------|
| 1 | Trait System | 3-5 days | 3-5 |
| 2 | Marketplace Debate | 3-5 days | 6-10 |
| 3 | Building Collapse | 4-6 days | 10-16 |
| 4 | Endings | 2-3 days | 12-19 |
| 5 | Save/Load | 2-3 days | 14-22 |
| 6 | API Layer | 3-4 days | 17-26 |
| 7 | Web UI | 5-7 days | 22-33 |

**Estimated completion:** 3-5 weeks with one developer

---

## Quick Win Path (If Time Is Limited)

If you want a playable prototype ASAP:

1. **Phase 1 (Trait System)** → Game responds to player traits ✓
2. **Phase 2 (Marketplace Debate)** → First major choice works ✓
3. **Phase 3 (Collapse)** → Story arc is complete ✓
4. **Skip Phase 5 (Save/Load)** → No persistence yet
5. **Phase 6 (API)** → Minimal endpoints only
6. **Phase 7 (Web UI)** → Streamlit demo interface only

**Result:** Full story playable in Streamlit in ~12-16 days

---

## Quality Gates

### By End of Phase 3:
- [ ] Trait system tracks player authenticity
- [ ] Marketplace Debate scene works with 3 paths
- [ ] Building Collapse has 3 divergent outcomes
- [ ] Relationship state locks in ending trajectory

### By End of Phase 4:
- [ ] All 6 endings are reachable
- [ ] Each ending reflects player's trait journey
- [ ] Corelink choice matches player philosophy

### By End of Phase 7:
- [ ] Game is fully playable in web browser
- [ ] Full playthrough takes ~30-45 minutes
- [ ] All systems responsive and working
- [ ] Ready for playtesting

---

## Architectural Principles to Maintain

As you build, keep these in mind:

1. **Trait patterns matter, not individual choices** - NPC responses look at 5-10 previous choices, not just the current one
2. **Coherence is key** - World responds when player is consistent, notices when they're contradictory
3. **Consequences cascade** - A choice in Marketplace Debate directly affects which Building Collapse path is available
4. **Authenticity over optimization** - Multiple valid paths, not a single "correct" path
5. **People matter more than systems** - Everything reinforces that synthesis requires human connection, not infrastructure

---

## Next Immediate Steps

1. Start with Phase 1 - Create trait_system.py
2. Get Streamlit demo showing trait profiles
3. Verify marketplace_intro scene responds to traits
4. Then move to Phase 2 - Marketplace Debate

Want to start there?
