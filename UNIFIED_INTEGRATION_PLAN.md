# UNIFIED INTEGRATION PLAN - Analysis Complete + Comprehensive Modules

# Performance-First, Locally-Hosted, Compassionate Responses

**Status:** Ready to implement
**Timeline:** 4 weeks, incremental rollout
**Response Target:** < 100ms (local only, no API calls)
**Architecture:** Caring + Dynamic + Presient + Relevant
##

## PHASE OVERVIEW & TIMELINE

### WEEK 1: Tier 1 - Foundation (3-5 hours)
**Goal:** Fast foundation enabling context + compassionate openings
**Modules:** ConversationMemory, LexiconLearner, basic Sanctuary

### WEEK 2: Tier 2 - Aliveness (4-6 hours)
**Goal:** Dynamic presence enabling adaptive tone + energy cycles
**Modules:** Presence layer, emotional reciprocity, signal enrichment

### WEEK 3-4: Tier 3 - Depth (6-8 hours)
**Goal:** Poetic understanding with multiple voices and managed surprise
**Modules:** Saori layer, generative tension, archetype generation

### Optional: Tier 4 - Memory (2-3 hours)
**Goal:** Cross-session emotional memory and pattern tracking
**Modules:** Temporal memory, dream engine, session persistence
##

## WEEK 1: TIER 1 - FOUNDATION (45 min to 3 hours)

### Core Objective
- Add context tracking across turns
- Eliminate repeated questions
- Introduce basic compassionate posture
- Verify response time stays under 100ms

### Modules to Integrate

#### 1. ConversationMemory (PRIORITY: HIGHEST)
**File:** `src/emotional_os_glyphs/conversation_memory.py`

**What it does:**
- Tracks emotional state across conversation
- Builds emotional profile from signals
- Detects shifts in emotional tone
- Provides context for next response

**Integration Points:**

```python

# In response_handler.py, session init:
from src.emotional_os_glyphs.conversation_memory import ConversationMemory

class SessionState:
    def __init__(self):
        self.memory = ConversationMemory()
        self.session_id = None
        self.user_id = None

# In handle_response_pipeline:
def handle_response_pipeline(user_input, session):
    # Add turn to memory FIRST (before any analysis)
    session.memory.add_turn(user_input, {
        "role": "user",
        "timestamp": datetime.now()
    })

    # Get emotional context for this turn
    emotional_profile = session.memory.get_emotional_profile_brief()

    # Use profile in response generation:
    response = composer.compose_response_with_memory(
        user_input=user_input,
        memory_context=emotional_profile,
        glyph=detected_glyph
    )

    # Add response to memory
    session.memory.add_turn(response, {
        "role": "assistant",
        "timestamp": datetime.now()
    })

    return response
```



**Performance Impact:** +2-3ms (negligible)
##

#### 2. LexiconLearner (PRIORITY: HIGH)
**File:** `src/emotional_os_learning/lexicon_learner.py`

**What it does:**
- Learns user's emotional vocabulary over time
- Expands signal detection from user input
- Personalizes emotional understanding
- Updates learned lexicon file

**Integration Points:**

```python

# In handle_response_pipeline, after response generated:

from src.emotional_os_learning.lexicon_learner import get_lexicon_learner

learner = get_lexicon_learner()
learner.learn_from_exchange(
    user_input=user_input,
    detected_signals=signals,
    ai_response=response,
    user_id=session.user_id
)
```



**Performance Impact:** +1-2ms (async optional)
##

#### 3. Basic Sanctuary Wrapper (PRIORITY: MEDIUM)
**File:** `src/emotional_os_safety/sanctuary.py`

**What it does:**
- Detects sensitive/crisis content
- Wraps response with compassionate framing
- Offers consent flow if high-risk
- Non-intrusive, user-controlled

**Integration Points:**

```python

# In handle_response_pipeline, before returning response:

from src.emotional_os_safety.sanctuary import is_sensitive_input, ensure_sanctuary_response
from src.emotional_os_safety.sanctuary_handler import classify_risk

# Check if input is sensitive
if is_sensitive_input(user_input):
    risk_level = classify_risk(user_input)

    # If high-risk, show consent (user controls next action)
    if risk_level == "high":
        consent_prompt = build_consent_prompt("high")
        return consent_prompt  # Wait for user choice

    # Otherwise, wrap response with compassionate framing
    response = ensure_sanctuary_response(
        input_text=user_input,
        base_response=response,
        tone="gentle"
    )

return response
```



