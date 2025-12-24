# FirstPerson Pipeline Specification

## Overview
The FirstPerson response pipeline is a composable, typed system that converts user messages into semantically attuned, contextually grounded responses. It enforces invariants at each stage to prevent canned, overly-celebratory, or verbatim-echo replies.

## Component Interfaces

### 1. TurnClassifier
**Purpose:** Deterministic classification of message intent and emotional context.

**Input:**
```python
{
    "message": str,
    "conversation_history": List[dict],  # [{role: "user"|"assistant", content: str}]
    "user_id": str,
}
```

**Output:**
```python
{
    "turn_type": "disclosure" | "gratitude" | "meta" | "closure" | "correction",
    "confidence": float,  # 0.0-1.0
    "emotional_signal": Optional[str],  # "grief", "exhaustion", "joy", None
    "reasoning": str,  # for debugging
}
```

**Invariants:**
- Always returns exactly one `turn_type`.
- `confidence >= 0.0`.
- Deterministic given the same input.

**Logic:**
- **disclosure**: User shares a struggle, feeling, or personal experience. Markers: "I feel", "I'm", emotional words, concrete struggle.
- **gratitude**: User expresses thanks or positive reflection. Markers: "thank you", "grateful", "appreciate".
- **meta**: User asks about the system, rules, or process. Markers: "how does", "can you", "do you".
- **closure**: User signals conversation end. Markers: "goodbye", "thanks for", "that helps", "bye".
- **correction**: User corrects prior statement or asks for re-framing. Markers: "actually", "wait", "I meant", "no that's not".

---

### 2. DomainExtractor
**Purpose:** Extract emotional domains (exhaustion, stress, blocked_joy, etc.) from message.

**Input:**
```python
{
    "message": str,
    "affect": Optional[dict],  # {tone, valence, arousal} from pipeline
}
```

**Output:**
```python
{
    "exhaustion": float,    # 0.0-1.0
    "stress": float,
    "blocked_joy": float,
    "contrast": float,      # feeling out-of-sync with surroundings
    "temporal_pressure": float,  # time-sensitive concern
    "disappointment": float,
    "isolation": float,
}
```

**Invariants:**
- All values are floats in [0.0, 1.0].
- Sum of domains need not equal 1.0 (multiple can be present).
- Deterministic given input.

---

### 3. SemanticCompressor
**Purpose:** Synthesize domains and message into a concise, two-sentence reflection.

**Input:**
```python
{
    "domains": dict,  # from DomainExtractor
    "message": str,
    "conversation_context": Optional[str],
}
```

**Output:**
```python
{
    "reflection": str,  # max 2 sentences
    "reference_count": int,  # how many domains mentioned
}
```

**Invariants:**
- `reflection` contains at most 2 sentences (periods or newlines).
- `reflection` length < 200 characters.
- If a domain has score > 0.5, the reflection MUST reference or acknowledge it.
- No verbatim echo of the user message (avoid >3 consecutive words from user).

---

### 4. PolicyRouter
**Purpose:** Enforce global invariants and route to appropriate response generator.

**Input:**
```python
{
    "turn_type": str,  # from TurnClassifier
    "base_response": str,
    "domains": dict,  # from DomainExtractor
    "conversation_history": List[dict],
    "candidate_generators": List[str],  # ["template_composer", "compressor", "orchestrator"]
}
```

**Output:**
```python
{
    "allowed_generators": List[str],
    "invariants_pass": bool,
    "violations": List[str],  # if any
    "recommended_generator": str,
}
```

**Invariants Enforced:**
1. **Turn-Type Routing:**
   - `closure` → Use `template_composer` (wrap-up).
   - `gratitude` → Use `template_composer` (affirm).
   - `disclosure` → Use `compressor` (reflect domains).
   - `meta` → Use `orchestrator` (explain).
   - `correction` → Use `compressor` (refine).

2. **Response Length:**
   - Max 3 sentences for non-disclosure.
   - Max 4 sentences for disclosure.
   - Each sentence ≤ 25 words (except opening salvo which can be longer).

3. **Verbatim Echo:**
   - Response must not contain >3 consecutive user words.
   - Avoid repeating user's exact phrases without reframing.

4. **Domain Reference:**
   - If any domain score > 0.6, response MUST reference it (by name or proxy).
   - Example: "you're describing an exhaustion that..." references "exhaustion" domain.

5. **Affect Consistency:**
   - If user message is negative (valence < 0.4), response tone must match or gently raise it.
   - No celebratory appends for negative-valence turns.

---

### 5. ResponseGenerator Variants

#### TemplateComposer
**Input:**
```python
{
    "turn_type": str,
    "domains": dict,
    "conversation_context": str,
}
```

**Output:**
```python
{
    "text": str,  # 1-3 sentences
    "template_name": str,  # for analytics
    "glyph_intent": dict,
}
```

**Templates:**
- **Closure:** "Thank you for sharing. I'm here whenever you need to talk again."
- **Gratitude:** "I hear the appreciation in that. It means something that you can see that in yourself."
- **Meta:** "I work by listening deeply and reflecting back what I'm hearing. My goal is to meet you where you are, not to fix or advise."

