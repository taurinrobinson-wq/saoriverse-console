# Integration Roadmap: Step-by-Step Implementation Guide

**Status:** Implementation blueprint for connecting presence + tension modules  
**Target:** 4-week phased rollout  
**Priority:** ConversationMemory (Week 1) → Full Presence (Week 2-3) → Advanced (Week 3-4)

---

## WEEK 1: TIER 1 INTEGRATIONS (ConversationMemory + LexiconLearner)

### Goal
Add multi-turn context awareness and implicit learning feedback.

### Files to Modify
- `src/emotional_os/deploy/modules/ui_components/response_handler.py` (main changes)
- `src/emotional_os/deploy/modules/ui_refactored.py` (session state init)

### Implementation

#### Step 1.1: Initialize Conversation Memory on Session Start

**File:** `ui_refactored.py`

```python
def initialize_session_state():
    """Enhanced session state initialization with memory layers."""
    
    # ... existing code ...
    
    # NEW: Initialize conversation memory
    if "conversation_memory" not in st.session_state:
        from emotional_os_glyphs.conversation_memory import ConversationMemory
        st.session_state.conversation_memory = ConversationMemory()
        logger.info("ConversationMemory initialized")
    
    # NEW: Initialize lexicon learner
    if "lexicon_learner" not in st.session_state:
        from emotional_os.core.lexicon_learner import LexiconLearner
        st.session_state.lexicon_learner = LexiconLearner()
        logger.info("LexiconLearner initialized")
```

#### Step 1.2: Feed Messages to Memory + Generate Memory-Aware Responses

**File:** `response_handler.py` - Modify `_build_conversational_response()`

```python
def _build_conversational_response(user_input: str, local_analysis: dict) -> str:
    """Build response using conversation memory for context awareness."""
    
    best_glyph = local_analysis.get("best_glyph") if local_analysis else None
    voltage_response = local_analysis.get("voltage_response", "") if local_analysis else ""
    
    # ===== NEW: Memory-informed response =====
    memory = st.session_state.get("conversation_memory")
    
    if memory and user_input.strip():
        # Add this turn to memory
        try:
            memory.add_turn(
                message=user_input,
                signal_analysis=local_analysis,
            )
            logger.info(f"Added turn to memory. Confidence: {memory._state.emotional_profile.confidence}")
        except Exception as e:
            logger.warning(f"Failed to add turn to memory: {e}")
    
    # Use memory-aware composition if we have context
    if memory and memory._state.emotional_profile.confidence > 0.7:
        try:
            from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer
            composer = DynamicResponseComposer()
            
            response = composer.compose_response_with_memory(
                input_text=user_input,
                conversation_memory=memory,
                glyph=best_glyph,
            )
            
            if response and response.strip():
                logger.info("Used memory-informed response")
                return response
        except Exception as e:
            logger.debug(f"Memory-informed response failed, falling back: {e}")
    
    # ===== FALLBACK: Use voltage response as before =====
    if voltage_response and voltage_response.strip():
        response = voltage_response.strip()
        if "Resonant Glyph:" in response:
            response = response.split("Resonant Glyph:")[0].strip()
        return response
    
    # Last resort: basic glyph-based response
    return f"I hear you. {best_glyph.get('description', 'Tell me more.')}"
```

#### Step 1.3: Add Implicit Learning Feedback

**File:** `response_handler.py` - Add new function

```python
def _collect_implicit_feedback(user_input: str, response: str, local_analysis: dict) -> None:
    """Collect implicit feedback for lexicon learning without user interaction."""
    
    try:
        learner = st.session_state.get("lexicon_learner")
        if not learner:
            return
        
        # Create conversation turn for learning
        conversation_data = {
            "user_message": user_input,
            "system_response": response,
            "glyph": local_analysis.get("best_glyph", {}),
            "signals": local_analysis.get("signals", []),
            "timestamp": datetime.datetime.now().isoformat(),
        }
        
        # Learn from this exchange
        learning_results = learner.learn_from_conversation(conversation_data)
        
        if learning_results:
            logger.info(f"Learned patterns: {learning_results.get('new_patterns', [])}")
            
            # Update lexicon with new patterns
            learner.update_lexicon_from_learning(learning_results)
    
    except Exception as e:
        logger.warning(f"Implicit feedback collection failed: {e}")
```

#### Step 1.4: Call Feedback Collection After Response

**File:** `response_handler.py` - Modify `handle_response_pipeline()`

```python
def handle_response_pipeline(user_input: str, conversation_context: dict) -> str:
    """Execute the full response processing pipeline."""
    start_time = time.time()
    response = ""
    
    try:
        # ... existing code ...
        response = _run_local_processing(user_input, conversation_context)
        
        # NEW: Collect implicit feedback for learning
        local_analysis = st.session_state.get("last_local_analysis", {})
        _collect_implicit_feedback(user_input, response, local_analysis)
        
        # ... rest of pipeline ...
        
    except Exception as e:
        # ... error handling ...
        
    return response, processing_time
```