**Performance Impact:** +3-5ms (trauma lexicon lookup)
##

### Week 1 Implementation Steps

**Step 1: Update response_handler.py** (15 min)

```python

# File: src/emotional_os/deploy/modules/ui_components/response_handler.py

# Add imports at top
from src.emotional_os_glyphs.conversation_memory import ConversationMemory
from src.emotional_os_learning.lexicon_learner import get_lexicon_learner
from src.emotional_os_safety.sanctuary import is_sensitive_input, ensure_sanctuary_response
from src.emotional_os_safety.sanctuary_handler import classify_risk, build_consent_prompt

# Update handle_response_pipeline:
def handle_response_pipeline(user_input, context, session):
    """
    TIER 1: Foundation layer with context + compassion

    Flow:
    1. Add to memory (for context tracking)
    2. Check safety (risk classification)
    3. Detect signals (from expanded lexicon)
    4. Generate response (with context)
    5. Learn from exchange (update lexicon)
    6. Wrap with compassion (if needed)
    """

    # STAGE 1: Memory tracking
    session.memory.add_turn(user_input, {
        "role": "user",
        "timestamp": datetime.now()
    })
    emotional_profile = session.memory.get_emotional_profile_brief()

    # STAGE 2: Safety check
    is_sensitive = is_sensitive_input(user_input)
    if is_sensitive:
        risk = classify_risk(user_input)
        if risk == "high":
            prompt = build_consent_prompt(risk)
            session.memory.add_turn(prompt, {
                "role": "assistant",
                "timestamp": datetime.now(),
                "type": "consent_prompt"
            })
            return prompt

    # STAGE 3: Signal detection (existing)
    signals = signal_parser.parse_input(user_input)
    glyph = glyph_matcher.find_matching_glyph(signals)

    # STAGE 4: Response generation with context
    if emotional_profile and emotional_profile.get("confidence", 0) > 0.5:
        response = composer.compose_response_with_memory(
            user_input=user_input,
            memory_context=emotional_profile,
            glyph=glyph
        )
    else:
        response = composer.compose_response(user_input, glyph)

    # STAGE 5: Learning
    learner = get_lexicon_learner()
    learner.learn_from_exchange(
        user_input=user_input,
        detected_signals=signals,
        ai_response=response,
        user_id=session.user_id
    )

    # STAGE 6: Compassion wrapping
    if is_sensitive and risk != "high":
        response = ensure_sanctuary_response(
            input_text=user_input,
            base_response=response,
            tone="gentle"
        )

    # Add response to memory
    session.memory.add_turn(response, {
        "role": "assistant",
        "timestamp": datetime.now()
    })

    return response
```



**Step 2: Update ui_refactored.py** (10 min)

```python

# File: src/emotional_os/deploy/modules/ui_refactored.py

# In session initialization:
class SessionState:
    def __init__(self):
        # Add memory
        from src.emotional_os_glyphs.conversation_memory import ConversationMemory
        self.memory = ConversationMemory()

        # Keep existing state...
        self.conversation = []
        self.session_id = str(uuid.uuid4())
        self.user_id = None
```



**Step 3: Create test file** (15 min)

