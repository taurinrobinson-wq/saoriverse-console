# ARCHITECTURAL INTEGRATION GUIDE

## System Architecture Overview

The refined semantic parsing system consists of **5 independent modules** that work together as a pipeline to transform user input into contextually appropriate, emotionally attuned responses.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│ USER MESSAGE                                                          │
└────────────────────────┬─────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │ SEMANTIC PARSER                │
        │ (semantic_parsing_schema.py)   │
        │                                │
        │ Input: User message text       │
        │ Output: SemanticLayer (7 layers)
        │ - Emotional stance             │
        │ - Disclosure pacing            │
        │ - Conversational moves         │
        │ - Power dynamics               │
        │ - Identity signals             │
        │ - Emotional contradictions     │
        │ - Implied needs                │
        └────────────┬────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌─────────────┐    ┌──────────────────┐
    │ ACTIVATION  │    │ CONTINUITY       │
    │ MATRIX      │    │ ENGINE           │
    │ (activation │    │ (continuity_     │
    │ _matrix.py) │    │ engine.py)       │
    │             │    │                  │
    │ Input: 7    │    │ Input: Semantic  │
    │ layers      │    │ Layer + message  │
    │             │    │ index            │
    │ Output:     │    │                  │
    │ BlockTypes  │    │ Output: Updated  │
    │ to activate │    │ continuity state │
    └──────┬──────┘    └────────┬─────────┘
           │                    │
           └──────────┬─────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │ PRIORITY WEIGHTING SYSTEM       │
        │ (priority_weighting.py)         │
        │                                 │
        │ Input: BlockTypes + semantics   │
        │                                 │
        │ Process:                        │
        │ 1. Extract priority elements    │
        │ 2. Calculate override rules     │
        │ 3. Remove conflicts             │
        │                                 │
        │ Output: Ordered BlockTypes      │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ RESPONSE COMPOSITION ENGINE     │
        │ (response_composition_engine.py)│
        │                                 │
        │ Input:                          │
        │ - Ordered BlockTypes            │
        │ - Safety requirements           │
        │ - Pacing requirements           │
        │                                 │
        │ Process:                        │
        │ 1. Fetch blocks from library    │
        │ 2. Check forbidden combinations │
        │ 3. Compose response text        │
        │ 4. Calculate quality metrics    │
        │                                 │
        │ Output: ComposedResponse        │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ FINAL OUTPUT                    │
        │                                 │
        │ Generated Response:             │
        │ - Full text                     │
        │ - Block composition             │
        │ - Safety level                  │
        │ - Attunement level              │
        │ - Pacing appropriateness        │
        │ - Quality metrics               │
        └─────────────────────────────────┘
```

---

## Module Specifications

### 1. SEMANTIC PARSER
**File**: `semantic_parsing_schema.py`

**Purpose**: Extracts all 7 semantic layers from raw user message text.

**Input**: 
- `message: str` - User message text
- `message_index: int` - Position in conversation (0-indexed)

**Output**: 
- `SemanticLayer` dataclass containing:
  - `emotional_stance: EmotionalStance` - 8 enumerated stances
  - `disclosure_pace: DisclosurePace` - 5 enumerated paces
  - `conversational_moves: List[ConversationalMove]` - What user is doing
  - `identity_signals: SemanticIdentitySignal` - Who/what user references
  - `power_dynamics: List[PowerDynamic]` - Agency patterns
  - `implied_needs: List[ImpliedNeed]` - Unstated requirements
  - `emotional_contradictions: List[EmotionalContradiction]` - Paradoxes
  - `meta_properties: Dict` - Weight, trust increase, readiness signals

**Key Methods**:
```python
parser = SemanticParser()
layer = parser.parse(message="text...", message_index=0)
# Returns SemanticLayer with all 7 layers extracted
```

**Critical Outputs**:
- `emotional_stance.value` → Used by activation matrix for stance rules
- `disclosure_pace.value` → Used for pacing block activation
- `emotional_contradictions` → Triggers ambivalence blocks
- `power_dynamics` → Triggers identity injury blocks
- `meta_properties["emotional_weight"]` → Determines response depth
- `meta_properties["ready_to_go_deeper"]` → Determines readiness for gentle direction

---

### 2. ACTIVATION MATRIX
**File**: `activation_matrix.py`

**Purpose**: Maps semantic layer attributes to response block types using deterministic rules.

**Input**: 
- Semantic layer attributes (stance, pacing, moves, dynamics, needs, contradictions, etc.)

**Output**: 
- `Set[BlockType]` - Which blocks to activate

**Key Method**:
```python
blocks = ActivationMatrix.compute_full_activation(
    emotional_stance="bracing",
    disclosure_pacing="testing_safety",
    conversational_moves=["testing_safety"],
    power_dynamics=["self_protection"],
    implied_needs=["containment", "pacing"],
    emotional_contradictions_present=False,
    emotional_weight=0.4,
    has_impact_words=False,
    identity_signal_count=0,
    ready_to_go_deeper=False,
)
# Returns: {BlockType.CONTAINMENT, BlockType.PACING}
```

**Rules Tables**:
- 7 mapping tables define which blocks activate for each semantic attribute
- All mappings are deterministic and testable
- Example: If `emotional_stance == "ambivalent"` → activate `{BlockType.AMBIVALENCE, BlockType.ACKNOWLEDGMENT}`

**Validation**:
```python
BlockActivationValidator.validate_forbidden_absence(
    blocks,
    message_index=0
)
# Ensures rules like "GENTLE_DIRECTION only after message 3"
```

---

### 3. CONTINUITY ENGINE
**File**: `continuity_engine.py`

**Purpose**: Tracks emotional and relational progression across turns. Ensures each message builds on previous context.

**Input**: 
- `SemanticLayer` from parser + message index

**Output**: 
- Updated `ConversationContinuity` state

**Key Methods**:
```python
engine = ContinuityEngine()

