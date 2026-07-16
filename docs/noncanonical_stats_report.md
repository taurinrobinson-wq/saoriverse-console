# Non-Canonical Stats Report

**Generated:** 2026-07-09
**Repository:** taurinrobinson-wq/saoriverse-console
**Branch:** main

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Non-Canonical Stats Found** | 23+ instances across 2 major systems |
| **Files Scanned** | 50+ files |
| **Directories Scanned** | `/velinor`, `/Velinor-web`, `/Velinor-Unity`, repo root |
| **Critical Issues** | 2 (Trait System, NPC Perception System) |
| **Scope** | Python code, SQL schemas, markdown documentation |

---

## Canonical Systems (Reference)

### TONE (Player Stance) — 4 Stats Only
- `trust`
- `observation`
- `narrative_presence`
- `empathy`

### REMNANTS (NPC Traits) — 8 Stats Only
- `resolve`
- `empathy`
- `memory`
- `nuance`
- `authority`
- `need`
- `trust`
- `skepticism`

---

## Non-Canonical Systems Identified

### ❌ SYSTEM 1: Trait System (Velinor Core Engine)

**Status:** ACTIVE IN PRODUCTION CODE

**Location:** `velinor/engine/trait_system.py` (lines 7-40)

**Non-Canonical Traits (4 total):**
1. **`EMPATHY`** (0-100 scale)
   - Definition: "Responds to emotional states, chooses comfort over judgment"
   - Current usage: Primary trait in marketplace/dialogue branching
   - Files affected: 8+ Python files

2. **`SKEPTICISM`** (0-100 scale)
   - Definition: "Questions assumptions, holds others accountable, maintains critical distance"
   - Current usage: Primary trait in marketplace/dialogue branching
   - Files affected: 8+ Python files

3. **`INTEGRATION`** (0-100 scale)
   - Definition: "Holds multiple truths simultaneously, advocates for synthesis"
   - Current usage: Primary trait in dialogue responses
   - Files affected: 6+ Python files

4. **`AWARENESS`** (0-100 scale)
   - Definition: "Sees subtext, notices body language, recognizes patterns"
   - Current usage: Primary trait in dialogue responses
   - Files affected: 8+ Python files

**Usage in Code:**

#### velinor/engine/trait_system.py (Lines 31-66)
```python
class TraitType(Enum):
    """Four foundational traits in Velinor's emotional OS"""
    EMPATHY = "empathy"
    SKEPTICISM = "skepticism"
    INTEGRATION = "integration"
    AWARENESS = "awareness"

@dataclass
class TraitProfile:
    empathy: float = 50.0
    skepticism: float = 50.0
    integration: float = 50.0
    awareness: float = 50.0
    coherence: float = 100.0
```

**Issue:** This is a COMPLETE ALTERNATIVE trait system that contradicts the canonical TONE system.

---

### ❌ SYSTEM 2: NPC Perception System

**Status:** ACTIVE IN PRODUCTION CODE

**Location:** `velinor/streamlit_state.py` (lines 100-120)

**Non-Canonical Fields (3 total in NPCPerception dataclass):**

#### velinor/streamlit_state.py (Lines 100-120)
```python
@dataclass
class NPCPerception:
    """How an NPC perceives the player, plus their REMNANTS profile."""
    name: str
    trust: float = 0.0  # -1.0 to 1.0: How much they trust the player
    affinity: float = 0.0  # ❌ NON-CANONICAL: "How much they like the player"
    understanding: float = 0.0  # ❌ NON-CANONICAL: "How well they understand the player"
    emotion: str = "neutral"
    last_interaction: Optional[str] = None
    remnants_profile: RemnantTraits = field(default_factory=RemnantTraits)
```

**Non-Canonical Fields:**