```python

# File: test_tier1_foundation.py

import pytest
from datetime import datetime
from src.emotional_os_glyphs.conversation_memory import ConversationMemory
from src.emotional_os_learning.lexicon_learner import get_lexicon_learner
from src.emotional_os_safety.sanctuary import is_sensitive_input

def test_memory_tracks_context():
    """Memory should track emotional arc across turns"""
    memory = ConversationMemory()

    # Turn 1: Stressed
    memory.add_turn("I'm overwhelmed at work", {"role": "user"})
    profile1 = memory.get_emotional_profile_brief()
    assert profile1["primary_emotion"] == "stress"

    # Turn 2: Conversation develops
    memory.add_turn("Tell me more", {"role": "assistant"})
    memory.add_turn("My boss keeps piling on tasks", {"role": "user"})
    profile2 = memory.get_emotional_profile_brief()

    # Should NOT show same opening twice
    assert profile2.get("depth_increase", 0) > 0

def test_lexicon_learns():
    """Lexicon should learn user vocabulary"""
    learner = get_lexicon_learner()

    # Teach new emotional words
    learner.learn_from_exchange(
        user_input="I feel gridlocked and suffocated",
        detected_signals=["stress", "overwhelm"],
        ai_response="That combination of gridlock and suffocation sounds real.",
        user_id="test_user"
    )

    # Verify learned
    learned = learner.get_learned_patterns("test_user")
    assert "gridlocked" in learned.get("user_vocabulary", [])

def test_sanctuary_detects_crisis():
    """Sanctuary should detect sensitive input"""
    assert is_sensitive_input("I'm suicidal") == True
    assert is_sensitive_input("I'm stressed") == False

def test_response_time():
    """Full pipeline should complete in < 100ms"""
    import time
    from src.emotional_os.deploy.modules.ui_components.response_handler import handle_response_pipeline

    class MockSession:
        def __init__(self):
            from src.emotional_os_glyphs.conversation_memory import ConversationMemory
            self.memory = ConversationMemory()
            self.user_id = "test"

    session = MockSession()

    start = time.time()
    response = handle_response_pipeline("I'm feeling stuck", {}, session)
    elapsed = (time.time() - start) * 1000  # ms

    assert elapsed < 100, f"Response took {elapsed}ms (should be < 100ms)"
    assert len(response) > 0
```



**Step 4: Test & Verify** (10 min)

```bash

# Run tests
python -m pytest test_tier1_foundation.py -v

# Run integration test with UI
streamlit run src/emotional_os/deploy/modules/ui_refactored.py

# Talk to system, verify:

# - No repeated questions

# - System remembers prior context

# - Responses feel more compassionate

# - Check response times in console
```



**Step 5: Deploy Tier 1** (5 min)
- Merge to main
- Test in staging
- Monitor response times
- Enable for all users
##

## WEEK 2: TIER 2 - ALIVENESS (4-6 hours)

### Core Objective
- Add emotional tone variation (not single robotic voice)
- Enable energy/fatigue cycles (detect and match pacing)
- Implement emotional reciprocity (system responds to emotion, not just content)
- Verify response time still under 100ms

### Modules to Integrate

#### 1. Presence Layer - Attunement (PRIORITY: HIGHEST)
**File:** `src/emotional_os/core/presence_integration.py`

**What it does:**
- Detects user's emotional pacing
- Matches system response pace to user
- Varies tone based on energy level
- Prevents robotic consistency

**Integration Points:**

```python

# In response_handler.py:

from src.emotional_os.core.presence_integration import PresenceIntegration

def handle_response_pipeline(user_input, context, session):
    # ... Tier 1 code ...

    # NEW: Attunement
    presence = PresenceIntegration()
    pacing_score = presence.detect_user_pacing(user_input, emotional_profile)

    # Apply pacing to response (affects sentence length, word choice)
    response = composer.compose_response_with_pacing(
        user_input=user_input,
        response=response,
        pacing=pacing_score
    )

    return response
```



**Performance Impact:** +2-3ms (profile-based, not model call)
##

#### 2. Emotional Reciprocity (PRIORITY: HIGH)
**File:** `src/emotional_os/core/emotional_reciprocity.py`

**What it does:**
- Detects user's emotional state
- Generates emotionally complementary response (not echoing)
- Balances validation + exploration
- Prevents stagnation in conversation

**Integration Points:**

```python

# In response_handler.py:

from src.emotional_os.core.emotional_reciprocity import EmotionalReciprocity

def handle_response_pipeline(user_input, context, session):
    # ... Tier 1 + Attunement code ...

    # NEW: Emotional reciprocity
    reciprocity = EmotionalReciprocity()
    complementary_tone = reciprocity.generate_complementary_tone(
        user_emotion=signals[0]["signal"] if signals else "neutral",
        conversation_history=session.memory.get_last_n_turns(3)
    )

    # Apply complementary tone
    response = composer.add_emotional_texture(
        response=response,
        emotional_tone=complementary_tone
    )

    return response
```