# After each message is parsed
engine.update_from_semantic_layer(semantic_layer, message_index=0)

# After each response is generated
engine.record_response_quality(safety_level=0.7, attunement_level=0.5)

# Query continuity state
stance_arc = engine.get_stance_arc()
# Returns: ["bracing", "revealing", "revealing", "ambivalent"]

trust_level = engine.get_trust_level()
# Returns: 0.65

contradictions = engine.get_active_contradictions()
# Returns: ["relief vs grief", "clarity vs uncertainty"]

summary = engine.get_conversation_summary()
# Returns complete continuity state for logging
```

**Continuity Elements Tracked**:
- Emotional stance progression (arc)
- Disclosure pace progression (arc)
- Trust development (0.0-1.0 scale)
- Named individuals (accumulated)
- Duration markers ("10 years", "18 years")
- Active contradictions (carried forward)
- Agency loss trajectory
- Pacing needs evolution
- Response quality trend

**Why It Matters**:
- System can recognize when user builds on previous messages
- Can track contradictions across turns (e.g., relief on turn 3, grief acknowledgment needed on turn 4)
- Can identify progression (e.g., safety testing → naming → full vulnerability)

---

### 4. PRIORITY WEIGHTING SYSTEM
**File**: `priority_weighting.py`

**Purpose**: Implements 8-level priority stack. Determines which semantic elements take precedence.

**Priority Stack** (highest to lowest):
1. **Safety / Containment** - If user needs grounding, everything else waits
2. **Pacing** - If user needs slowing, depth exploration is suppressed
3. **Contradictions** - Emotional paradoxes must be honored
4. **Identity Injury** - Agency loss and wound markers must be acknowledged
5. **Emotional Stance** - Overall emotional posture
6. **Conversational Move** - What user is strategically doing
7. **Disclosure Pacing** - How quickly user is revealing
8. **Contextual Details** - Lowest priority

**Key Concept**: Higher-priority elements can *override* lower-priority ones.

Example: If user is in safety-testing (priority 1) and has a contradiction (priority 3), safety blocks activate and contradiction blocks are suppressed until safety is established.

**Input**:
- All semantic layer attributes

**Output**:
- `List[PriorityElement]` - Ordered priority elements
- `Dict[BlockType, int]` - Block priority mapping

**Key Method**:
```python
elements = PriorityWeightingSystem.extract_priority_elements(
    emotional_stance="bracing",
    disclosure_pacing="testing_safety",
    # ... all semantic attributes ...
    needs_pace_slowing=True,
)
# Returns ordered list of PriorityElements

block_priorities = PriorityWeightingSystem.compute_block_activation_with_priorities(
    elements
)
# Returns {BlockType.CONTAINMENT: 1, BlockType.PACING: 2}

