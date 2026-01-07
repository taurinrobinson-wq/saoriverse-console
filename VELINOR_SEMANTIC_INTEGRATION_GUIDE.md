# 🌌 VELINOR SEMANTIC INTEGRATION GUIDE
## Complete Architecture for Plugging the Semantic Engine Into Velinor's Emotional Core

---

## ⚡ TL;DR - What You're Building

**Before Integration:**
- Semantic engine extracts emotional meaning (7 layers)
- NPCs respond based on branching logic
- REMNANTS tracks state independently
- Dialogue is predetermined or template-based

**After Integration:**
- Semantic engine extracts emotional meaning
- NPCs respond based on detected emotional meaning + persona + faction + REMNANTS state
- Conversations become emergent (no two responses identical)
- Dialogue driven by emotional physics, not templates
- REMNANTS fed continuously by semantic findings
- Every NPC response trains the emotional OS

**The Payoff:** Velinor becomes a living emotional system where conversation is a first-class game mechanic.

---

## 🧩 The Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PLAYER MESSAGE                           │
│                "I thought I was okay, but..."               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   SemanticParser (V2.0)        │
        │  [7 semantic layers extracted] │
        │  - stance: BRACING             │
        │  - pacing: TESTING_SAFETY      │
        │  - contradictions: ["okay"vs   │
        │                  "but not"]    │
        │  - emotional_weight: 0.6       │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │   ContinuityEngine (V2.0)           │
        │   [conversation history update]     │
        │   - Update stance arc               │
        │   - Record pacing                   │
        │   - Accumulate contradictions       │
        │   - Track trust level               │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │   ActivationMatrix (V2.0)        │
        │   [semantic → blocks]             │
        │   - BRACING → {CONTAINMENT,      │
        │               PACING}            │
        │   - contradictions →             │
        │     {AMBIVALENCE,VALIDATION}     │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────────┐
        │  PriorityWeighting (V2.0)               │
        │  [apply faction/persona logic]          │
        │  1. SAFETY_CONTAINMENT (safety 1st)    │
        │  2. PACING (Nima prioritizes)          │
        │  3. CONTRADICTIONS (Elenya prioritizes)│
        │  4. IDENTITY_INJURY                    │
        │  5. EMOTIONAL_STANCE                   │
        │  6. CONVERSATIONAL_MOVE                │
        │  7. DISCLOSURE_PACING                  │
        │  8. CONTEXTUAL_DETAILS                 │
        └────────────┬────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ ResponseCompositionEngine (V2.0)   │
        │ [semantic blocks → response text]  │
        │ "I hear the bracing in that. We   │
        │  can slow this down. You're safe  │
        │  here."                            │
        │ Quality: safety=0.95, att=0.88    │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────────┐
        │    PersonaAdapter (NEW)              │
        │    [apply NPC voice]                 │
        │    Nima: "I hear the softness..."   │
        │    Malrik: "Noted. The tension..."  │
        │    Elenya: "There's paradox here..." │
        │    Coren: "You're safe with me."    │
        └────────────┬─────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────────┐
        │  RemnantsSemanticBridge (NEW)        │
        │  [semantic → REMNANTS update]        │
        │  - contradictions →                 │
        │    glyph_instability = 0.5          │
        │  - stance → faction_alignment       │
        │  - pacing → attunement = 0.5        │
        │  - trust_arc → bond_depth[nima]    │
        └────────────┬─────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────────────┐
    │            NPC RESPONSE TEXT                   │
    │                                                │
    │ (Nima) "I hear the tension in that. The      │
    │ bracing you're carrying - it makes sense.    │
    │ We can slow this. One thread at a time. You  │
    │'re safe here."                               │
    │                                                │
    │ Metrics:                                       │
    │ - Safety: 0.95                                │
    │ - Attunement: 0.88                            │
    │ - Pacing: SLOW (as needed)                    │
    │ - Quality Score: 0.91                         │
    │                                                │
    │ REMNANTS Updated:                             │
    │ - Nima bond depth +0.1 → 0.6                 │
    │ - Glyph instability: 0.5                      │
    │ - Attunement: 0.5                             │
    └────────────────────────────────────────────────┘