**Performance Impact:** +1-2ms (heuristic-based, no ML)
##

#### 3. Embodied Simulation - Energy Cycles (PRIORITY: MEDIUM)
**File:** `src/emotional_os/core/embodied_simulation.py`

**What it does:**
- Simulates system's "energy" state (fresh vs. fatigued)
- Varies response detail based on cycle
- Creates rhythm to conversation
- Feels more human-like

**Integration Points:**

```python

# In response_handler.py:

from src.emotional_os.core.embodied_simulation import EmbodiedSimulation

# Initialize once per session
session.embodied = EmbodiedSimulation()

def handle_response_pipeline(user_input, context, session):
    # ... Tier 1 + Attunement + Reciprocity code ...

    # NEW: Energy cycles
    energy_state = session.embodied.get_current_state()

    # Fresh: Longer, more detailed responses
    # Mid: Normal responses
    # Fatigued: Shorter, more direct responses
    response_length = {
        "fresh": "long",
        "mid": "normal",
        "fatigued": "short"
    }[energy_state]

    response = composer.compose_with_energy_state(
        response=response,
        energy=energy_state,
        length_preference=response_length[energy_state]
    )

    # Update system state (cycle through turns)
    session.embodied.update_state()

    return response
```



**Performance Impact:** +1ms (state machine, not model)
##

### Week 2 Implementation Steps

**Step 1: Create PresenceIntegration** (30 min)

```python

# File: src/emotional_os/core/presence_integration.py

from typing import Dict, Optional
import re

class PresenceIntegration:
    """Detect and match user pacing"""

    def __init__(self):
        self.fast_pace_indicators = [
            r"!+", r"\?\?+", r"etc\.", r"btw", r"omg", r"asap"
        ]
        self.slow_pace_indicators = [
            r"\.\.\.", r"hmm", r"maybe", r"i guess", r"i don't know"
        ]

    def detect_user_pacing(self, user_input: str, profile: Dict) -> str:
        """
        Detect pacing: 'fast', 'normal', 'slow'

        Fast: Exclamation marks, short turns, urgency
        Slow: Ellipses, hedging, contemplation
        """
        lower = user_input.lower()
        fast_score = sum(1 for pattern in self.fast_pace_indicators
                        if re.search(pattern, lower))
        slow_score = sum(1 for pattern in self.slow_pace_indicators
                        if re.search(pattern, lower))

        # Also check confidence from memory profile
        confidence = profile.get("confidence", 0.5)
        if confidence < 0.3:
            return "slow"
        elif fast_score > slow_score:
            return "fast"
        elif slow_score > fast_score:
            return "slow"
        else:
            return "normal"

    def apply_pacing_to_response(self, response: str, pacing: str) -> str:
        """Adjust response based on detected pacing"""
        if pacing == "fast":
            # Shorten, remove elaboration
            sentences = response.split(". ")
            return ". ".join(sentences[:2]) + "."
        elif pacing == "slow":
            # Lengthen, add pauses and reflection
            return response.replace(". ", ". ... ")
        else:
            return response
```



**Step 2: Create EmotionalReciprocity** (30 min)

```python

# File: src/emotional_os/core/emotional_reciprocity.py

from typing import Dict, List, Optional

class EmotionalReciprocity:
    """Generate emotionally complementary responses"""

    # Map from user emotion to system response approach
    RECIPROCITY_MAP = {
        "overwhelm": "grounding",  # Calm, steady, anchoring
        "joy": "expansion",         # Encourage, elaborate, celebrate
        "grief": "presence",        # Stay with, hold space, witness
        "confusion": "clarifying",  # Offer structure, name patterns
        "anger": "channeling",      # Validate, explore meaning
        "vulnerability": "safety",  # Gentle, protective, affirming
    }

    def generate_complementary_tone(self, user_emotion: str, history: List[Dict]) -> str:
        """
        What emotional stance should system take?

        Not echoing user (don't add more overwhelm if they're overwhelmed)
        But complementing (ground them)
        """
        approach = self.RECIPROCITY_MAP.get(user_emotion, "reflective")

        # Check if we've used this approach recently (avoid repetition)
        recent_approaches = [
            turn.get("emotional_approach")
            for turn in history
            if turn.get("role") == "assistant"
        ]

        if approach in recent_approaches:
            # Vary approach
            return self._vary_approach(approach)

        return approach

    def _vary_approach(self, approach: str) -> str:
        """Vary approach to avoid repetition"""
        variations = {
            "grounding": "validating",
            "expansion": "deepening",
            "presence": "exploring",
            "clarifying": "wondering",
            "channeling": "understanding",
            "safety": "empowering",
        }
        return variations.get(approach, "reflective")
```