ordered = PriorityWeightingSystem.get_ordered_blocks(block_priorities)
# Returns [BlockType.CONTAINMENT, BlockType.PACING]
```

---

### 5. RESPONSE COMPOSITION ENGINE
**File**: `response_composition_engine.py`

**Purpose**: Assembles responses from semantic blocks. No templates—only composable units.

**Block Library** (8 types):

| BlockType | Examples | When Activated | Purpose |
|-----------|----------|----------------|---------|
| CONTAINMENT | "I'm here with you." "Take your time." | Safety needs | Create safety, ground |
| VALIDATION | "That makes sense." "This matters." | Validation needs | Affirm experience |
| PACING | "We can take this slowly." | Pace slowing needs | Control tempo |
| ACKNOWLEDGMENT | "I hear you." "That's significant." | Reflecting needs | Show understanding |
| AMBIVALENCE | "It's okay to feel two things." | Contradictions present | Hold paradoxes |
| TRUST | "Thank you for sharing." | Disclosure progression | Reinforce safety |
| IDENTITY_INJURY | "That took something from you." | Agency loss present | Acknowledge wound |
| GENTLE_DIRECTION | "What part feels most present?" | Ready to explore | Open next steps |

**Input**:
- `activated_blocks: List[BlockType]` - Which blocks to use
- `priorities: Dict[BlockType, int]` - Block order
- `safety_required: bool` - Whether safety blocks are mandatory
- `pacing_required: str` - "slow", "moderate", or "deep"

**Output**:
- `ComposedResponse` containing:
  - `blocks: List[ResponseBlock]` - Activated blocks
  - `full_text: str` - Composed response
  - `safety_level: float` - 0.0-1.0 quality metric
  - `attunement_level: float` - 0.0-1.0 quality metric
  - `pacing_appropriate: bool` - Whether pace matches requirement
  - `contains_forbidden_content: bool` - Whether response has analysis/advice/interrogation

**Key Method**:
```python
engine = ResponseCompositionEngine()

response = engine.compose(
    activated_blocks=[
        BlockType.CONTAINMENT,
        BlockType.PACING,
    ],
    priorities={
        BlockType.CONTAINMENT: 1,
        BlockType.PACING: 2,
    },
    safety_required=True,
    pacing_required="slow"
)

print(response.full_text)
# Output: "I'm here with you. Take your time with this."

print(f"Safety: {response.safety_level:.1%}")  # 0.9
print(f"Attunement: {response.attunement_level:.1%}")  # 0.5
print(f"Pacing OK: {response.pacing_appropriate}")  # True
```

---

## Integration Points

### Where Each Module Connects

```python
# STEP 1: USER MESSAGE ARRIVES
user_message = "I'm glad it's over because it was not good, but I don't know…"
message_index = 3

# STEP 2: PARSE SEMANTICALLY
parser = SemanticParser()
semantic_layer = parser.parse(user_message, message_index)
# semantic_layer.emotional_stance = EmotionalStance.AMBIVALENT
# semantic_layer.implied_needs = [ImpliedNeed.VALIDATION, ImpliedNeed.ATTUNEMENT]
# semantic_layer.emotional_contradictions = [relief vs grief, clarity vs uncertainty]

# STEP 3: UPDATE CONTINUITY
continuity = ContinuityEngine()
continuity.update_from_semantic_layer(semantic_layer, message_index)
# Tracks that this is 4th message (ambivalent)
# Carries forward contradictions from previous turns
# Updates trust level

# STEP 4: DETERMINE BLOCK ACTIVATION
blocks = ActivationMatrix.compute_full_activation(
    emotional_stance=semantic_layer.emotional_stance.value,
    disclosure_pacing=semantic_layer.disclosure_pace.value,
    conversational_moves=[m.value for m in semantic_layer.conversational_moves],
    power_dynamics=[d.value for d in semantic_layer.power_dynamics],
    implied_needs=[n.value for n in semantic_layer.implied_needs],
    emotional_contradictions_present=len(semantic_layer.emotional_contradictions) > 0,
    # ... other parameters ...
)
# blocks = {
#     BlockType.VALIDATION,
#     BlockType.AMBIVALENCE,
#     BlockType.IDENTITY_INJURY,
#     BlockType.ACKNOWLEDGMENT,
# }