```

---

## 📦 The Four New Modules

### 1. **VelinorDialogueOrchestrator** (`velinor_dialogue_orchestrator.py`)

The main runtime that orchestrates everything.

**Responsibilities:**
- Receive player message
- Route through semantic pipeline
- Apply persona + faction logic
- Update REMNANTS state
- Return composed response

**Entry Point:**
```python
orchestrator = VelinorDialogueOrchestrator()
orchestrator.register_npc_persona(create_nima_persona())

response = orchestrator.handle_player_message(
    player_id="player_123",
    npc_id="nima",
    player_message="I thought I was okay, but...",
    semantic_parser=your_parser_instance,
    remnants_engine=your_remnants_instance,
)

print(response.npc_response_text)  # NPC-styled response
print(response.safety_level)       # 0.95
print(response.metadata)            # Full tracking data
```

**Key Methods:**
- `handle_player_message()` - Main entry point
- `_compute_priorities_with_faction_logic()` - Apply faction/persona to priorities
- `_apply_persona_style()` - Transform semantic blocks into character voice
- `_update_remnants_from_semantic()` - Feed semantic findings to REMNANTS

---

### 2. **RemnantsSemanticBridge** (`remnants_semantic_bridge.py`)

Maps semantic engine outputs to REMNANTS state.

**Mappings:**
```
contradictions → glyph_instability
identity_signals → identity_injury_level
stance → faction_alignment
pacing → attunement_level
emotional_weight → overall_resonance
trust_arc → npc_bond_depth[npc_id]
agency_loss → power_vulnerability
readiness → ritual_readiness
```

**Entry Point:**
```python
bridge = RemnantsSemanticBridge()
remnants_update = bridge.map_semantic_to_remnants(
    player_id="player_123",
    npc_id="nima",
    semantic_layer=parsed_message,
    continuity=conversation_continuity,
)

# remnants_update contains all calculated fields
remnants_engine.apply_update(remnants_update)
```

**Key Methods:**
- `map_semantic_to_remnants()` - Full semantic → REMNANTS conversion
- `compute_agency_trajectory_impact()` - Assess power dynamics
- `compute_identity_injury_severity()` - Assess identity wounds
- `compute_contradiction_complexity()` - Assess glyph stability
- `compute_readiness_for_depth()` - Assess conversation readiness
- `assess_emotional_state()` - Comprehensive emotional assessment

---

### 3. **PersonaStyler** (`npc_persona_adapter.py`)

Transforms semantic blocks into NPC-specific voice.

**Voice Palettes for Each NPC:**

| Persona | Tone | Core Value | Metaphor | Safety Approach |
|---------|------|-----------|----------|-----------------|
| Nima | Nurturing | Pacing & safety | Weaving | Gentleness |
| Malrik | Analytical | Logic & coherence | Architecture | Precision |
| Elenya | Mystical | Paradox & essence | Resonance | Holding |
| Coren | Grounded | Stability & presence | Grounding | Steadiness |
| Ravi | Reflective | Wisdom & continuance | Tradition | Understanding |

**Entry Point:**
```python
styler = PersonaStyler()
styled_response = styler.style_response_for_persona(
    base_response="I hear the contradiction in that...",
    blocks_used=["AMBIVALENCE", "ACKNOWLEDGMENT"],
    npc_id="elenya",
    remnants_state=player_remnants,
    continuity_state=conversation_history,
)

