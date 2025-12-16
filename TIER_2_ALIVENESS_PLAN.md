# TIER 2 ALIVENESS - IMPLEMENTATION PLAN

**Status:** Starting Week 2
**Date:** December 4, 2025
**Duration:** 4-6 hours
**Target Performance:** <100ms total (Tier 1+2 combined)
##

## Overview

Tier 2 adds **emotional presence and adaptivity** to responses. While Tier 1 focuses on context and learning, Tier 2 makes the system feel alive by adapting tone, energy, and presence in real-time.
##

## Components to Build

### 1. AttunementLoop
**Purpose:** Real-time emotional synchronization with user

**What it does:**
- Detects shifts in user's emotional tone
- Adjusts response energy to match
- Creates sense of being "with" the user
- Non-intrusive presence

**Key Methods:**

```python
class AttunementLoop:
    def __init__(self)
    def detect_tone_shift(user_input: str, history: list) -> str
    def get_current_attunement() -> dict
```text
```text
```



**Performance:** ~5-7ms
##

### 2. EmotionalReciprocity
**Purpose:** Mirror and build on user's emotional intensity

**What it does:**
- Reflects user's emotional patterns
- Builds conversational momentum
- Shows genuine emotional engagement
- Prevents flat, one-note responses

**Key Methods:**

```python

class EmotionalReciprocity:
    def __init__(self)
    def measure_intensity(user_input: str) -> float  # 0.0 - 1.0
    def match_intensity(response: str, target_intensity: float) -> str

```text
```




**Performance:** ~5-7ms
##

### 3. EmbodiedSimulation
**Purpose:** Create sense of physical presence and embodied interaction

**What it does:**
- Uses presence metaphors (sitting, breathing, reaching)
- Creates spatial awareness
- Suggests physical attention and care
- Grounds abstract emotions in body

**Key Methods:**

```python
class EmbodiedSimulation:
    def __init__(self)
    def suggest_presence(context: dict) -> str
    def add_embodied_language(response: str) -> str
```text
```text
```



**Performance:** ~3-5ms
##

### 4. EnergyTracker
**Purpose:** Maintain and adapt conversation energy levels

**What it does:**
- Tracks conversation phase (opening, deepening, closing)
- Monitors user fatigue or engagement
- Suggests pacing changes
- Prevents energy crashes

**Key Methods:**

```python

class EnergyTracker:
    def __init__(self)
    def get_conversation_phase(history: list) -> str
    def detect_fatigue(history: list) -> bool
    def calculate_optimal_pacing(phase: str) -> dict

```text
```




**Performance:** ~3-5ms
##

## Architecture

```
Tier 2: Aliveness Layer
    ↓
AttunementLoop (detect tone shift) → 5-7ms
    ↓
EmotionalReciprocity (measure & match intensity) → 5-7ms
    ↓
EmbodiedSimulation (add presence) → 3-5ms
    ↓
EnergyTracker (maintain pacing) → 3-5ms
    ↓
```text
```text
```



**Total Tier 2 Processing:** ~17-27ms
**Tier 1 + Tier 2 Total:** ~40ms + 20ms = ~60ms ✅
##

## Implementation Steps

### Step 1: Create tier2_aliveness.py (2-3 hours)
**File:** `src/emotional_os/tier2_aliveness.py`

**Structure:**

```python


# Imports
from emotional_os.core.lexicon_learner import LexiconLearner
from emotional_os.core.signal_parser import parse_signals

# ... other imports

# AttunementLoop class (80 lines)
class AttunementLoop:
    def __init__(self): ...

# EmotionalReciprocity class (80 lines)
class EmotionalReciprocity:
    def __init__(self): ...

# EmbodiedSimulation class (80 lines)
class EmbodiedSimulation:
    def __init__(self): ...

# EnergyTracker class (80 lines)
class EnergyTracker:
    def __init__(self): ...

# Tier2Aliveness orchestrator (100 lines)
class Tier2Aliveness:
    def __init__(self): ...

```text
```




**Target:** ~420 lines total

### Step 2: Create test_tier2_aliveness.py (1-2 hours)
**File:** `tests/test_tier2_aliveness.py`

**Test Coverage:**
- [ ] Tone shift detection
- [ ] Intensity matching
- [ ] Embodied language addition
- [ ] Energy tracking
- [ ] Combined pipeline
- [ ] Performance <30ms
- [ ] Error handling

**Target:** ~200 lines, 8-10 tests

### Step 3: Integrate into response handler (30 min)
**Files:**
- `src/emotional_os/deploy/modules/ui_components/response_handler.py`

**Changes:**

```python