### Testing Tier 1

```python
# Test script: test_tier1_integration.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from emotional_os_glyphs.conversation_memory import ConversationMemory
from emotional_os.core.lexicon_learner import LexiconLearner

def test_tier1():
    """Test memory and learning integration."""
    
    # Test ConversationMemory
    memory = ConversationMemory()
    
    turn1 = {
        "signals": ["stress"],
        "intensity": 0.7,
    }
    memory.add_turn("I'm feeling stressed", turn1)
    print(f"Turn 1 Confidence: {memory._state.emotional_profile.confidence}")
    
    turn2 = {
        "signals": ["stress", "work_pressure"],
        "intensity": 0.85,
    }
    memory.add_turn("Work has so much going on", turn2)
    print(f"Turn 2 Confidence: {memory._state.emotional_profile.confidence}")
    
    # Check that understanding improved
    assert memory._state.emotional_profile.confidence > 0.7, "Memory should improve"
    
    # Test LexiconLearner
    learner = LexiconLearner()
    results = learner.learn_from_conversation({
        "user_message": "I feel overwhelmed",
        "system_response": "That overwhelm is real.",
        "glyph": {"glyph_name": "Fragmentation"},
    })
    print(f"Learning results: {results}")
    
    print("✅ TIER 1 INTEGRATION TESTS PASSED")

if __name__ == "__main__":
    test_tier1()
```

### Expected Outcomes (Week 1)

- ✅ Conversation memory tracking per session
- ✅ Context builds across turns
- ✅ System learns user's emotional vocabulary
- ✅ No repeated questions
- ✅ Response quality improves with each turn

---

## WEEK 2: TIER 2 INTEGRATIONS (Attunement + Embodiment + Reciprocity)

### Goal
Make responses feel alive, adaptive, and emotionally intelligent.

### Files to Create/Modify
- Create: `src/emotional_os/presence_integration.py` (new module)
- Modify: `response_handler.py` (call presence modules)
- Modify: `ui_refactored.py` (session init)

### Implementation

#### Step 2.1: Create Presence Integration Module

**File:** Create `src/emotional_os/presence_integration.py`

```python
"""
Presence Integration - Coordinate attunement, embodiment, reciprocity.
"""

import streamlit as st
import logging
from typing import Dict, Optional
from emotional_os.core.presence.attunement_loop import AttunementLoop
from emotional_os.core.presence.embodied_simulation import EmbodiedSimulation, InteractionLoad
from emotional_os.core.presence.emotional_reciprocity import EmotionalReciprocity

logger = logging.getLogger(__name__)


class PresenceIntegration:
    """Coordinate all presence layer components."""
    
    def __init__(self):
        """Initialize presence components."""
        self.attunement = AttunementLoop()
        self.embodiment = EmbodiedSimulation()
        self.reciprocity = EmotionalReciprocity()
    
    def process_user_message(self, user_input: str, analysis: Dict) -> Dict:
        """Process message through all presence layers."""
        
        # 1. Process through attunement
        signal = self.attunement.process_message(user_input)
        
        # 2. Calculate interaction load
        intensity = min(1.0, len(analysis.get("signals", [])) / 7.0)
        complexity = len(user_input.split()) / 100.0
        load = InteractionLoad(
            intensity=intensity,
            complexity=min(1.0, complexity),
            duration_factor=0.3,  # Placeholder
            requires_holding="grief" in analysis.get("signals", []),
        )
        
        # 3. Process through embodiment
        embodiment_state = self.embodiment.process_interaction(load)
        
        # 4. Process through emotional reciprocity
        emotional_input = self.reciprocity.detect_emotional_input(user_input)
        reciprocal_response = self.reciprocity.generate_reciprocal_response(emotional_input)
        
        # Return modifiers
        return {
            "attunement_state": self.attunement.get_current_state(),
            "embodiment_state": embodiment_state,
            "emotional_input": emotional_input,
            "reciprocal_response": reciprocal_response,
            "modifiers": self._build_response_modifiers(
                self.attunement.get_current_state(),
                embodiment_state,
                reciprocal_response,
            ),
        }
    
    def _build_response_modifiers(self, attunement_state, embodiment_state, reciprocal) -> Dict:
        """Build modifiers to apply to response."""
        return {
            "tone": attunement_state.tone.value,
            "rhythm": attunement_state.rhythm.value,
            "texture": embodiment_state.texture.value,
            "silence_weight": attunement_state.silence_weight,
            "reciprocal_tone": reciprocal.get("response_tone", "present"),
        }


def apply_presence_modifiers(response: str, modifiers: Dict) -> str:
    """Apply presence modifiers to response text."""
    
    # Example: Add strategic pauses based on silence_weight
    if modifiers.get("silence_weight", 0) > 0.3:
        # Add implicit pause indicator (could be rendered as literal pause in voice)
        response = f"[Pause...]\n{response}"
    
    # Example: Adjust vocabulary density based on texture
    texture = modifiers.get("texture", "flowing")
    if texture == "sparse":
        # More concise, fewer elaborations
        sentences = response.split(". ")
        if len(sentences) > 2:
            sentences = sentences[:2]  # Trim elaborations
            response = ". ".join(sentences) + "."
    
    elif texture == "soft":
        # Soften language
        soft_replacements = {
            "I notice": "I'm sensing",
            "You should": "You might",
            "must": "might",
            "have to": "could",
        }
        for hard, soft in soft_replacements.items():
            response = response.replace(hard, soft)
    
    return response
```