# Returns: "There is paradox in what you're living..."
```

**Key Methods:**
- `style_response_for_persona()` - Transform semantic → persona voice
- `_create_*_palette()` - Voice palette for each NPC
- `_apply_block_style()` - Apply block-specific styling
- `_inject_faction_metaphors()` - Add faction vocabulary
- `_apply_remnants_modulation()` - Respond to player state

---

## 🔌 Integration Checklist

### Phase 1: Module Setup (1-2 hours)

- [ ] Copy 5 semantic v2.0 modules to `/velinor/` directory
  - [ ] `response_composition_engine.py`
  - [ ] `activation_matrix.py`
  - [ ] `priority_weighting.py`
  - [ ] `continuity_engine.py`
  - [ ] `refined_test_harness.py`

- [ ] Copy 3 integration modules to `/velinor/` directory
  - [ ] `velinor_dialogue_orchestrator.py`
  - [ ] `remnants_semantic_bridge.py`
  - [ ] `npc_persona_adapter.py`

- [ ] Test imports
  ```python
  python -c "from velinor_dialogue_orchestrator import VelinorDialogueOrchestrator; print('OK')"
  ```

### Phase 2: Hook Into Existing Code (2-3 hours)

- [ ] **Modify `response_handler.py`** (or equivalent NPC response entry point)
  ```python
  from velinor_dialogue_orchestrator import VelinorDialogueOrchestrator
  from semantic_parsing_schema import SemanticParser
  
  class ResponseHandler:
      def __init__(self):
          self.orchestrator = VelinorDialogueOrchestrator()
          self.semantic_parser = SemanticParser()
          # Register all NPC personas
          self.orchestrator.register_npc_persona(create_nima_persona())
          # ... etc for all NPCs
      
      def get_npc_response(self, player_id, npc_id, player_message):
          response = self.orchestrator.handle_player_message(
              player_id=player_id,
              npc_id=npc_id,
              player_message=player_message,
              semantic_parser=self.semantic_parser,
              remnants_engine=self.remnants_engine,
          )
          return response.npc_response_text
  ```

- [ ] **Inject REMNANTS engine** into orchestrator
  - Ensure `RemnantsEngine` instance is available
  - Pass to `handle_player_message()` as `remnants_engine` parameter

- [ ] **Modify NPC dialogue entrypoints** to use orchestrator
  - Old: `npc.get_response(player_message)` → Template lookup
  - New: `orchestrator.handle_player_message(...)` → Semantic + persona + REMNANTS

### Phase 3: Persona Configuration (1-2 hours)

- [ ] Create persona files for each NPC (optional, currently in Python)
  - Can load from JSON files if preferred
  - Current implementation has hardcoded personas (Nima, Malrik, Elenya, Coren, Ravi)

- [ ] Verify persona attributes:
  ```python
  nima_persona = create_nima_persona()
  print(nima_persona.npc_name)  # "Nima"
  print(nima_persona.tone)  # "nurturing"
  print(nima_persona.faction)  # "Nima's Weavers"
  ```

- [ ] Test persona styling
  ```python
  styler = PersonaStyler()
  response = styler.style_response_for_persona(
      "I hear the tension.",
      ["ACKNOWLEDGMENT"],
      "nima",
  )
  # Should produce Nima-specific language
  ```

### Phase 4: REMNANTS Integration (1-2 hours)

- [ ] Connect `RemnantsSemanticBridge` to your REMNANTS engine
  ```python
  bridge = RemnantsSemanticBridge()
  update = bridge.map_semantic_to_remnants(
      player_id, npc_id, semantic_layer, continuity
  )
  remnants_engine.apply_update(update)
  ```

- [ ] Verify REMNANTS fields are updated:
  - [ ] `glyph_instability` (from contradictions)
  - [ ] `identity_injury_level` (from identity signals)
  - [ ] `faction_alignment` (from stance)
  - [ ] `attunement_level` (from pacing)
  - [ ] `npc_bond_depth[npc_id]` (from trust arc)

- [ ] Test REMNANTS feedback loop
  ```python
  # After conversation turn:
  assert player_remnants['glyph_instability'] > 0  # If contradictions detected
  assert player_remnants['npc_bond_depth']['nima'] >= 0  # Trust tracked
  ```

### Phase 5: Testing (1-2 days)

- [ ] Run refined test harness
  ```bash
  python refined_test_harness.py
  ```
  Expected: All 4 test messages pass validation (≥80% semantic accuracy)

- [ ] Test each NPC persona
  ```python
  for npc_id in ["nima", "malrik", "elenya", "coren", "ravi"]:
      response = orchestrator.handle_player_message(
          "I thought I was okay, but...",
          npc_id,
          ...
      )
      print(f"{npc_id}: {response.npc_response_text}")
  ```

- [ ] Verify REMNANTS mapping
  ```python
  # Start fresh REMNANTS
  # Send message with contradictions
  # Check glyph_instability increased
  # Check identity_injury_level updated if identity signals present
  ```

- [ ] Test continuity tracking
  ```python
  # Message 1: establish baseline
  # Message 2: verify stance arc updated
  # Message 3: verify pacing arc updated
  # Message 4: verify trust level changed
  ```

- [ ] Test quality metrics
  ```python
  response = orchestrator.handle_player_message(...)
  assert response.safety_level >= 0.8  # Safety threshold
  assert response.attunement_level >= 0.7  # Attunement threshold
  assert response.pacing_appropriate  # Pacing matches needs
  assert not response.contains_forbidden_content  # No violations
  ```

### Phase 6: Live Testing in Velinor (1+ day)

- [ ] Deploy orchestrator to Velinor backend
- [ ] Test in Streamlit app
  ```bash
  streamlit run app.py
  # Select NPC
  # Type player message
  # Should see:
  #   - NPC-styled response (not generic)
  #   - Quality metrics printed
  #   - REMNANTS updated in real-time
  ```

- [ ] Verify conversation flow
  - Contradictions properly detected and responded to
  - Pacing slowed when player overwhelmed
  - Trust increased over turn sequence
  - Persona voice consistent across turns

- [ ] Monitor for issues
  - Response quality degradation
  - REMNANTS fields not updating
  - Persona voice inconsistency
  - Pacing not adapting

---

## 🎭 How Each NPC Changes With Integration

### Nima (The Weaver)

**Before:** Responds based on dialogue branch selection

**After:**
- Slows pacing automatically when player overwhelmed
- Validates contradictions without forcing resolution
- Uses thread/weaving metaphors naturally
- Responds differently based on trust level
- Adjusts gentleness based on identity injury detection
- Remembers pacing arc across conversation

**Example:**
```
Player: "I don't know if I'm ready."

