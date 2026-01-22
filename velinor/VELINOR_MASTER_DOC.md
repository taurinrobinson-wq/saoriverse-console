# VELINOR_MASTER_DOC.md

**Authoritative Source for Game Logic, Emotional OS, and Engine Architecture**

**Last Updated:** January 20, 2026  
**Status:** Canonical reference — single source of truth for Velinor game systems  
**Scope:** Game logic, narrative OS, glyph system, NPCs, traits, story structure, engine phases

> **Note:** This document defines the **game world and its rules**.  
> For how the web frontend **renders** this world, see `../velinor-web/VELINOR_WEB_MASTER_DOC.md`  
> For the **contract between systems**, see `VELINOR_INTEGRATION_CONTRACT.md` (shared in both repos)

---

## Quick Navigation

- [What is Velinor?](#what-is-velinor) — Core concept and design
- [Emotional OS](#emotional-os) — TONE stats, coherence, emotional gates, influence
- [Glyph System](#glyph-system) — 118 glyphs, 3-tier cipher, emotional encoding
- [Trait System](#trait-system) — 21 core traits, emotional gates, NPC influence
- [Story Structure](#story-structure) — 6 endings, passages, choices, collapse event
- [NPCs & Characters](#npcs--characters) — 21 characters, profiles, response logic
- [Engine Architecture](#engine-architecture) — Phases, systems, data flow
- [File Reference](#file-reference) — What each file does, how to modify
- [Adding Game Content](#adding-game-content) — Glyphs, NPCs, traits, endings
- [Testing & Validation](#testing--validation) — Test organization, running tests

---

## What is Velinor?

### Core Concept

**Velinor** is an emotional narrative game engine that:

1. **Tracks emotional state** through TONE stats (Empathy, Skepticism, Integration, Awareness)
2. **Uses glyphs** as a 3-tier cipher to encode emotional meaning into dialogue
3. **Models NPC responses** based on coherence and emotional gates
4. **Presents 6 distinct endings** based on player emotional trajectory
5. **Supports save/load** for session persistence and exploration

### Design Principle

Every game system serves **emotional coherence**:
- Glyphs encode emotional intent
- Traits define emotional boundaries
- NPCs respond based on emotional alignment
- Endings reflect emotional arc completion

---

## Emotional OS

### TONE Stats (4-dimensional emotional space)

**Files:**
- `velinor/engine/trait_system.py` — TONE tracking and modification
- `velinor/data/trait_profiles.json` — Trait definitions and TONE impacts

**The Four Dimensions:**

| Stat | Range | Meaning | Increases When |
|------|-------|---------|-----------------|
| **Empathy** | 0-100 | Compassion, emotional openness | Choosing caring responses |
| **Skepticism** | 0-100 | Critical thinking, questioning | Choosing analytical responses |
| **Integration** | 0-100 | Acceptance, wholeness | Pursuing coherent paths |
| **Awareness** | 0-100 | Self-understanding | Reflecting on emotional state |

**Mechanics:**
- Each player choice modifies one or more TONE stats
- NPCs have emotional gates that trigger when TONE meets thresholds
- Coherence is calculated as harmony between TONE stats
- Endings are determined by TONE state at game completion

### Coherence System

**Formula:** Harmony between TONE stats (0-100 scale)

```python
coherence = 100 - average_deviation(empathy, skepticism, integration, awareness)
```

**Meaning:**
- **High coherence (80-100):** Emotional alignment, strong sense of self
- **Medium coherence (40-80):** Mixed signals, growing understanding
- **Low coherence (0-40):** Conflict, internal contradiction

**Impact:**
- Higher coherence unlocks deeper NPC responses
- Low coherence triggers doubt/crisis responses
- Coherence progression determines which ending is reachable

**Files to Modify:**
- `velinor/engine/coherence_calculator.py` — Coherence calculation logic
- `velinor/engine/npc_response_engine.py` — How coherence affects NPC dialogue

### Emotional Gates

**Definition:** Threshold conditions that unlock NPC dialogue branches

**Gate Types:**

1. **TONE-based gates** — Require minimum stat level
   - `empathy >= 70` → NPC responds with vulnerability
   - `skepticism >= 60` → NPC respects critical questions

2. **Coherence gates** — Require emotional alignment
   - `coherence >= 80` → NPC reveals deep truth
   - `coherence < 30` → NPC expresses concern

3. **Influence gates** — Based on NPC-specific relationship
   - `influence[npc_name] >= 0.7` → NPC trusts player
   - `influence[npc_name] < 0.3` → NPC withdraws

**Files to Modify:**
- `velinor/data/npc_profiles.json` — Gate definitions per NPC
- `velinor/engine/npc_response_engine.py` — Gate evaluation logic

### Influence System

**Definition:** Individual relationship tracking with each NPC (0-1 scale)

**Mechanics:**
- Starts at 0.5 (neutral) for each NPC
- Increases when player choices align with NPC values
- Decreases when player contradicts NPC emotional stance
- Influences dialogue selection, NPC mood, and ending variations

**Files to Modify:**
- `velinor/data/influence_map.json` — NPC relationships and influence rules
- `velinor/engine/npc_response_engine.py` — Influence calculation on choice impact

---

## Glyph System

### Overview

**118 glyphs** organized in a **3-tier cipher architecture**:

```
Tier 1 (Hint Layer)      → Surface emotional signal
         ↓
Tier 2 (Context Layer)   → Narrative context
         ↓
Tier 3 (Plaintext Layer) → Decoded meaning
```

**Purpose:** Allow players to discover emotional layers through interaction

### Glyph Categories

**75 Base Glyphs** — Core emotional vocabulary:
- Comfort (12) — Solace, reassurance, presence
- Crisis (12) — Urgency, fear, overwhelm
- Growth (12) — Learning, change, perspective
- Connection (12) — Relationship, empathy, resonance
- Understanding (12) — Clarity, insight, realization
- Transcendence (3) — Completion, transformation, transcendence

**36 Fragment Glyphs** — Emotional modifiers and combinations:
- Intensity variants (18) — Strong vs. subtle versions
- Temporal frames (9) — Past, present, future perspectives
- Relational contexts (9) — Self, other, collective framings

**7 Transcendence Glyphs** — Ending-related, special cipher rules:
- Unlock only in specific emotional states
- Reveal hidden story layers
- Lead to rare/premium endings

**NEW (Post-2.0):**
- **Glyph #76 (Shared Dawn)** — Joy/Presence hybrid. Catalytic tryst between Sera & Korrin. Unlocks Grounded Presence tool. Gated on Empathy 50+/Trust 50+, Coherence 50+, multi-NPC encounters.
- **Glyph of Severed Covenant** — Ache/Legacy hybrid. Malrik & Elenya pre-collapse bond revelation. Unlocks alternative ending branches. Gated on Coherence 70+, Empathy 70+/Integration 70+, 4+ encounters with each NPC.

### 3-Tier Cipher

**Example:**

```
Glyph: VELINOR-COMFORT-001

Tier 1 (Hint):
  Symbol: ◈
  Color: Soft blue
  Player sees: "Something soothing..."

Tier 2 (Context):
  After interaction: "Presence. Someone is here with you."
  Revealed through dialogue choice

Tier 3 (Plaintext):
  In ending: "The promise of companionship held true."
  Full emotional meaning unlocked
```

**Files:**
- `velinor/data/glyphs_complete.json` — All 118 glyph definitions (hint, context, plaintext)
- `velinor/engine/glyph_cipher_engine.py` — Cipher logic and tier unlocking
- `velinor/docs/GLYPH_CIPHER_3_TIER_INTEGRATION.md` — Detailed glyph semantics

**How to Add/Modify:**
1. Edit `glyphs_complete.json` — add glyph entry with all 3 tiers
2. Assign category (base/fragment/transcendence)
3. Set emotional associations in tier 2 and 3
4. Test via `test_glyph_cipher.py`

---

## Trait System

### 21 Core Traits

**Definition:** Emotional/psychological attributes that define character and NPC behavior

**Trait Categories:**

| Category | Traits | Purpose |
|----------|--------|---------|
| **Emotional** | Empathy, Vulnerability, Honesty | How NPCs process emotion |
| **Relational** | Trust, Reciprocity, Presence | How NPCs connect |
| **Cognitive** | Awareness, Insight, Acceptance | How NPCs understand |
| **Existential** | Mortality, Purpose, Transcendence | How NPCs face meaning |

**Each Trait:**
- Has emotional gate requirements
- Affects NPC response selection
- Influences influence gain/loss on choices
- Links to specific glyphs

**Files:**
- `velinor/data/trait_profiles.json` — All 21 trait definitions
- `velinor/engine/trait_system.py` — Trait evaluation logic
- `velinor/docs/DIALOGUE_SYSTEM_COMPLETE_INDEX.md` — Trait-to-dialogue mapping

**How to Add/Modify:**
1. Edit `trait_profiles.json` — add trait with emotional gates
2. Link to relevant glyphs
3. Define influence impact on NPC choices
4. Test with `test_trait_system_foundation.py`

---

## Story Structure

### 6 Endings

Each ending represents a different emotional resolution:

| Ending | Emotional State | TONE Profile | Outcome |
|--------|-----------------|------|---------|
| **Transcendence** | Maximum coherence + all TONE balanced | E:90+, S:85+, I:95+, A:90+ | Rare, requires 7 transcendence glyphs |
| **Integration** | High coherence, balanced approach | E:75+, S:75+, I:80+, A:75+ | Player achieves wholeness |
| **Compassion** | High empathy, low skepticism | E:85+, S:30-, I:70+, A:70+ | Player chooses connection |
| **Wisdom** | High skepticism and awareness | E:50-, S:85+, I:75+, A:85+ | Player chooses understanding |
| **Survival** | Mixed state, low coherence | Variable | Player persists despite confusion |
| **Dissolution** | Extreme incoherence | All TONE divergent, coherence <30 | Player loses sense of self |

**Ending Determination:**
- Calculated at game completion based on final TONE state and paths taken
- Each ending has unique final passage and glyph revelations
- Replay with different choices → different emotional arcs → different endings

**Files:**
- `velinor/stories/story_definitions.py` — All 6 endings and final passages
- `velinor/engine/ending_system.py` — Ending calculation logic
- `velinor/engine/event_timeline.py` — Collapse event timing
- `velinor/docs/STORY_MAP_VELINOR.md` — Story structure and passage map

### Collapse Event

**Definition:** Central dramatic pivot point where player must make critical choice

**Mechanics:**
- Triggers mid-game when coherence crosses threshold
- Forces choice between emotional paths
- Affects all remaining NPC interactions
- Determines which endings remain reachable

**Impact:**
- High coherence before collapse → access to transcendence/integration endings
- Low coherence → survival/dissolution endings become primary
- No reload possible during collapse (forces commitment)

**Files to Modify:**
- `velinor/data/event_timeline.json` — Collapse trigger conditions
- `velinor/engine/event_timeline.py` — Collapse event logic
- `velinor/stories/story_definitions.py` — Collapse passage

### Passages & Choices

**Structure:**

```python
passage = {
  "id": "passage-001",
  "type": "narration|dialogue|choice_point",
  "content": "Story text with glyphs",
  "npc": "character_name (optional)",
  "choices": [
    {
      "id": "choice-001",
      "text": "Player action",
      "tone_impact": {"empathy": +10, "skepticism": -5},
      "influence_impact": {"character_name": +0.1},
      "gates": [{"type": "empathy", "value": 60}],
      "next_passage": "passage-002"
    }
  ]
}
```

**Files:**
- `velinor/stories/story_definitions.py` — All passages and choices
- `velinor/engine/passage_manager.py` — Passage loading and navigation

**How to Add/Modify:**
1. Edit `story_definitions.py` — add passage with choices
2. Set `tone_impact` and `influence_impact` values
3. Define `gates` for conditional content
4. Link to glyphs in passage content
5. Test with `test_passage_manager.py`

---

## NPCs & Characters

### 21 Named Characters

**Files:**
- `velinor/data/npc_profiles.json` — All NPC metadata, gates, response pools
- `velinor/engine/npc_manager.py` — NPC state and response selection
- `velinor/engine/npc_response_engine.py` — Dialogue generation logic
- `velinor/npcs/` — Character portrait images (PNG)

### NPC Profile Structure

```json
{
  "name": "Saori",
  "archetype": "Guide",
  "traits": ["Awareness", "Insight", "Vulnerability"],
  "emotional_stance": {
    "preferred_empathy": 0.8,
    "prefers_vulnerability": true
  },
  "gates": {
    "trust_gate": {"type": "influence", "value": 0.7},
    "revelation_gate": {"type": "coherence", "value": 80},
    "crisis_gate": {"type": "empathy", "value": 50}
  },
  "response_pools": {
    "greeting": ["pool_greeting_001", ...],
    "crisis": ["pool_crisis_001", ...]
  }
}
```

### NPC Response Engine

**Process:**
1. Get current game state (TONE, coherence, influence with NPC)
2. Evaluate emotional gates
3. Select appropriate response pool
4. Generate response with glyphs and trait activation
5. Calculate influence impact

**Files to Modify:**
- `velinor/engine/npc_response_engine.py` — Response selection logic
- `velinor/data/npc_profiles.json` — NPC gates and response pools

**How to Add/Modify:**
1. Edit `npc_profiles.json` — add NPC entry
2. Define traits, emotional stance, gates
3. Create response pools with trait-tagged responses
4. Test with `test_npc_manager.py`

**NEW (Post-2.0) NPC Updates:**

**Sera & Korrin (Shared Dawn Arc)**:
- New joint glyph encounter (#76): Market courtyard at dawn, post-tryst scene
- New tools: Grounded Presence (Sera/Korrin tool, requires Presence 70+), Sacred Silence (Korrin tool, requires high influence post-Shared Dawn)
- Influence mechanics: Sera/Korrin each gain +0.20 if player honors silence, -0.15 if exposed
- Dialogue: Private reflection branches unlock post-encounter for each NPC
- See `markdowngameinstructions/npcs/MARKETPLACE_NPC_ROSTER.md` (Sera lines 128+, Korrin lines 240+) for full profiles

**Malrik & Elenya (Severed Bond Arc)**:
- Optional revelation arc gated on Coherence 70+, Empathy 70+/Integration 70+, 4+ encounters each
- Glyph of Severed Covenant unlocks post-revelation
- Both NPCs show deeper vulnerability; Malrik admits past connection, Elenya reveals deliberate memory severance
- Influence: Malrik +0.25, Elenya +0.25 (if encounter facilitated)
- Integration with ending branches: Alternative final passage where both contribute to player's emotional resolution
- See `markdowngameinstructions/story/story_arcs.md` ("The Severed Bond" section) for full encounter sequence

---

## Engine Architecture

### Phase Structure (5 phases)

**Phase 1: Trait Introduction** (Early game)
- Player meets NPCs, learns about trait system
- Low-stakes choices build baseline TONE
- Glyphs introduced gradually

**Phase 2: Marketplace** (Mid-game)
- Player interacts with multiple NPCs
- Complex choice chains emerge
- Influence system becomes visible
- NEW: Sera/Korrin Shared Dawn encounter becomes available (mid-game potential)

**Phase 3: Collapse** (Pivot)
- Central dramatic event forces commitment
- Coherence pressure increases
- Endings become visible in possibility space
- NEW: Optional Malrik/Elenya revelation arc becomes available (coherence-dependent)

**Phase 4: Endings** (Late game)
- Player pursues specific emotional arc
- Final NPC interactions reveal deep truths
- Glyphs reach transcendence tier

**Phase 5: Persistence** (Meta-layer)
- Save/load system enables exploration
- Multiple playthroughs reveal alternative arcs
- New Game+ features unlock

**Files:**
- `velinor/engine/orchestrator.py` — Phase management
- `velinor/engine/core.py` — Main game loop

### Core Systems

```
Orchestrator (phase & game loop)
    ↓
PassageManager (load story content)
    ↓
NpcResponseEngine (generate dialogue)
    ↓
TraitSystem (evaluate gates)
    ↓
CoherenceCalculator (compute emotional state)
    ↓
GlyphCipherEngine (encode/decode glyphs)
    ↓
SaveSystem (persist state)
```

**Main Files:**
- `velinor/engine/orchestrator.py` — Main game orchestration
- `velinor/engine/core.py` — Core game mechanics
- `velinor/engine/passage_manager.py` — Story content loading
- `velinor/engine/npc_response_engine.py` — Dialogue generation
- `velinor/engine/coherence_calculator.py` — Emotional state
- `velinor/engine/glyph_cipher_engine.py` — Glyph mechanics
- `velinor/engine/save_system.py` — Persistence

### API Endpoints

**Reference:** See `VELINOR_INTEGRATION_CONTRACT.md` for full API spec

Quick reference:
- `POST /api/game/start` — Initialize game
- `POST /api/game/action` — Process player choice
- `GET /api/game/status` — Get current state
- `POST /api/game/save` — Save to slot
- `GET /api/game/load` — Load from slot

---

## File Reference

### Core Engine Files

| File | Purpose | Modify for |
|------|---------|-----------|
| `engine/orchestrator.py` | Main game loop, phase management | Phase logic, game flow |
| `engine/core.py` | Game initialization, main mechanics | Core rule changes |
| `engine/passage_manager.py` | Load/navigate story | Story structure, passage logic |
| `engine/npc_response_engine.py` | Generate NPC dialogue | NPC behavior, response rules |
| `engine/trait_system.py` | Track and evaluate traits | Trait mechanics, gates |
| `engine/coherence_calculator.py` | Calculate emotional harmony | Coherence formula |
| `engine/glyph_cipher_engine.py` | Encode/decode glyphs | Cipher mechanics, tier unlocking |
| `engine/ending_system.py` | Determine final ending | Ending logic, thresholds |
| `engine/event_timeline.py` | Manage collapse event | Event timing, triggers |
| `engine/save_system.py` | Save/load persistence | Save slots, serialization |
| `engine/api_handler.py` | REST API endpoints | API contract changes |

### Data Files

| File | Purpose | Contains |
|------|---------|----------|
| `data/glyphs_complete.json` | All 118 glyphs | 3-tier cipher definitions |
| `data/npc_profiles.json` | All 21 NPCs | NPC metadata, gates, responses |
| `data/trait_profiles.json` | All 21 traits | Trait definitions, impacts |
| `data/influence_map.json` | NPC relationships | Influence rules |

### Story Files

| File | Purpose | Contains |
|------|---------|----------|
| `stories/story_definitions.py` | All story content | 6 endings, passages, choices |
| `markdowngameinstructions/` | Design docs | Story design principles |

### Test Files

| Location | Purpose |
|----------|---------|
| `tests/test_orchestrator.py` | Main game loop tests |
| `tests/test_trait_system_foundation.py` | Trait mechanics |
| `tests/test_glyph_cipher.py` | Glyph cipher logic |
| `tests/test_npc_manager.py` | NPC system |
| `tests/test_suicidality_protocol.py` | Safety gates |
| `tests/test_phase*_*.py` | Phase-specific tests |
| `tests/test_ending_system.py` | Ending determination |

---

## Adding Game Content

### Adding a New Glyph

1. **Edit** `velinor/data/glyphs_complete.json`
   ```json
   {
     "id": "glyph_new_001",
     "name": "Your Glyph Name",
     "category": "comfort|crisis|growth|connection|understanding|transcendence",
     "tier1_hint": "Short visual/emotional hint",
     "tier1_color": "#hexcolor",
     "tier2_context": "Narrative context revealed mid-game",
     "tier3_plaintext": "Full meaning revealed in ending",
     "associated_traits": ["Trait1", "Trait2"],
     "influence_threshold": 0.6
   }
   ```

2. **Reference** in story passages via `{{glyph:glyph_new_001}}`

3. **Test** with `pytest tests/test_glyph_cipher.py`

### Adding a New NPC

1. **Add portrait** to `velinor/npcs/{npc_name}.png`

2. **Edit** `velinor/data/npc_profiles.json`
   ```json
   {
     "name": "NewNPC",
     "archetype": "Guide|Challenger|Mirror|etc",
     "traits": ["Trait1", "Trait2"],
     "emotional_stance": {"preferred_empathy": 0.7},
     "gates": { ... },
     "response_pools": { ... }
   }
   ```

3. **Create responses** in `velinor/stories/story_definitions.py`

4. **Test** with `pytest tests/test_npc_manager.py`

### Adding a New Ending

1. **Edit** `velinor/stories/story_definitions.py` — add to ENDINGS dict
   ```python
   "ending_name": {
     "name": "Ending Title",
     "tone_requirements": {"empathy": 80, ...},
     "coherence_minimum": 75,
     "description": "Short description",
     "final_passage": "passage_id",
     "reveals_glyphs": ["glyph_id1", ...]
   }
   ```

2. **Update** `velinor/engine/ending_system.py` — add condition logic

3. **Test** with `pytest tests/test_ending_system.py`

### Adding a New Trait

1. **Edit** `velinor/data/trait_profiles.json`
   ```json
   {
     "name": "NewTrait",
     "category": "emotional|relational|cognitive|existential",
     "description": "What this trait represents",
     "gate_requirements": {"empathy": 50},
     "influence_multiplier": 1.2
   }
   ```

2. **Reference** in NPC response pools

3. **Test** with `pytest tests/test_trait_system_foundation.py`

---

## Testing & Validation

### Test Organization

**By System:**
- `test_orchestrator.py` — Main game loop
- `test_trait_system_foundation.py` — Trait mechanics
- `test_glyph_cipher.py` — Glyph system
- `test_npc_manager.py` — NPC behavior
- `test_coherence_calculator.py` — Emotional state
- `test_ending_system.py` — Endings
- `test_suicidality_protocol.py` — Safety

**By Phase:**
- `test_phase1_integration.py` — Phase 1 tests
- `test_phase2_integration.py` — Phase 2 tests
- etc.

**Integration:**
- `test_comprehensive_integration.py` — Full game flow

### Running Tests

```bash
# All tests
pytest velinor/tests/

# Specific test file
pytest velinor/tests/test_npc_manager.py

# With coverage
pytest velinor/tests/ --cov=velinor/engine

# Single test
pytest velinor/tests/test_trait_system_foundation.py::test_trait_gate_evaluation
```

### Adding a Test

Create `velinor/tests/test_your_feature.py`:
```python
import pytest
from velinor.engine.your_module import YourClass

def test_your_feature():
    obj = YourClass()
    result = obj.do_something()
    assert result == expected_value
```

---

## How to Use This Document

### I want to understand...
- **How glyphs work** → [Glyph System](#glyph-system)
- **How NPCs decide what to say** → [NPC Response Engine](#npcs--characters)
- **How endings are determined** → [Story Structure](#story-structure)
- **How player choices affect the game** → [TONE Stats](#tone-stats-4-dimensional-emotional-space)

### I want to modify...
- **NPC dialogue** → Edit `npc_profiles.json` + `story_definitions.py`
- **A trait's impact** → Edit `trait_profiles.json`
- **The collapse event** → Edit `event_timeline.json` + `event_timeline.py`
- **An ending** → Edit `story_definitions.py` + `ending_system.py`

### I want to add...
- **A new glyph** → Follow [Adding a New Glyph](#adding-a-new-glyph)
- **A new NPC** → Follow [Adding a New NPC](#adding-a-new-npc)
- **A new ending** → Follow [Adding a New Ending](#adding-a-new-ending)
- **A new trait** → Follow [Adding a New Trait](#adding-a-new-trait)

---

**Last Updated:** January 20, 2026  
**Maintained by:** Velinor Development Team  
**Status:** Production-ready, actively maintained