#### Step 2.2: Initialize Presence Layer in Session

**File:** `ui_refactored.py` - Add to `initialize_session_state()`

```python
    # NEW: Initialize presence layer
    if "presence_integration" not in st.session_state:
        from emotional_os.presence_integration import PresenceIntegration
        st.session_state.presence_integration = PresenceIntegration()
        logger.info("PresenceIntegration initialized")
```

#### Step 2.3: Apply Presence to Response Generation

**File:** `response_handler.py` - Modify response generation

```python
def _build_conversational_response(user_input: str, local_analysis: dict) -> str:
    """Build response with presence layer."""
    
    # ... existing memory logic ...
    
    # NEW: Apply presence layer
    presence = st.session_state.get("presence_integration")
    response_modifiers = None
    
    if presence:
        try:
            presence_output = presence.process_user_message(user_input, local_analysis)
            response_modifiers = presence_output.get("modifiers", {})
            logger.info(f"Presence: tone={response_modifiers.get('tone')}, rhythm={response_modifiers.get('rhythm')}")
        except Exception as e:
            logger.warning(f"Presence layer failed: {e}")
    
    # Generate base response
    response = ""  # ... existing response generation ...
    
    # NEW: Apply presence modifiers
    if response_modifiers:
        from emotional_os.presence_integration import apply_presence_modifiers
        try:
            response = apply_presence_modifiers(response, response_modifiers)
        except Exception as e:
            logger.warning(f"Failed to apply presence modifiers: {e}")
    
    return response
```

### Testing Tier 2

```python
# test_tier2_integration.py
from emotional_os.presence_integration import PresenceIntegration, apply_presence_modifiers

def test_tier2():
    """Test presence layer integration."""
    
    presence = PresenceIntegration()
    
    # Test attunement + embodiment
    result = presence.process_user_message(
        "I'm feeling so overwhelmed and anxious",
        {"signals": ["anxiety", "overwhelm"]},
    )
    
    print(f"Attunement: {result['attunement_state'].tone}")
    print(f"Embodiment: {result['embodiment_state'].state}")
    print(f"Emotional reciprocity: {result['reciprocal_response']}")
    
    # Test modifier application
    response = "You're feeling overwhelmed."
    modified = apply_presence_modifiers(response, result['modifiers'])
    print(f"Modified response: {modified}")
    
    print("✅ TIER 2 INTEGRATION TESTS PASSED")

if __name__ == "__main__":
    test_tier2()
```

### Expected Outcomes (Week 2)

- ✅ Responses reflect attunement to user pacing
- ✅ Embodiment creates realistic fatigue/energy cycles
- ✅ Emotional reciprocity provides complementary responses
- ✅ Response tone and texture vary dynamically
- ✅ System feels more "alive"

---

## WEEK 3-4: TIER 3 INTEGRATIONS (Saori + Generative Tension)

### Goal
Add poetic understanding, archetypal voices, and controlled surprise.

### Files to Create/Modify
- Create: `src/emotional_os/saori_integration.py` (new module)
- Create: `src/emotional_os/tension_integration.py` (new module)
- Modify: `response_handler.py` (call Saori + Tension)

### Implementation Outline (High-Level)

#### Step 3.1: Saori Integration