1. **`affinity`** (-1.0 to 1.0 scale)
   - Purpose: "How much they like the player"
   - Context: NPC-level perception metric
   - Files affected: velinor/streamlit_state.py, velinor/streamlit_ui.py

   **Usage in UI (velinor/streamlit_ui.py, line 127):**
   ```python
   f"Affinity: {perception.affinity:+.2f}"
   ```

   **Usage in Manager (velinor/engine/npc_manager.py, line 712):**
   ```python
   "Drossel": 0.1,     # roguelike affinity
   ```

2. **`understanding`** (-1.0 to 1.0 scale)
   - Purpose: "How well they understand the player"
   - Context: NPC-level perception metric
   - Files affected: velinor/streamlit_state.py (definition only)

3. **`trust`** (-1.0 to 1.0 scale)
   - Purpose: "How much they trust the player"
   - Context: NPC-level perception metric (NOT the canonical REMNANTS trait)
   - Issue: Duplicates canonical `trust` but at perception level instead of REMNANTS trait level

---

### ⚠️ SYSTEM 3: Dialogue-Linked Traits (Secondary Usages)

**Locations:**
- `velinor/engine/marketplace_scene.py` — Trait branching with TraitType enum
- `velinor/engine/npc_response_engine.py` — NPC responses keyed to traits
- `velinor/engine/coherence_calculator.py` — Coherence based on trait patterns
- `velinor/tests/test_phase2_integration.py` — Test fixtures using TraitType

**Pattern:** All dialogue branching, NPC response selection, and coherence calculation depend on the 4-trait system (EMPATHY, SKEPTICISM, INTEGRATION, AWARENESS).

---

## Detailed Findings by File

### HIGH PRIORITY

#### 1. velinor/engine/trait_system.py (PRIMARY SOURCE)
- **Lines:** 1-300+
- **Severity:** CRITICAL
- **Issue:** Defines entire non-canonical trait system
- **Traits:** EMPATHY, SKEPTICISM, INTEGRATION, AWARENESS (all 0-100 scale)
- **Affected Systems:** 
  - TraitType enum (line 31)
  - TraitChoice dataclass (line 44)
  - TraitProfile dataclass (line 54)
  - TraitProfiler class (line 77)
- **Recommendation:** Map to TONE system or remove entirely

#### 2. velinor/streamlit_state.py (DATA SCHEMA)
- **Lines:** 100-120
- **Severity:** CRITICAL
- **Issue:** Defines NPCPerception with non-canonical `affinity` and `understanding` fields
- **Non-Canonical Fields:** affinity, understanding, trust (at perception level)
- **Used By:** UI rendering, NPC state management
- **Recommendation:** Replace with REMNANTS trait mappings

#### 3. velinor/engine/marketplace_scene.py (DIALOGUE BRANCHING)
- **Lines:** 1-150+
- **Severity:** HIGH
- **Issue:** All dialogue choices branch on non-canonical TraitType
- **Example (line 87):**
  ```python
  'trait_choice': TraitType.AWARENESS,  # Observing builds awareness
  ```
- **Recommendation:** Convert choices to TONE-based branching

### MEDIUM PRIORITY

#### 4. velinor/engine/npc_response_engine.py
- **Lines:** 19-60
- **Issue:** NPC responses mapped to TraitType traits
- **Non-Canonical Fields:** `preferred_traits`, `uncomfortable_traits` (both List[TraitType])
- **Recommendation:** Map to REMNANTS instead

#### 5. velinor/engine/coherence_calculator.py
- **Lines:** 1-150+
- **Issue:** Coherence calculation based on trait patterns
- **Non-Canonical Usage:** All coherence logic uses TraitType
- **Recommendation:** Refactor to TONE-based coherence or remove

#### 6. velinor/engine/orchestrator.py
- **Lines:** 20, 256+
- **Issue:** Imports and uses TraitProfiler, TraitChoice, TraitType
- **Non-Canonical Usage:** Dialog response generation uses trait patterns
- **Recommendation:** Replace with TONE-based orchestration

#### 7. velinor/engine/npc_manager.py
- **Line:** 712
- **Issue:** NPC initialization with "affinity" field
- **Context:**
  ```python
  "Drossel": 0.1,     # roguelike affinity
  ```
