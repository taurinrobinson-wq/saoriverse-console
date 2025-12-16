# Phase 2.3 Integration Guide

Wiring the Repair Module into the Response Pipeline.

## Overview

This guide explains how to integrate the repair module and orchestrator into the main response
engine for end-to-end correction detection and learning.

### Current Architecture

- `repair_module.py`: Core rejection detection and learning framework
- `repair_orchestrator.py`: Integration layer connecting modules
- `glyph_response_composer.py`: Conversational glyph-aware responses
- `integration_orchestrator.py`: Main Phase 1 conversation pipeline

## Integration Flow

### 1. Session Initialization

Create RepairOrchestrator when user session starts.

```python
from emotional_os.core.firstperson.repair_orchestrator import RepairOrchestrator

if "repair_orchestrator" not in st.session_state:
    st.session_state.repair_orchestrator = RepairOrchestrator(
        user_id=st.session_state.user_id
```text
```text
```

### 2. Response Generation

Generate response and record glyph context.

```python

response_text = glyph_composer.compose_glyph_aware_response(
    tone=detected_tone,
    arousal=arousal,
    valence=valence,
    glyph_name=selected_glyph
)

context = GlyphCompositionContext(
    tone=detected_tone,
    arousal=arousal,
    valence=valence,
    glyph_name=selected_glyph,
    user_id=user_id
)

st.session_state.repair_orchestrator.record_response(response_text)

```text
```

### 3. Next Turn - Detect Corrections

At start of next turn, analyze for rejections.

```python
repair_analysis = st.session_state.repair_orchestrator.analyze_for_repair( user_input=user_input )

if repair_analysis.is_rejection:
    # User rejected previous response
suggested_glyph = repair_analysis.suggested_alternative correction_hint =
repair_analysis.user_correction else:
    # Record acceptance
if st.session_state.last_glyph_context: st.session_state.repair_orchestrator.record_acceptance(
st.session_state.last_glyph_context
```text
```text
```

### 4. Generate Response with Alternative (if rejected)

Use suggested glyph if available.

```python

if repair_analysis.is_rejection:
    # Acknowledge correction
if repair_analysis.user_correction: response = f"I hear that—{repair_analysis.user_correction}.
{response}"

    # Use suggested glyph
if suggested_glyph: response = glyph_composer.compose_glyph_aware_response( tone=detected_tone,
arousal=arousal, valence=valence, glyph_name=suggested_glyph

```text
```

## Session State Variables

Track these in Streamlit session state:

```python
st.session_state.repair_orchestrator    # RepairOrchestrator instance
st.session_state.last_glyph_context     # GlyphCompositionContext from last response
```text
```text
```

## Testing Integration

1. **Unit tests**: Use `test_repair_module.py` and `test_repair_orchestrator.py` 2. **Integration
tests**: Create `test_repair_integration.py` for end-to-end flows 3. **Manual testing**: Test full
correction workflow in Streamlit app

## Phase 2.3 Checklist

- [x] `repair_module.py`: Core framework (368 lines)
- [x] `repair_orchestrator.py`: Integration layer (272 lines)
- [x] `test_repair_module.py`: 27 comprehensive tests
- [x] `test_repair_orchestrator.py`: 16 orchestrator tests
- [ ] Integration into `integration_orchestrator.py`
- [ ] Integration tests for full workflow
- [ ] Streamlit session state wiring
- [ ] Manual QA of correction detection
- [ ] Documentation with examples
- [ ] Optional: UI for preference visibility

## Example Complete Workflow

```python

def handle_conversation_turn(user_input: str) -> str:
    orch = st.session_state.repair_orchestrator

    # Detect if user is correcting previous response
    repair = orch.analyze_for_repair(user_input)

    if repair.is_rejection:
        if st.session_state.last_glyph_context:
            # Record the rejection (orchestrator does this internally)
            pass
        glyph = repair.suggested_alternative or default_glyph
    else:
        # Record acceptance of previous response
        if st.session_state.last_glyph_context:
            orch.record_acceptance(st.session_state.last_glyph_context)

        # Use best glyph for this state
        affect = affect_parser.parse(user_input)
        glyph = orch.get_best_glyph_for_state(
            affect["tone"],
            affect["arousal"],
            affect["valence"]
        ) or default_glyph

    # Generate response
    response = glyph_composer.compose_glyph_aware_response(
        tone=affect["tone"],
        arousal=affect["arousal"],
        valence=affect["valence"],
        glyph_name=glyph
    )

    # Record for next turn
    context = GlyphCompositionContext(
        tone=affect["tone"],
        arousal=affect["arousal"],
        valence=affect["valence"],
        glyph_name=glyph,
        user_id=st.session_state.user_id
    )
    orch.record_response(response)
    st.session_state.last_glyph_context = context

    return response

```

## Test Results

- Total tests: 262 (219 baseline + 27 repair + 16 orchestrator)
- All passing with zero regressions
- Coverage: Rejection detection, learning, preference tracking, integration

## Next Steps

1. Integrate orchestrator into `integration_orchestrator.py` 2. Add affect parser output to glyph
selection 3. Wire session state in Streamlit app 4. Create integration test suite 5. Manual QA of
full workflow
