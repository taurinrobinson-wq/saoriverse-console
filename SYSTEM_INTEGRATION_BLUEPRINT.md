# Integrated System Architecture & Implementation Plan

**Status:** Integration strategy for all modules into a cohesive, production-ready system  
**Scope:** Learning, Safety, Privacy, Lexicon, Parser modules + existing presence/saori/tension layers

---

## SYSTEM OVERVIEW

Your codebase contains several mature, independent systems that need integration:

### Core Systems (Active)
- **Signal Parser** → Emotion detection (currently used)
- **Glyph System** → Emotional vocabulary (currently used)
- **Response Composer** → Response generation (currently used)

### Learning Systems (Mature, Not Wired)
- **ArchetypeResponseGenerator** (v1 & v2) → Learn conversation patterns
- **HybridLearner** (v1 & v2) → Learn from cloud responses to improve local
- **ConversationLearner** → Multi-turn pattern extraction
- **PoetrySignalExtractor** → Extract poetry/metaphor signals
- **AdaptiveSignalExtractor** → Context-aware signal detection
- **ConversationArchetype** → Archetype library management

### Safety Systems (Mature, Partially Integrated)
- **Sanctuary** → Compassionate safety posture
- **SanctuaryHandler** → Risk classification + consent flow
- **ConversationManager** → Session safety management
- **CrisisRouting** → Crisis escalation protocol
- **FallbackProtocols** → Error handling safety nets

### Privacy Systems (Mature, Ready)
- **EncryptionManager** → AES-256 encryption for data at rest
- **DataEncodingPipeline** → 5-stage encoding (raw → signals → gates → glyphs → storage)
- **DreamEngine** → Long-term pattern summarization
- **AnonymizationProtocol** → User anonymization

### Lexicon Systems (Mature)
- **WordCentricLexicon** → Word-to-signal mapping with frequency data
- **LexiconLoader** → Unified lexicon interface

### Presence/Advanced Layers (Built in isolation)
- **ConversationMemory** → Multi-turn context tracking
- **Presence modules** → Attunement, embodiment, reciprocity, temporal memory
- **Poetic Consciousness** → Metaphor perception
- **Saori Layer** → Mirror engine, archetypes, mortality
- **Generative Tension** → Surprise, challenge, subversion, creation

---

## INTEGRATION ARCHITECTURE

### Unified Request Pipeline