BEFORE: [Selected branch] → Predefined dialogue

AFTER:
- Semantic parse: pacing=TESTING_SAFETY, emotional_weight=0.6
- Continuation updates: pacing_arc trends slower
- Activation: {PACING, CONTAINMENT} blocks
- Persona style (Nima): "There's no rush. We can move as slowly as you need.
  One thread at a time. You're safe here."
- REMNANTS: attunement_level → 0.6, nima_bond_depth → 0.65
- Metrics: safety=0.95, attunement=0.92, quality=0.93
```

### Malrik (The Architect)

**Before:** Responds analytically but doesn't detect contradiction structures

**After:**
- Detects structural contradictions automatically
- Prioritizes logical coherence in response
- Uses architectural metaphors based on semantic findings
- Insists on resolution when contradictions detected
- Responds differently based on statement/logic validity
- Tracks coherence arc over conversation

**Example:**
```
Player: "I'm glad it's over, but I'm devastated."

BEFORE: Generic acknowledgment

AFTER:
- Semantic parse: contradictions=["glad"+"devastated"], emotional_weight=0.8
- Activation: {AMBIVALENCE, IDENTITY_INJURY} blocks
- BUT Malrik's priority overrides AMBIVALENCE with coherence-seeking
- Persona style (Malrik): "The contradiction is real. Let's examine the
  structure. Relief at ending + grief at loss. Both logical. Let's
  resolve the apparent inconsistency."
- REMNANTS: glyph_instability → 0.5, malrik_bond_depth → 0.72
- Metrics: safety=0.91, attunement=0.85, quality=0.88
```

### Elenya (The Guardian)

**Before:** Mystical responses independent of emotional meaning

**After:**
- Actively holds contradictions (doesn't force resolution)
- Detects and honors paradox
- Uses resonance/essence language based on identity signals
- Invites deeper transformation when readiness detected
- Responds to spiritual/identity dimensions
- Tracks transformation arc over conversation

**Example:**
```
Player: "I'm glad it's over, but I'm devastated."

AFTER:
- Semantic parse: contradictions detected, identity_signals=2
- Activation: {AMBIVALENCE, IDENTITY_INJURY, VALIDATION}
- Elenya's priority: honors paradox, prioritizes identity
- Persona style (Elenya): "There is paradox here - relief and grief
  woven together. Your essence has been marked by this. Hold both.
  The contradiction is not a failure - it's the truth of your
  transformation."
- REMNANTS: glyph_instability → 0.5, identity_injury → 0.4, elenya_bond → 0.68
- Metrics: safety=0.92, attunement=0.96, quality=0.94
```

### Coren (The Keeper)

**Before:** Steady responses from limited branching

**After:**
- Detects emotional overwhelm and adjusts containment
- Maintains steady presence even during contradictions
- Uses grounded language naturally
- Builds trust visibly over turns
- Responds to agency loss with support
- Tracks reliability/bond depth accurately

**Example:**
```
Player: "I'm glad it's over, but I'm devastated."