- **Recommendation:** Replace with REMNANTS trait mapping

#### 8. velinor/streamlit_ui.py
- **Line:** 127
- **Issue:** UI display of non-canonical "affinity" stat
- **Context:**
  ```python
  f"Affinity: {perception.affinity:+.2f}"
  ```
- **Recommendation:** Display REMNANTS traits instead

---

## Trait Mapping Analysis

### Current Trait System vs. Canonical TONE

| Non-Canonical Trait | Definition | Closest TONE Equivalent | Closest REMNANTS Traits |
|-------------------|-----------|----------------------|----------------------|
| **EMPATHY** | Responds to emotional states, chooses comfort | `empathy` (TONE) | `empathy`, `need` (REMNANTS) |
| **SKEPTICISM** | Questions assumptions, maintains distance | N/A | `skepticism`, `nuance` (REMNANTS) |
| **INTEGRATION** | Holds multiple truths, advocates synthesis | `observation` or `narrative_presence` | `nuance`, `authority` (REMNANTS) |
| **AWARENESS** | Sees subtext, notices patterns | `observation` (TONE) | `memory`, `nuance` (REMNANTS) |

### NPC Perception Fields vs. Canonical Systems

| Non-Canonical Field | Current Definition | Should Map To |
|-------------------|-------------------|--------------|
| `affinity` | "How much they like the player" | REMNANTS: `empathy` + `need` |
| `understanding` | "How well they understand the player" | REMNANTS: `memory` + `nuance` |
| `trust` (perception level) | "How much they trust the player" | REMNANTS: `trust` |

---

## Files Using Non-Canonical Stats

### Python Files (Trait System Usage)

| File | Line(s) | Usage | Severity |
|------|---------|-------|----------|
| velinor/engine/trait_system.py | 31-66 | Definition | CRITICAL |
| velinor/engine/marketplace_scene.py | 16, 87, 95, 104 | TraitType usage | HIGH |
| velinor/engine/npc_response_engine.py | 19, 55-56 | TraitType list fields | HIGH |
| velinor/engine/coherence_calculator.py | 21, 38, 128 | Trait pattern matching | HIGH |
| velinor/engine/orchestrator.py | 20, 256 | Trait imports/usage | HIGH |
| velinor/engine/npc_manager.py | 15, 712 | Trait docs, affinity | MEDIUM |
| velinor/tests/test_phase2_integration.py | 18, 74, 91 | Test fixtures | MEDIUM |
| velinor/tests/test_phase3_integration.py | 23 | TraitType import | LOW |
| velinor/tests/test_trait_system_foundation.py | 9+ | Trait tests | LOW |

### Data/Schema Files (Perception System Usage)

| File | Line(s) | Field(s) | Severity |
|------|---------|----------|----------|
| velinor/streamlit_state.py | 107-109 | affinity, understanding, trust | CRITICAL |
| velinor/streamlit_ui.py | 127 | affinity display | HIGH |
| velinor/engine/npc_manager.py | 712 | affinity reference | MEDIUM |

### Documentation Files (References)

| File | Issue | Severity |
|------|-------|----------|
| velinor/docs/STREAMLIT_IMPLEMENTATION_SUMMARY.md | Line 46: "Track Trust, Affinity, Understanding" | LOW |
| velinor/STREAMLIT_QUICK_REFERENCE.md | Line 55: "**Affinity** - Liking and comfort" | LOW |
| velinor/STREAMLIT_README.md | Line 12: "how each NPC perceives player trust/affinity/understanding" | LOW |
| velinor/VELINOR_STREAMLIT_IMPLEMENTATION_GUIDE.md | Line 147: affinity_delta parameter | LOW |
| velinor/markdowngameinstructions/IMPLEMENTATION_QUICK_MAP.md | Line 44: "TONE Affinity" | LOW |
| velinor/markdowngameinstructions/npcs/MARKETPLACE_NPC_ROSTER.md | Multiple lines: "TONE Affinity" in NPC descriptions | LOW |