```
User Input
    ↓
┌─────────────────────────────────────────────────────────────┐
│ SAFETY CHECK LAYER                                          │
│ ├─ Sanctuary.is_sensitive_input()                           │
│ ├─ SanctuaryHandler.classify_risk()                         │
│ └─ Handle high-risk escalation (with user consent)          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ ANALYSIS LAYER                                              │
│ ├─ WordCentricLexicon.find_emotional_words()               │
│ ├─ AdaptiveSignalExtractor.extract_signals()               │
│ ├─ ConversationMemory.add_turn()                           │
│ └─ PoetrySignalExtractor.extract_poetry_signals()          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ COMPOSITION LAYER                                           │
│ ├─ Select archetype (ConversationArchetype library)        │
│ ├─ Apply archetype principles (ArchetypeResponseGenerator) │
│ ├─ Apply presence modifiers (Attunement + Embodiment)      │
│ ├─ Apply Saori layer (Mirror + Genome + Mortality)        │
│ └─ Apply generative tension (Surprise + Challenge)         │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ ENCODING LAYER (Privacy)                                    │
│ ├─ DataEncodingPipeline (never store raw text)             │
│ ├─ EncryptionManager (AES-256 at rest)                     │
│ └─ Store only encoded/encrypted data                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE OUTPUT                                             │
│ ├─ Clean prosody metadata                                  │
│ ├─ Sanctuary wrapping if needed                            │
│ └─ Return to user                                          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ LEARNING LAYER (Post-Response)                              │
│ ├─ HybridLearner.learn_from_exchange()                     │
│ ├─ ConversationLearner.update_archetypes()                 │
│ ├─ DreamEngine.create_daily_summary()                      │
│ └─ Update lexicon + archetype library                      │
└─────────────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION STRATEGY (3-Phase Rollout)

### PHASE 1: Core Integration (1 week, 10-15 hours)

**Goal:** Wire all mature systems into main response pipeline

**Changes:**

1. **Create `src/emotional_os/integrated_pipeline.py`** (new orchestrator)
   - Coordinates all safety, analysis, composition, encoding, learning
   - Single entry point for response generation
   - Error handling and fallbacks

2. **Modify `response_handler.py`** to use integrated pipeline
   - Replace `_run_local_processing()` with integrated pipeline call
   - Keep backwards compatibility

3. **Wire Safety Layer**
   - Check sensitivity before processing
   - Handle consent flows for high-risk
   - Integrate CrisisRouting for escalation

4. **Wire Learning Layer**
   - Initialize HybridLearner + ConversationLearner in session
   - Call learn_from_exchange() after each response
   - Update archetype library daily

5. **Wire Privacy Layer**
   - DataEncodingPipeline for all stored data
   - EncryptionManager for at-rest encryption
   - Never store raw text

**Deliverables:**
- Integrated pipeline module
- Updated response handler
- Session state initialization
- Tests validating each layer

---

### PHASE 2: Presence & Advanced Layers (1-2 weeks, 10-15 hours)

**Goal:** Integrate ConversationMemory, Presence, Saori, Tension layers

**Changes:**

1. **Wire ConversationMemory**
   - Initialize per session
   - Add turn after analysis
   - Use for context-aware response selection

2. **Wire Presence Layer**
   - Attunement: Detect user pacing, apply rhythm modifiers
   - Embodiment: Track energy cycles, affect response texture
   - Reciprocity: Detect emotion, provide complementary response
   - Apply modifiers to final response

3. **Wire Saori Layer**
   - MirrorEngine: Creative inversion of emotional states
   - EmotionalGenome: Select archetype voice
   - MortalityClock: Add entropy/variation

4. **Wire Generative Tension**
   - Decide when to apply surprise (every nth turn)
   - Generate divergence when appropriate
   - Blend with base response

**Deliverables:**
- Presence integration module
- Saori + Tension integration
- Session state management
- Tests for each component

---

### PHASE 3: Optimization & Deployment (1 week, 5-10 hours)

**Goal:** Performance, monitoring, deployment

**Changes:**

1. **Performance Optimization**
   - Cache archetype library on startup
   - Batch learning operations
   - Async dream engine

2. **Monitoring & Logging**
   - Log all pipeline stages
   - Track safety escalations
   - Monitor response quality metrics

3. **Deployment**
   - Canary rollout (10% → 25% → 50% → 100%)
   - A/B testing for presence layer
   - Feature flags for quick disable

**Deliverables:**
- Performance benchmarks
- Monitoring dashboard
- Deployment playbook

---

## CORE INTEGRATION MODULE (Phase 1 - IMMEDIATE)

Create `src/emotional_os/integrated_pipeline.py`:

```python
"""
Unified Response Pipeline - Orchestrates all system layers
"""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PipelineContext:
    """Request context flowing through pipeline"""
    user_input: str
    user_id: Optional[str] = None
    conversation_context: Optional[Dict] = None
    safety_level: str = "normal"
    should_learn: bool = True
    