**Step 3: Create EmbodiedSimulation** (30 min)

```python

# File: src/emotional_os/core/embodied_simulation.py

from enum import Enum

class EnergyState(Enum):
    FRESH = "fresh"
    MID = "mid"
    FATIGUED = "fatigued"

class EmbodiedSimulation:
    """Simulate system energy cycles"""

    def __init__(self, cycle_length: int = 7):
        """
        cycle_length: turns per full cycle
        Cycle: Fresh (2) → Mid (3) → Fatigued (2)
        """
        self.cycle_length = cycle_length
        self.turn_count = 0

    def get_current_state(self) -> str:
        """Where in cycle are we?"""
        position = self.turn_count % self.cycle_length

        if position < 2:
            return "fresh"
        elif position < 5:
            return "mid"
        else:
            return "fatigued"

    def update_state(self):
        """Move forward one turn"""
        self.turn_count += 1

    def reset(self):
        """Reset cycle (new conversation)"""
        self.turn_count = 0
```



**Step 4: Update response_handler.py with Tier 2** (20 min)

```python

# Add to imports
from src.emotional_os.core.presence_integration import PresenceIntegration
from src.emotional_os.core.emotional_reciprocity import EmotionalReciprocity
from src.emotional_os.core.embodied_simulation import EmbodiedSimulation

# Update handle_response_pipeline
def handle_response_pipeline(user_input, context, session):
    """
    TIER 1 + TIER 2: Foundation + Aliveness

    Tier 1: Memory + Safety + Learning
    Tier 2: Presence + Reciprocity + Energy
    """

    # [Tier 1 code from Week 1...]

    # TIER 2: Aliveness

    # Presence: Detect and match pacing
    presence = PresenceIntegration()
    pacing = presence.detect_user_pacing(user_input, emotional_profile)
    response = presence.apply_pacing_to_response(response, pacing)

    # Reciprocity: Generate complementary emotion
    reciprocity = EmotionalReciprocity()
    complementary_tone = reciprocity.generate_complementary_tone(
        user_emotion=signals[0]["signal"] if signals else "neutral",
        history=session.memory.get_last_n_turns(3)
    )

    # Embodied: Apply energy cycles
    if not hasattr(session, 'embodied'):
        session.embodied = EmbodiedSimulation()

    energy_state = session.embodied.get_current_state()
    # Apply energy state modulation to response...
    session.embodied.update_state()

    return response
```



**Step 5: Create test file** (20 min)

```python

# File: test_tier2_aliveness.py

import pytest
from src.emotional_os.core.presence_integration import PresenceIntegration
from src.emotional_os.core.emotional_reciprocity import EmotionalReciprocity
from src.emotional_os.core.embodied_simulation import EmbodiedSimulation

def test_pacing_detection():
    """Should detect fast vs slow pacing"""
    presence = PresenceIntegration()

    fast = presence.detect_user_pacing("I'm so stressed!!! Help ASAP!!!!", {})
    slow = presence.detect_user_pacing("I... I don't know. Maybe... I'm lost.", {})

    assert fast == "fast"
    assert slow == "slow"

def test_emotional_reciprocity():
    """Should vary emotional approach"""
    reciprocity = EmotionalReciprocity()

    # If user is overwhelmed, system grounds
    tone1 = reciprocity.generate_complementary_tone("overwhelm", [])
    assert tone1 == "grounding"

    # If joy, system expands
    tone2 = reciprocity.generate_complementary_tone("joy", [])
    assert tone2 == "expansion"

def test_energy_cycles():
    """Should cycle through energy states"""
    sim = EmbodiedSimulation(cycle_length=5)

    states = []
    for i in range(5):
        states.append(sim.get_current_state())
        sim.update_state()

    # Should see pattern: fresh → mid → fatigued
    assert "fresh" in states
    assert "mid" in states

def test_tier2_response_time():
    """Full pipeline with Tier 2 still under 100ms"""
    import time

    # [Similar to Tier 1 test, verify time]
    pass
```