---

## Narrative/Design Usage (Non-Code)

### In Markdown Documentation

**"Affinity" as NPC relationship concept (mostly narrative, not stat):**
- velinor/FOURTH_LAYER_TEMPORAL_ARCHITECTURE.md (line 337)
- velinor/stories/CHOICE_CONSEQUENCES_GUIDE.md (line 4)
- velinor/markdowngameinstructions/npcs/SWAMP_MAZE_SIDEQUEST.md (line 30)

**Status:** These are mostly narrative descriptions, not stat system fields. They describe relationships conceptually, not with numeric values. **LOWER PRIORITY for cleanup.**

---

## Conversion Recommendations

### For Trait System (EMPATHY, SKEPTICISM, INTEGRATION, AWARENESS)

**Option 1: Map to TONE+REMNANTS**
- Player choices currently tied to EMPATHY/SKEPTICISM/INTEGRATION/AWARENESS should be remapped to TONE 4-stat system
- NPC responses tied to these traits should be recalibrated to REMNANTS 8-trait system

**Option 2: Remove Trait System Entirely**
- If not using player trait tracking in current roadmap, remove all TraitType references
- Simplify to TONE choices → REMNANTS effects directly

**Recommendation:** Option 1 (Map to TONE+REMNANTS) preserves design intent while aligning with canonical system.

---

### For NPC Perception System (affinity, understanding)

**Recommended Mapping:**

```
affinity → map to REMNANTS: {empathy: 0.5, need: 0.5}
understanding → map to REMNANTS: {memory: 0.5, nuance: 0.5}
trust (perception) → map to REMNANTS: {trust: 1.0}
```

**Implementation:**
```python
# BEFORE (non-canonical)
perception = NPCPerception(
    name="Ravi",
    trust=0.3,
    affinity=0.2,
    understanding=0.15,
)

# AFTER (canonical)
perception = NPCPerception(
    name="Ravi",
    remnants_profile=RemnantTraits(
        trust=0.3,
        empathy=0.1,
        need=0.1,
        memory=0.075,
        nuance=0.075,
    ),
)
```

---

## Action Items (For Review)

Before proceeding with cleanup, confirm:

- [ ] Trait System (EMPATHY/SKEPTICISM/INTEGRATION/AWARENESS) should be mapped to TONE/REMNANTS (Option 1)?
- [ ] NPC Perception fields (affinity/understanding) should be replaced with REMNANTS traits?
- [ ] Documentation references to "Affinity" in NPC descriptions are narrative-only (not stat system)?
- [ ] All dialogue branching currently keyed to TraitType should be re-keyed to TONE?
- [ ] Test fixtures should be updated to use TONE/REMNANTS after mapping?

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Non-canonical trait types | 4 (EMPATHY, SKEPTICISM, INTEGRATION, AWARENESS) |
| Non-canonical perception fields | 3 (affinity, understanding, + perception-level trust) |
| Python files using trait system | 9 |
| Python files using perception system | 3 |
| Markdown files with references | 8 |
| Total files affected | 20+ |
| Critical issues | 2 |
| High-priority issues | 5 |
| Medium-priority issues | 3 |

---

## Notes for Cleanup Phase

1. **Trait System removal is NOT a simple find-replace** — dialogue branching logic, NPC responses, and coherence calculations are all intertwined with TraitType
2. **Perception system is localized** — primarily in Streamlit UI and state management; should be easier to migrate
3. **Tests will fail after conversion** — all test fixtures using TraitType will need updates
4. **Documentation will need updates** — especially STREAMLIT implementation guides and NPC roster descriptions
5. **Design intent is preserved by mapping** — player choices → trait tracking → NPC responses can be maintained with TONE/REMNANTS equivalents

---

**END REPORT**

**Next Step:** Wait for user approval before proceeding to cleanup phase.