class IntegratedResponsePipeline:
    """Main orchestrator coordinating all system layers"""
    
    def __init__(self):
        """Initialize all pipeline components"""
        # Safety
        from emotional_os.safety.sanctuary import Sanctuary
        from emotional_os.safety.sanctuary_handler import SanctuaryHandler
        self.sanctuary = Sanctuary()
        self.sanctuary_handler = SanctuaryHandler()
        
        # Analysis
        from emotional_os_lexicon.lexicon_loader import WordCentricLexicon
        from emotional_os_learning.adaptive_signal_extractor import AdaptiveSignalExtractor
        from emotional_os_glyphs.conversation_memory import ConversationMemory
        from emotional_os_learning.poetry_signal_extractor import PoetrySignalExtractor
        self.lexicon = WordCentricLexicon()
        self.signal_extractor = AdaptiveSignalExtractor()
        self.memory = ConversationMemory()
        self.poetry_extractor = PoetrySignalExtractor()
        
        # Composition
        from emotional_os_learning.conversation_archetype import get_archetype_library
        from emotional_os_learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2
        from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer
        from emotional_os.core.presence_integration import PresenceIntegration
        from emotional_os.core.saori_integration import SaoriIntegration
        from emotional_os.core.tension_integration import TensionIntegration
        self.archetype_library = get_archetype_library()
        self.archetype_gen = ArchetypeResponseGeneratorV2()
        self.composer = DynamicResponseComposer()
        self.presence = PresenceIntegration()
        self.saori = SaoriIntegration()
        self.tension = TensionIntegration()
        
        # Privacy & Encoding
        from emotional_os_privacy.data_encoding import DataEncodingPipeline
        from emotional_os_privacy.encryption_manager import EncryptionManager
        self.encoding = DataEncodingPipeline()
        self.encryption = EncryptionManager()
        
        # Learning
        from emotional_os_learning.hybrid_learner_v2 import get_hybrid_learner
        from emotional_os_learning.conversation_learner import get_conversation_learner
        from emotional_os_privacy.dream_engine import DreamEngine
        self.hybrid_learner = get_hybrid_learner()
        self.conversation_learner = get_conversation_learner()
        self.dream_engine = DreamEngine()
    
    def process_request(self, context: PipelineContext) -> str:
        """
        Process user input through complete pipeline.
        Returns response text.
        """
        
        try:
            # STAGE 1: Safety Check
            response, risk_level = self._safety_check(context)
            if response:  # High-risk escalation handled
                return response
            
            # STAGE 2: Analysis
            analysis = self._analyze_input(context)
            
            # Add to memory
            self.memory.add_turn(context.user_input, analysis)
            
            # STAGE 3: Composition
            response = self._compose_response(context, analysis)
            
            # STAGE 4: Apply Presence & Advanced Layers
            response = self._apply_presence(response, analysis)
            response = self._apply_saori(response, analysis)
            response = self._apply_tension(response, analysis)
            
            # STAGE 5: Privacy & Encoding
            # (Encoding happens at storage, not in response)
            
            # STAGE 6: Learning (Async if possible)
            if context.should_learn:
                self._learn_from_exchange(context.user_input, response, analysis)
            
            return response
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return self._fallback_response(context)
    
    def _safety_check(self, context: PipelineContext) -> tuple:
        """STAGE 1: Safety check with consent flow"""
        try:
            if not self.sanctuary.is_sensitive_input(context.user_input):
                return None, "normal"
            
            risk = self.sanctuary_handler.classify_risk(context.user_input)
            
            if risk == "high":
                # Build consent prompt for high-risk
                prompt = self.sanctuary_handler.build_consent_prompt("high")
                return prompt, "high"
            
            return None, risk
        except Exception as e:
            logger.warning(f"Safety check failed: {e}")
            return None, "normal"
    
    def _analyze_input(self, context: PipelineContext) -> Dict:
        """STAGE 2: Full analysis"""
        try:
            analysis = {
                "lexicon_words": self.lexicon.find_emotional_words(context.user_input),
                "signals": self.signal_extractor.extract_signals(context.user_input),
                "poetry": self.poetry_extractor.extract_signals(context.user_input),
                "memory_state": self.memory.get_conversation_summary() if self.memory._turns else None,
            }
            return analysis
        except Exception as e:
            logger.warning(f"Analysis failed: {e}")
            return {}
    
    def _compose_response(self, context: PipelineContext, analysis: Dict) -> str:
        """STAGE 3: Response composition"""
        try:
            # Try archetype-based generation first
            archetype_response = self.archetype_gen.generate_archetype_aware_response(
                context.user_input,
                prior_context=context.conversation_context,
                glyph=analysis.get("glyph"),
            )
            
            if archetype_response:
                return archetype_response
            
            # Fallback to traditional composition with memory
            if self.memory._state.emotional_profile.confidence > 0.7:
                return self.composer.compose_response_with_memory(
                    context.user_input,
                    self.memory,
                    analysis.get("glyph"),
                )
            
            # Standard composition
            return self.composer.compose_response(
                context.user_input,
                analysis.get("glyph"),
            )
        except Exception as e:
            logger.warning(f"Composition failed: {e}")
            return "I'm here to listen."
    
    def _apply_presence(self, response: str, analysis: Dict) -> str:
        """Apply presence layer modifiers"""
        try:
            result = self.presence.process_analysis(response, analysis)
            return result.get("response", response)
        except Exception as e:
            logger.debug(f"Presence layer failed: {e}")
            return response
    
    def _apply_saori(self, response: str, analysis: Dict) -> str:
        """Apply Saori layer (mirror, archetypes, mortality)"""
        try:
            return self.saori.enhance_response(response, analysis)
        except Exception as e:
            logger.debug(f"Saori layer failed: {e}")
            return response
    
    def _apply_tension(self, response: str, analysis: Dict) -> str:
        """Apply generative tension"""
        try:
            if self.tension.should_apply_tension({}):
                return self.tension.apply_tension(response, analysis)
            return response
        except Exception as e:
            logger.debug(f"Tension layer failed: {e}")
            return response
    
    def _learn_from_exchange(self, user_input: str, response: str, analysis: Dict) -> None:
        """STAGE 6: Post-response learning"""
        try:
            # Hybrid learning (improve local model from cloud responses)
            self.hybrid_learner.learn_from_exchange(
                user_input=user_input,
                ai_response=response,
                emotional_signals=analysis.get("signals", []),
                glyphs=analysis.get("glyphs", []),
            )
            
            # Conversation learning (update archetype library)
            self.conversation_learner.learn_from_turn(
                user_input=user_input,
                response=response,
                signals=analysis.get("signals", []),
            )
        except Exception as e:
            logger.debug(f"Learning failed: {e}")
    
    def _fallback_response(self, context: PipelineContext) -> str:
        """Safe fallback response"""
        return "I'm here to listen. What's on your mind?"