# STEP 5: APPLY PRIORITY WEIGHTING
priority_system = PriorityWeightingSystem()
elements = priority_system.extract_priority_elements(
    emotional_stance=semantic_layer.emotional_stance.value,
    # ... pass all semantic attributes ...
)
# Contradictions (priority 3) override identity injury (priority 4)
# Identity injury (priority 4) overrides stance (priority 5)

block_priorities = priority_system.compute_block_activation_with_priorities(elements)
# {
#     BlockType.AMBIVALENCE: 3,      # Contradiction priority
#     BlockType.VALIDATION: 4,       # Identity injury priority
#     BlockType.IDENTITY_INJURY: 4,
#     BlockType.ACKNOWLEDGMENT: 5,   # Stance priority
# }

# STEP 6: COMPOSE RESPONSE
composition = ResponseCompositionEngine()
composed = composition.compose(
    activated_blocks=list(blocks),
    priorities=block_priorities,
    safety_required=False,  # Not testing safety anymore
    pacing_required="deep"  # Ready for deeper exploration
)
# composed.full_text = 
# "You're holding two contradictions at once. The clarity—it was not good,
#  she undermined you, and you're glad it's over. That's all true.
#  And underneath that... the 'but I don't know...' And I think what you 
#  don't know isn't about the relationship anymore. It's about yourself..."

# STEP 7: RECORD QUALITY
continuity.record_response_quality(
    safety_level=composed.safety_level,
    attunement_level=composed.attunement_level,
)

# STEP 8: RETURN TO USER
return composed.full_text
```

---

## Data Flow Summary

```
Message Text
    ↓
[SemanticParser] → SemanticLayer (7 layers)
    ↓
    ├→ [ContinuityEngine] → Updated state + story context
    │
    └→ [ActivationMatrix] → Set[BlockType]
        ↓
        [PriorityWeighting] → Ordered BlockTypes with overrides
        ↓
        [CompositionEngine] → ComposedResponse (text + metrics)
        ↓
        → [ContinuityEngine] → Record quality delivered
        ↓
    Return to User
```

---

## Testing Integration

The **refined_test_harness.py** validates the entire pipeline:

```python
harness = RefinedSemanticTestHarness()
results = harness.run_full_test()

# Validates:
# 1. Semantic accuracy ≥80%
# 2. Block activation accuracy 100%
# 3. Response quality ≥90%
# 4. Continuity awareness ✓ all fields updated
# 5. Contradiction-holding ✓ Message 4
# 6. Pacing appropriateness ✓ Slow 1-3, Deep 4
# 7. Safety/attunement metrics ✓ tracked
```

---

## Integration Checklist

To integrate into existing system:

- [ ] **Import modules** into response handler
- [ ] **Initialize parsers/engines** at application start
- [ ] **Parse user message** → get SemanticLayer
- [ ] **Update continuity** with semantic layer
- [ ] **Get block activation** from matrix
- [ ] **Apply priority weighting** to blocks
- [ ] **Compose response** from blocks
- [ ] **Record quality** in continuity
- [ ] **Return composed response** to user
- [ ] **Log all metrics** (safety, attunement, pacing, etc.)

---

## Key Architectural Principles

1. **Separation of Concerns**: Each module has single responsibility
2. **Deterministic Behavior**: All mappings and rules are testable
3. **Composability**: Response blocks are independently valid
4. **Continuity Awareness**: System remembers and builds on context
5. **Priority-Based Resolution**: Conflicts resolved by priority stack
6. **Metrics-Driven**: Every response tracked for quality
7. **No Templates**: Only semantic composition
8. **State Tracking**: Emotional progression visible throughout

---

## Performance Characteristics

- **Parsing**: O(n) where n = message length
- **Activation**: O(1) - lookup tables
- **Priority Weighting**: O(m) where m = semantic elements
- **Composition**: O(k) where k = activated blocks
- **Total Pipeline**: Sub-millisecond for typical messages

---

## Future Enhancements

1. **Adaptive Block Library**: Learn effective block combinations
2. **Contradiction Tracking Visualization**: Show user emotional arcs
3. **Multi-turn Contradiction Resolution**: Track contradictions across many turns
4. **Contextual Block Variations**: Different phrasing based on identity markers
5. **Safety Threshold Adjustment**: Dynamic safety requirements based on history
6. **Agency Reclamation Scoring**: Explicit tracking of user agency work

---