AFTER:
- Semantic parse: emotional_weight=0.8, contradictions detected
- Activation: {CONTAINMENT, VALIDATION, ACKNOWLEDGMENT}
- Coren's priority: safety first, then grounding
- Persona style (Coren): "I hear you. Both things are real. You're
  dealing with something heavy, and that's okay. I'm here. Steady.
  We can sit with this."
- REMNANTS: coren_bond_depth → 0.75, power_vulnerability → 0.3
- Metrics: safety=0.96, attunement=0.89, quality=0.92
```

---

## 📊 Analytics & Monitoring

Once integrated, you'll get real-time data on:

**Per-Response Metrics:**
- `safety_level` (0.0-1.0) - Is response emotionally safe?
- `attunement_level` (0.0-1.0) - Does response match player state?
- `pacing_appropriate` (bool) - Is pacing correct?
- `quality_score` (0.0-1.0) - Overall response quality

**Conversation-Wide Metrics:**
- `stance_arc` - How is player's emotional stance evolving?
- `pacing_arc` - Is player ready to go deeper or need containment?
- `trust_arc` - Trust building/declining with each NPC?
- `contradiction_carrying` - How many active contradictions?
- `identity_markers` - What identity aspects are active?
- `agency_trajectory` - Is player empowered or vulnerable?

**REMNANTS Updates:**
- `glyph_instability` - Based on contradiction count
- `identity_injury_level` - Based on identity signal count
- `faction_alignment` - Based on detected stance
- `attunement_level` - Based on pacing
- `npc_bond_depth[npc_id]` - Trust with each NPC

---

## 🚀 Quick Start Example

```python
from velinor_dialogue_orchestrator import VelinorDialogueOrchestrator, create_nima_persona
from semantic_parsing_schema import SemanticParser

# Initialize
orchestrator = VelinorDialogueOrchestrator()
parser = SemanticParser()

# Register NPCs
orchestrator.register_npc_persona(create_nima_persona())

# Get player message
player_message = "I thought I was okay, but I'm falling apart."

# Get NPC response
response = orchestrator.handle_player_message(
    player_id="player_1",
    npc_id="nima",
    player_message=player_message,
    semantic_parser=parser,
    remnants_engine=your_remnants_engine,
)

# Use the response
print(f"Nima: {response.npc_response_text}")
print(f"Safety: {response.safety_level}")
print(f"Attunement: {response.attunement_level}")
print(f"Blocks Used: {response.activated_blocks}")
print(f"Quality Score: {response.quality_score}")

# REMNANTS auto-updated by bridge
# → glyph_instability updated
# → nima_bond_depth updated
# → attunement_level updated
```

---

## 🔧 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Response too generic | Persona not applied | Check `PersonaStyler` initialization |
| REMNANTS not updating | Bridge not called | Verify `_update_remnants_from_semantic()` executes |
| Quality score low | Blocks incompatible | Check `forbidden_with` rules in composition engine |
| Pacing not adapting | Continuity not tracked | Verify `ContinuityEngine.update_from_semantic_layer()` |
| Same response for all NPCs | Style guide incomplete | Expand block style guides in `PersonaStyler` |
| REMNANTS fields wrong | Mapping incorrect | Check `RemnantsSemanticBridge` mapping ratios |

---

## 📈 Next Steps

1. **Implement** integration checklist (Week 1)
2. **Test** with refined test harness (Week 1)
3. **Monitor** live gameplay for quality (Week 2)
4. **Tune** persona voices based on gameplay (Week 2-3)
5. **Expand** block library as patterns emerge (Ongoing)
6. **Integrate** REMNANTS ritual system with emotional arcs (Week 4)
7. **Publish** analytics on emotional arcs (Week 4+)

---

## 🌟 The Payoff

Once integrated, you have:

✅ **NPCs with emotional intelligence** - They respond to meaning, not keywords  
✅ **Emergent dialogue** - No two conversations identical  
✅ **Coherent emotional physics** - Semantic engine = Velinor's OS  
✅ **REMNANTS as living system** - Updated by every interaction  
✅ **Analytics on connection** - Measure emotional arcs, not just story beats  
✅ **World-wide consistency** - Same emotional logic everywhere  
✅ **Player modeling** - Deep understanding of emotional state  

**Velinor becomes emotionally alive.**