#### CompressorComposer
**Input:**
```python
{
    "domains": dict,
    "message": str,
    "history": List[dict],
}
```

**Output:**
```python
{
    "text": str,  # via SemanticCompressor
    "domains_referenced": List[str],
    "glyph_intent": dict,
}
```

#### OrchestratorComposer
**Input:**
```python
{
    "message": str,
    "user_id": str,
    "conversation_history": List[dict],
}
```

**Output:**
```python
{
    "text": str,
    "memory_state": dict,
    "glyph_intent": dict,
}
```

---

## Data Flow Diagram

```
User Message
    ↓
TurnClassifier → {turn_type, confidence, emotional_signal}
    ↓
Pipeline (affect parsing) → {tone, valence, arousal}
    ↓
DomainExtractor → {exhaustion, stress, blocked_joy, ...}
    ↓
PolicyRouter → {allowed_generators, invariants_pass}
    ↓
Choose Generator (CompressorComposer | TemplateComposer | OrchestratorComposer)
    ↓
Generate Response (text, glyph_intent)
    ↓
Micro-Engines (PunInterjector, MutualJoyHandler) [GATED by affect + lexical cues]
    ↓
Final Response
```

---

## Example Scenarios

### Scenario 1: Exhaustion Disclosure
**User:** "I'm so tired of things right now... Christmas in two days."

**TurnClassifier output:**
```python
{
    "turn_type": "disclosure",
    "confidence": 0.95,
    "emotional_signal": "exhaustion",
    "reasoning": "Contains 'I'm', explicit fatigue language, temporal pressure (Christmas in two days)"
}
```

**DomainExtractor output:**
```python
{
    "exhaustion": 0.9,
    "temporal_pressure": 0.8,
    "stress": 0.7,
    "blocked_joy": 0.6,
    "contrast": 0.4,
    "disappointment": 0.3,
    "isolation": 0.2,
}
```

**PolicyRouter:**
- `turn_type="disclosure"` → recommended_generator = `CompressorComposer`
- Invariants check:
  - Domains > 0.6: exhaustion, temporal_pressure, stress, blocked_joy → must reference all.
  - Response length: ≤ 4 sentences OK.
  - Verbatim echo: avoid "Christmas in two days" or "so tired" unless reframed.

**Response (CompressorComposer):**
```
I hear you—the exhaustion that comes before the day does, compounded by the approaching pressure of Christmas. That's not just fatigue; it's the weight of time running out while you're already empty. I'm standing beside you in that. What's the part of this that's weighing on you most?
```

---

### Scenario 2: Gratitude Turn
**User:** "Thank you for listening. That actually helped a lot."

**TurnClassifier output:**
```python
{
    "turn_type": "gratitude",
    "confidence": 0.99,
    "emotional_signal": None,
    "reasoning": "Explicit 'thank you' + positive outcome signal"
}
```

**PolicyRouter:**
- `turn_type="gratitude"` → recommended_generator = `TemplateComposer`
- Use gratitude template.

**Response (TemplateComposer):**
```
I hear the appreciation in that. It means something that you can see the shift. I'm here whenever you need to talk again.
```

---

### Scenario 3: Meta Question
**User:** "How do you know what to say?"

**TurnClassifier output:**
```python
{
    "turn_type": "meta",
    "confidence": 0.98,
    "emotional_signal": None,
    "reasoning": "Direct question about system ("How do you"), meta-cognitive"
}
```

**PolicyRouter:**
- `turn_type="meta"` → recommended_generator = `OrchestratorComposer`

**Response (OrchestratorComposer):**
```
I listen deeply to what you're saying, then I reflect back what I'm hearing—the themes, the weight, the specific shape of your struggle. I'm not guessing; I'm responding to you. That's the core of how I work.
```

---

## Testing Invariants

Each component and the full pipeline should have unit tests asserting:

1. **TurnClassifier:**
   - Always returns exactly one turn_type.
   - Deterministic given same input.
   - High confidence (>0.8) for clear markers.
   - Distinguishes disclosure from meta (avoid false positives on "I think I should ask for help").

2. **DomainExtractor:**
   - All outputs in [0.0, 1.0].
   - Exhaustion marker correlates with exhaustion score > 0.5.
   - Multiple domains can be high simultaneously.

3. **SemanticCompressor:**
   - Output ≤ 2 sentences.
   - If domain > 0.6, it appears in output (by name or proxy concept).
   - No >3-word verbatim echo.

4. **PolicyRouter:**
   - Correct generator for each turn_type.
   - Detects verbatim echo violations.
   - Detects length violations.

5. **End-to-End:**
   - Exhaustion disclosure → compressor output < 4 sentences.
   - Gratitude turn → template response < 2 sentences.
   - No joy micro-engine append for negative-valence turns.
   - Response never echoes user verbatim.

---

## Implementation Notes

- All components are pure functions (deterministic, no side effects).
- Logging at each stage for debugging and telemetry.
- Timeouts: each component should complete in <100ms; full pipeline <500ms.
- Graceful fallback if any component fails (use prior stage output or base response).