**Step 6: Deploy Tier 2** (Incremental)
- Test locally first
- Deploy to canary (10% users)
- Monitor metrics
- Scale gradually
##

## WEEK 3-4: TIER 3 - DEPTH (6-8 hours)

### Core Objective
- Enable poetic understanding (metaphor-aware responses)
- Implement multiple archetypal voices
- Add managed surprise (dynamic variation)
- Maintain < 100ms response time

### Modules to Integrate

#### 1. Poetic Consciousness (PRIORITY: HIGHEST)
**File:** `src/emotional_os/core/poetic_consciousness.py`

**What it does:**
- Detects metaphorical language in user input
- Understands symbolic meaning, not just literal
- Responds poetically (reframes with imagery)
- Treats language as creative, not just informational

#### 2. Saori Layer (PRIORITY: HIGH)
**File:** `src/emotional_os/core/saori_integration.py`

**What it does:**
- Multiple archetypal voices (Mirror, Guardian, Witness, etc.)
- Creative response reframing
- Manages death/mortality themes compassionately
- Adds personality and depth

#### 3. Generative Tension (PRIORITY: MEDIUM)
**File:** `src/emotional_os/core/tension_integration.py`

**What it does:**
- Introduces managed surprise
- Challenges assumptions gently
- Creates dynamic variation
- Prevents predictable response patterns

### Implementation Strategy (Save detailed steps for when ready)

**Core principle:** Keep all local, fast, heuristic-based (no heavy ML)
##

## OPTIONAL: TIER 4 - LONG-TERM MEMORY (2-3 hours)

### Modules
- Temporal Memory (track patterns over time)
- Dream Engine (daily summaries)
- Cross-session persistence

### Implementation timing
After all Tiers 1-3 stable and tested
##

## ARCHITECTURE DECISIONS FOR PERFORMANCE

### Decision 1: Local-Only Processing

```python

# ✅ DO: Use local systems
- NRC (emotion lexicon)
- Spacy (NLP, entity recognition)
- TextBlob (sentiment)
- Regex patterns (fast matching)

# ❌ DON'T: External APIs
- No OpenAI calls
- No remote LLMs
- No network roundtrips
```



### Decision 2: Heuristic-Based, Not ML-Based

```python

# ✅ DO: Heuristics for speed
- Pattern matching (regex)
- Keyword lookups
- Rule-based logic
- State machines

# ❌ DON'T: Heavy models
- Large language models
- Complex neural networks
- Slow inference pipelines
```



### Decision 3: Pre-computation & Caching

```python

# ✅ DO: Cache what you can
- Emotion lexicon loaded once per session
- Patterns compiled at startup
- Emotional profiles cached

# ❌ DON'T: Recompute each turn
- Reparse lexicon files
- Recompile patterns
- Rebuild profiles
```



### Decision 4: Simple > Complex

```python

# ✅ DO: Simple approaches
- Detect pacing from punctuation
- Energy cycles with counters
- Emotional tones from keywords

# ❌ DON'T: Complex approaches
- Sentiment analysis on every word
- Complex ML models
- Deep NLP parsing
```


##

## PERFORMANCE MONITORING

### Metrics to Track

**Per-Response:**

```python
metrics = {
    "total_time_ms": 0,
    "breakdown": {
        "memory_add": 0,
        "signal_detection": 0,
        "safety_check": 0,
        "response_generation": 0,
        "learning": 0,
        "sanctuary_wrap": 0,
        "memory_update": 0,
    }
}
```



**Per-Session:**

```python
session_metrics = {
    "avg_response_time": 0,
    "max_response_time": 0,
    "min_response_time": 0,
    "turns_completed": 0,
    "error_count": 0,
}
```