# Singleton
_pipeline = None

def get_pipeline() -> IntegratedResponsePipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = IntegratedResponsePipeline()
    return _pipeline
```

---

## PHASE 1 INTEGRATION CHECKLIST

### Week 1 Tasks
- [ ] Create integrated_pipeline.py with above code
- [ ] Update response_handler.py to use new pipeline
- [ ] Initialize pipeline in ui_refactored.py session
- [ ] Wire safety layer (Sanctuary + risk classification)
- [ ] Wire learning layer (HybridLearner + ConversationLearner)
- [ ] Test each stage independently
- [ ] Run integration tests
- [ ] Deploy to 10% users

### Files to Modify
1. Create: `src/emotional_os/integrated_pipeline.py`
2. Modify: `src/emotional_os/deploy/modules/ui_components/response_handler.py`
3. Modify: `src/emotional_os/deploy/modules/ui_refactored.py`

### Tests to Create
- `test_integrated_pipeline.py` - Full end-to-end
- `test_safety_integration.py` - Safety layer
- `test_learning_integration.py` - Learning layer
- `test_privacy_encoding.py` - Privacy layer

---

## SYSTEM BENEFITS (Post-Integration)

**User Experience:**
- ✅ Safer interactions (risk detection + consent flow)
- ✅ Context-aware responses (memory builds)
- ✅ Learning improves over time (hybrid + archetype learning)
- ✅ Responsive, adaptive presence
- ✅ Creative, dynamic responses
- ✅ Complete privacy (raw text never stored)

**System Intelligence:**
- ✅ Learns user patterns (archetype library)
- ✅ Extracts poetry/metaphor (signal extraction)
- ✅ Adaptive signal detection (context-aware)
- ✅ Daily summaries for long-term patterns (dream engine)

**Privacy & Safety:**
- ✅ AES-256 encryption at rest
- ✅ 5-stage encoding pipeline
- ✅ Risk classification + consent
- ✅ Crisis escalation with user agency

---

## SUCCESS METRICS

### Phase 1 Complete
- All pipeline stages operational
- No regression in response quality
- < 500ms added latency per request
- Learning log growing (new patterns detected)
- Safety escalations tracked

### Phase 2 Complete
- Presence modifiers visible in responses
- Saori layer archetypes active
- Tension creates appropriate surprises
- User engagement metrics improve

### Phase 3 Complete
- System in production (100% users)
- Monitoring dashboard live
- Archetype library growing
- Dream engine creating summaries

---

## NEXT STEP

Start Phase 1 immediately:

1. Copy integrated_pipeline.py code above into new file
2. Import into response_handler.py
3. Replace pipeline in handle_response_pipeline()
4. Test with sample conversations
5. Deploy to canary

Expected time to functional system: **1 week** for Phase 1