# After Tier 1 processing:
tier2 = st.session_state.get("tier2_aliveness")
if tier2:
    response, metrics = tier2.process_for_aliveness(
        user_input, response, history
```text
```text
```



### Step 4: Add to session manager (20 min)
**File:** `src/emotional_os/deploy/modules/ui_components/session_manager.py`

**Changes:**

```python

def _ensure_tier2_aliveness():
    """Initialize Tier 2 Aliveness components."""
    if "tier2_aliveness" not in st.session_state:
        try:
            from src.emotional_os.tier2_aliveness import Tier2Aliveness
            tier2 = Tier2Aliveness()
            st.session_state["tier2_aliveness"] = tier2
        except Exception as e:
            logger.warning(f"Tier 2 initialization failed: {e}")

```text
```




### Step 5: Test and validate (30 min)
- Run pytest: `tests/test_tier2_aliveness.py`
- Run manual tests with real conversations
- Verify <100ms total time
- Check for no new errors
##

## Performance Budget

```
Tier 1 (Complete):      ~40ms  │████░░░░░░░░░░░░░░░│ 40%
Tier 2 (New):          ~20ms  │██░░░░░░░░░░░░░░░░│ 20%
─────────────────────────────────
Total:                 ~60ms  │██████░░░░░░░░░░░│ 60%
```text
```text
```


##

## Key Design Decisions

### 1. Non-Intrusive
- Adjustments should feel natural
- No weird tone shifts
- Subtle energy matching
- Imperceptible to user

### 2. Context-Aware
- Uses conversation history
- Considers session history
- Respects user preferences
- Adapts to individual patterns

### 3. Graceful Degradation
- Each component has fallback
- Missing dependencies don't break system
- Can disable Tier 2, system still works
- Performance doesn't degrade

### 4. Fast & Efficient
- All heuristic-based (no ML models)
- <30ms per component
- <100ms combined with Tier 1
- Minimal memory overhead
##

## Testing Strategy

### Unit Tests

```python

def test_tone_shift_detection():
    # Test AttunementLoop.detect_tone_shift()

def test_intensity_matching():
    # Test EmotionalReciprocity.match_intensity()

def test_embodied_language():
    # Test EmbodiedSimulation.add_embodied_language()

def test_energy_tracking():

```text
```




### Integration Tests

```python
def test_tier2_with_tier1():
    # Test Tier 1 + Tier 2 combined
    # Verify performance <100ms

def test_aliveness_improves_responses():
```text
```text
```



### Manual Tests
1. Have natural conversation (10+ exchanges)
2. Notice if responses feel more "alive"
3. Check for tone consistency
4. Verify energy pacing
5. Look for embodied language
##

## Success Metrics

### Performance
- [ ] Each component <7ms
- [ ] Total Tier 2 <30ms
- [ ] Tier 1+2 <70ms (10ms headroom)
- [ ] No performance degradation

### Quality
- [ ] Responses feel more present
- [ ] Tone shifts are natural
- [ ] Energy matching improves engagement
- [ ] Embodied language feels authentic

### Testing
- [ ] 8-10 tests all passing
- [ ] >90% code coverage
- [ ] Full error handling
- [ ] Graceful fallbacks
##

## Files to Create/Modify

### New Files
- `src/emotional_os/tier2_aliveness.py` (420 lines)
- `tests/test_tier2_aliveness.py` (200 lines)

### Modified Files
- `src/emotional_os/deploy/modules/ui_components/response_handler.py` (+20 lines)
- `src/emotional_os/deploy/modules/ui_components/session_manager.py` (+20 lines)
##

## Git Strategy

**Commit 1:** tier2_aliveness.py + tests

```bash

git commit -m "feat: Tier 2 Aliveness - AttunementLoop, Reciprocity, Embodiment

- Implement AttunementLoop for tone synchronization
- Implement EmotionalReciprocity for intensity matching
- Implement EmbodiedSimulation for physical presence
- Implement EnergyTracker for pacing management
- Create Tier2Aliveness orchestrator class
- Create comprehensive test suite (8-10 tests)

```text
```




**Commit 2:** Integration into response handler and session manager

```bash
git commit -m "feat: Integrate Tier 2 Aliveness into response pipeline

- Add Tier 2 to response_handler.py
- Add session initialization to session_manager.py
- Verify imports and no errors
- Test combined Tier 1+2 pipeline
- Performance <70ms for full pipeline"
```



##

## Timeline

- **Hour 1-2:** Create Tier2Aliveness class (420 lines)
- **Hour 2-3:** Create test suite (200 lines)
- **Hour 3-4:** Run tests and fix issues
- **Hour 4-5:** Integrate into response handler & session manager
- **Hour 5-6:** Manual testing and validation

**Total: 4-6 hours**
##

## Rollback Plan

If Tier 2 causes issues:
1. Comment out Tier 2 call in response_handler.py
2. System reverts to Tier 1 only
3. Performance returns to ~50ms
4. No data loss or user impact
##

## What's After Tier 2

Once Tier 2 is complete and integrated:

### Tier 3 (Week 3-4)
- Poetic Consciousness
- Saori Layer
- Generative Tension

### Tier 4 (Optional Week 5+)
- Dream Engine
- Temporal Memory
- Long-term Learning
##

## Ready to Begin?

✓ All previous changes committed
✓ Tier 1 fully integrated and tested
✓ Performance baseline established (~40ms)
✓ Next step: Build tier2_aliveness.py

**Let's start!**
##

Date: December 4, 2025
Status: Ready to implement
Estimated completion: December 4-5, 2025