### Instrumentation Code

```python

# In response_handler.py

import time
from contextlib import contextmanager

@contextmanager
def timer(label):
    """Simple timer context manager"""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[PERF] {label}: {elapsed:.2f}ms")

def handle_response_pipeline(user_input, context, session):
    total_start = time.perf_counter()

    with timer("Memory add"):
        session.memory.add_turn(user_input, {"role": "user"})

    with timer("Signal detection"):
        signals = signal_parser.parse_input(user_input)

    with timer("Safety check"):
        is_sensitive = is_sensitive_input(user_input)

    with timer("Response generation"):
        response = composer.compose_response(user_input, glyph)

    with timer("Learning"):
        learner.learn_from_exchange(user_input, signals, response)

    with timer("Memory update"):
        session.memory.add_turn(response, {"role": "assistant"})

    total_elapsed = (time.perf_counter() - total_start) * 1000
    print(f"\n[TOTAL] {total_elapsed:.2f}ms\n")

    # Warn if exceeds threshold
    if total_elapsed > 100:
        logger.warning(f"Response time {total_elapsed}ms > 100ms target")

    return response
```


##

## TESTING STRATEGY

### Tier 1 Tests (Week 1)

```bash
pytest test_tier1_foundation.py -v

# Verify: Context tracking, learning, safety
```



### Tier 2 Tests (Week 2)

```bash
pytest test_tier2_aliveness.py -v

# Verify: Pacing detection, reciprocity, energy cycles
```



### Tier 3 Tests (Week 3-4)

```bash
pytest test_tier3_depth.py -v

# Verify: Poetic understanding, archetypes, tension
```



### Integration Test (All Tiers)

```bash
pytest test_integration_full_pipeline.py -v

# Verify: All modules work together, no conflicts
```



### Performance Test (Each Tier)

```bash
pytest test_performance.py -v

# Verify: All responses < 100ms
```


##

## ROLLOUT STRATEGY

### Week 1 (Tier 1)
- Merge to main
- Deploy to staging
- Test for 24 hours
- Deploy to 10% users
- Monitor for 24 hours
- Deploy to 100%

### Week 2 (Tier 2)
- Same rollout sequence
- Can run in parallel with Tier 1 fixes if needed

### Week 3-4 (Tier 3)
- Same rollout sequence
- More thorough testing due to complexity

### Post-launch
- Monitor metrics daily
- Collect user feedback
- Fix issues discovered
- Plan optional Tier 4
##

## SUCCESS CRITERIA

### Tier 1: Foundation
- ✅ Context builds across turns (no repeated questions)
- ✅ All responses < 100ms
- ✅ No errors in learning
- ✅ Users report improved understanding

### Tier 2: Aliveness
- ✅ Responses vary in tone and pacing
- ✅ System matches user energy
- ✅ All responses < 100ms
- ✅ Users report system feels "more alive"

### Tier 3: Depth
- ✅ System understands metaphors
- ✅ Multiple voices active
- ✅ Managed surprise works
- ✅ All responses < 100ms
- ✅ Users report feeling "deeply understood"

### Overall
- ✅ Zero performance regressions
- ✅ No external API calls
- ✅ Fully local processing
- ✅ Compassionate + Dynamic + Presient + Relevant
##

## RISK MITIGATION

### Risk: Performance Degradation
**Mitigation:** Continuous monitoring, quick rollback per tier

### Risk: Learning Produces Bad Data
**Mitigation:** Quality filtering, user opt-in for learning

### Risk: Safety Wrapper Breaks Response
**Mitigation:** Careful testing, graceful fallbacks

### Risk: Multiple Systems Conflict
**Mitigation:** Clear integration points, minimal interdependency
##

## NEXT STEPS (TODAY)

1. **Review this plan** (20 min)
2. **Prepare development environment** (15 min)
3. **Create test files** (20 min)
4. **Implement Tier 1 changes** (30-60 min)
5. **Test locally** (20 min)
6. **Verify performance** (10 min)
7. **Commit and deploy to staging** (10 min)

**Total: 2-3 hours for Tier 1 foundation**

Then same process for Tier 2 and Tier 3 over following weeks.
