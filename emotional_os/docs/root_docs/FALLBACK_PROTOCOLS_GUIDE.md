# Fallback Protocols Integration Guide

## Overview

Fallback Protocols is a tone-aware system that prevents over-triggering, misinterpretation, and forced presence. It handles:

- **Ambiguous Tone Detection**: Mixed signals (e.g., "I'm fine" + voltage signals)
- **Trigger Misfire Detection**: False positives (e.g., sarcastic "stay")
- **Overlapping Trigger Handling**: Multiple signals with priority resolution
- **Silence Protocol**: Respectful waiting without prompting

## Components

### 1. ToneAnalyzer
Detects contradictory emotional signals in text.

```python
analyzer = ToneAnalyzer()

# Detect ambiguous tone
is_ambiguous, reason, confidence = analyzer.detect_ambiguity(
    "I'm fine, but honestly I feel so alone"
)
# Returns: (True, "Mixed signals: dismissal + voltage", 0.85)

# Detect trigger misfire  
is_misfire, reason = analyzer.detect_misfire(
    "stay",
    "Yeah sure, 'stay' with me because that's worked so well before"
)
# Returns: (True, "Sarcasm detected around 'stay'...")
```

### 2. GlyphStateManager
Manages state transitions and voice modulation.

```python
manager = GlyphStateManager()

# Transition to new state
transition = manager.transition_to(GlyphState.TONE_LOCK)
# Glyph state: TONE_LOCK
# Voice: "Low, steady • Slow • Protective, grounding"

# Get voice profile for any state
profile = manager.get_voice_profile(GlyphState.VOLTAGE_DETECTED)
# Tone: "Raw, unfiltered"
# Cadence: "Variable"
# Texture: "Unflinching, holds ache without dilution"

# Enter silence protocol
manager.hold_breath()
# Glyph: minimal animation, companion waits
```

### 3. FallbackProtocol (Main Orchestrator)
Coordinates all components for complete exchange processing.

```python
protocol = FallbackProtocol()

result = protocol.process_exchange(
    user_text="I'm fine, but I feel alone",
    detected_triggers=None
)

# Result structure:
{
    "user_text": "I'm fine, but I feel alone",
    "timestamp": "2024-01-15T10:30:00.123456",
    "detections": {
        "ambiguity": {
            "detected": True,
            "reason": "Mixed signals: dismissal + voltage",
            "confidence": 0.85
        },
        "misfires": [],
        "overlapping_triggers": False
    },
    "glyph_response": {
        "animation": "pause with soft pulse",
        "state": "paused",
        "visual": "Glyph pauses, soft pulse",
        "meaning": "System acknowledges uncertainty"
    },
    "companion_behavior": {
        "behavior": "ask for clarification",
        "message": "Do you want me to stay silent or stay close? No assumption.",
        "tone": "gentle, offering choice"
    },
    "decisions": {
        "should_lock_trigger": False,
        "should_wait": True,
        "should_ask_clarification": True,
        "should_explain_misfire": False
    }
}
```

## Glyph States & Voice Profiles

### 1. TONE_LOCK
**Meaning**: Trigger is locked, companion committed to presence.
- **Tone**: Low, steady
- **Cadence**: Slow
- **Texture**: Protective, grounding, like a vow spoken in dim light
- **Use**: After valid trigger when user chooses emotional support

### 2. VOLTAGE_DETECTED
**Meaning**: High emotional intensity detected, companion responds raw.
- **Tone**: Raw, unfiltered
- **Cadence**: Variable
- **Texture**: Unflinching, holds ache without dilution
- **Use**: When user is in active pain/crisis (overrides ritual if conflict)

### 3. REPAIR_RECONNECTION
**Meaning**: Healing/recovery phase, companion gently supports.
- **Tone**: Warm, gentle
- **Cadence**: Slow, patient
- **Texture**: Devotional, like a hand placed on a shoulder
- **Use**: After acknowledgment, during recovery/support

### 4. RUPTURE_CONFLICT
**Meaning**: Boundary or conflict phase, companion is clear and firm.
- **Tone**: Clear, firm
- **Cadence**: Measured, deliberate
- **Texture**: Boundary-coded, holds line without cruelty
- **Use**: When firm boundaries needed or conflict exists

### 5. LEGACY_ARCHIVE
**Meaning**: Historical/retrospective mode, companion is reverent.
- **Tone**: Reverent, quiet
- **Cadence**: Slow, spacious
- **Texture**: Sacred, like prayer held in silence
- **Use**: When reflecting on past patterns or archival content

## Integration Points

### In UI Response Pipeline