```python
# src/emotional_os/saori_integration.py

from emotional_os.core.saori.saori_layer import SaoriLayer, Archetype

class SaoriIntegration:
    """Integrate Saori layer (mirror, genome, mortality)."""
    
    def __init__(self):
        self.saori = SaoriLayer()
    
    def enhance_response_with_saori(self, response: str, user_input: str, analysis: Dict) -> str:
        """Enhance response with poetic understanding and archetypal voice."""
        
        # 1. Mirror engine - creative inversion
        mirror_reflection = self.saori.mirror_engine.create_reflection(
            message=user_input,
            emotion=analysis.get("primary_emotion"),
        )
        
        # 2. Select archetype
        archetype = self.saori.emotional_genome.select_archetype({
            "input": user_input,
            "engagement": "active",
        })
        
        # 3. Get mortality variance
        variance = self.saori.mortality_clock.get_response_variance({})
        
        # Blend into response
        enhanced = self._blend_saori_elements(
            response=response,
            mirror=mirror_reflection,
            archetype=archetype,
            variance=variance,
        )
        
        return enhanced
```

#### Step 3.2: Generative Tension Integration

```python
# src/emotional_os/tension_integration.py

from emotional_os.core.tension.generative_tension import GenerativeTension, DivergenceStyle

class TensionIntegration:
    """Integrate generative tension (surprise, challenge, subversion, creation)."""
    
    def __init__(self):
        self.tension = GenerativeTension()
        self.turn_count = 0
    
    def should_apply_tension(self, context: Dict) -> bool:
        """Decide if this turn should include tension."""
        self.turn_count += 1
        
        # Every 3rd turn, apply tension
        return self.turn_count % 3 == 0
    
    def apply_tension_to_response(self, response: str, user_input: str, analysis: Dict) -> str:
        """Apply generative tension to response."""
        
        if not self.should_apply_tension({}):
            return response
        
        # Generate divergence
        divergence = self.tension.generate_divergence(
            message=user_input,
            emotion=analysis.get("primary_emotion"),
            style=DivergenceStyle.METAPHORIC,
        )
        
        # Blend with base response
        enhanced = f"{response}\n\n{divergence.content}"
        return enhanced
```

---

## FULL INTEGRATION TIMELINE

```
WEEK 1
├─ Monday: Implement ConversationMemory (Step 1.1-1.2)
├─ Tuesday: Implement LexiconLearner (Step 1.3-1.4)
├─ Wednesday: Test Tier 1, fix bugs
├─ Thursday-Friday: Refinement, documentation

WEEK 2
├─ Monday: Create PresenceIntegration module (Step 2.1)
├─ Tuesday: Integrate into response pipeline (Step 2.2-2.3)
├─ Wednesday: Test Tier 2
├─ Thursday-Friday: Refinement, A/B test with users

WEEK 3
├─ Monday-Tuesday: Create SaoriIntegration + TensionIntegration
├─ Wednesday: Integrate into pipeline
├─ Thursday-Friday: Testing + A/B comparison

WEEK 4
├─ Monday-Wednesday: Refinement, user testing
├─ Thursday-Friday: Documentation, deployment prep
```

---

## TESTING EACH TIER

### Tier 1 Testing Checklist
- [ ] Memory accumulates confidence across turns
- [ ] System asks new questions (not repeated)
- [ ] Lexicon learns new patterns
- [ ] No performance degradation

### Tier 2 Testing Checklist
- [ ] Attunement adjusts to fast/slow user pacing
- [ ] Embodiment creates fatigue recovery cycles
- [ ] Reciprocity provides complementary responses
- [ ] Response tone varies appropriately

### Tier 3 Testing Checklist
- [ ] Mirror engine creates poetic inversions
- [ ] Archetype selection varies based on context
- [ ] Generative tension adds surprise at right moments
- [ ] No forced/artificial feeling

---

## SUCCESS METRICS

For each tier, measure:

1. **Response Quality**
   - User satisfaction ratings
   - Perceived understanding (1-10 scale)
   - Would recommend to friend

2. **System Intelligence**
   - Context recall accuracy
   - Question repetition rate (target: 0%)
   - Pattern recognition accuracy

3. **User Engagement**
   - Turn count before dropout
   - Return session rate
   - Session duration

4. **Technical**
   - Response latency
   - Memory footprint
   - Error rates

---

## DEPLOYMENT STRATEGY

### Canary Deployment
- Deploy Tier 1 to 10% of users
- Monitor for 1 week
- If stable, roll to 25%, then 50%, then 100%

### A/B Testing
- Tier 1: Control (old) vs. Test (with memory)
- Tier 2: Control vs. Test (with presence)
- Tier 3: Control vs. Test (with Saori + Tension)

### Rollback Plan
- Each tier is independently deployable/rollbackable
- Keep `use_presence_layer` flag in config for quick disable
- Log all errors for debugging

---

## NEXT STEPS

1. **Review this document** - Understand the architecture
2. **Start Week 1** - Begin with ConversationMemory integration
3. **Create test scripts** - Validate each tier before deployment
4. **Monitor metrics** - Track user experience improvements
5. **Iterate quickly** - Use feedback to refine

The framework is ready. Time to connect it all.