```python
from emotional_os.safety.fallback_protocols import FallbackProtocol

class UIController:
    def __init__(self):
        self.protocol = FallbackProtocol()
    
    def process_user_input(self, user_text: str, detected_triggers: list):
        # Run fallback protocols
        protocol_result = self.protocol.process_exchange(
            user_text=user_text,
            detected_triggers=detected_triggers
        )
        
        # Check for issues
        if protocol_result["decisions"]["should_ask_clarification"]:
            # Use companion message instead of standard response
            return protocol_result["companion_behavior"]["message"]
        
        if protocol_result["decisions"]["should_lock_trigger"]:
            # Enter silence protocol - wait for next user message
            self.ui_state["waiting_for_response"] = True
        
        # Apply voice modulation to response
        return apply_voice_profile(
            response_text,
            glyph_state=protocol_result["glyph_response"]["state"]
        )
```

### Streamlit Integration

```python
import streamlit as st
from emotional_os.safety.fallback_protocols import FallbackProtocol

protocol = FallbackProtocol()

# User input
user_message = st.text_area("Your message:")
detected_triggers = detect_triggers(user_message)

# Process through fallback protocols
result = protocol.process_exchange(user_message, detected_triggers)

# Display glyph response
st.write(f"**Glyph**: {result['glyph_response']['visual']}")

# Display companion behavior
if result["companion_behavior"]["message"]:
    st.write(f"**Companion**: {result['companion_behavior']['message']}")

# Show detections for transparency
with st.expander("Protocol Details"):
    st.json(result["detections"])
    st.json(result["decisions"])
```

## Key Behaviors

### Ambiguous Tone
**Detected When**: Mixed signals (dismissal + voltage keywords)
- Example: "I'm fine, but I feel so alone"
- **Glyph Response**: Pause with soft pulse
- **Companion Response**: Asks for clarification without assumption
- **Decision**: Wait, ask clarification, do NOT lock trigger

### Trigger Misfire  
**Detected When**: Phrase matches trigger but tone contradicts
- Example: "Yeah sure, 'stay' with me" (sarcastic)
- **Glyph Response**: Flicker then reset
- **Companion Response**: Explains misfire, respects boundary
- **Decision**: Do NOT lock trigger

### Overlapping Triggers
**Detected When**: Multiple triggers in rapid succession
- Example: "I need to heal and move forward" (multiple action triggers)
- **Glyph Response**: Hold last confirmed state
- **Companion Response**: Prioritizes most emotionally charged ("voltage overrides ritual")
- **Decision**: Lock only highest priority trigger

### Post-Trigger Silence
**Detected When**: Trigger locked but user goes silent
- **Glyph Response**: Hold breath (minimal animation)
- **Companion Response**: Wait message without prompting
- **Decision**: Do NOT assume or push - companion holds presence in silence

## Protocol Scenarios

### Scenario 1: Mixed Emotions
```
User: "I'm fine, but honestly I feel so alone right now"
→ Ambiguous Tone Detected
→ Glyph: Pauses, soft pulse
→ Companion: "Do you want me to stay silent or stay close? No assumption."
→ Awaits user clarification
```

### Scenario 2: Sarcastic Rejection
```
User: "Yeah sure, 'stay' with me because that's worked so well before"
→ Trigger Misfire Detected (sarcasm)
→ Glyph: Flickers, then resets
→ Companion: "Tone mismatch. I won't lock unless it's chosen."
→ Respects user's actual boundary
```

### Scenario 3: Multiple Signals
```
User: "I'm struggling but I need to heal and move forward"
→ Overlapping Triggers Detected (struggle, heal, move)
→ Glyph: Holds last confirmed state
→ Companion: "I hear the strongest signal. Moving there."
→ Prioritizes highest emotional intensity
```

### Scenario 4: Confirmed Trigger + Silence
```
User: "I need to stay."
[User goes silent]
→ Trigger Locked, Silence Detected
→ Glyph: Holds breath (minimal animation)
→ Companion: "I'll stay until you speak again."
→ No prompting, no performance - just presence
```

## Testing

Run comprehensive test suite:

```bash
python3 -m pytest tests/test_fallback_protocols.py -v
```

Tests cover:
- Tone ambiguity detection (7 tests)
- Glyph state management (6 tests)
- Protocol orchestration (6 tests)
- Edge cases and integration

All tests pass: ✅ 19/19

## Philosophy

> "No assumption. The system feels what's happening and responds without forcing presence into absence."

Key principles:
1. **Respect user agency** - Don't lock triggers unless tone + phrase both confirm
2. **Detect contradiction** - Ambiguous tone → ask, don't assume
3. **Hold boundaries** - Respect sarcasm and explicit negation
4. **Voltage overrides ritual** - When conflict exists, prioritize raw emotion
5. **Silence is sacred** - After confirmation, wait without performing

## Files

- `emotional_os/safety/fallback_protocols.py` - Core implementation (600+ lines)
- `tests/test_fallback_protocols.py` - Comprehensive test suite (19 tests)
- Commit: 6c615fe
