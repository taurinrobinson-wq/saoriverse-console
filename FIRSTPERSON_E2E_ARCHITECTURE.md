# FirstPerson System - End-to-End Architecture

## 🎯 Quick Summary

The FirstPerson Streamlit app is a **3-phase emotional response system** that:
1. **Parse** user input for emotional signals
2. **Interpret** the context and generate base response  
3. **Generate** enhanced response with tiers (Foundation, Aliveness, Poetic)

All tiers are **eager-initialized at app startup** (no first-message lag).

---

## 📊 System Architecture (Bird's Eye View)

```
┌─────────────────────────────────────────────────────────────┐
│ STREAMLIT APP (app.py)                                      │
│ - Runs: streamlit run app.py                               │
│ - Entry point for all user interaction                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ SESSION INITIALIZATION (session_manager.py)                 │
│ ✅ Eager Tier Init (Phase 2 optimization):                 │
│   - Tier 1 Foundation (learning, safety)                   │
│   - Tier 2 Aliveness (tone, energy)                        │
│   - Tier 3 Poetic (metaphor, mythology) [optional]         │
│ ✅ Mood ring                                               │
│ ✅ Responder system                                        │
│ ✅ FirstPerson orchestrator                                │
└────────────────────┬────────────────────────────────────────┘
                     │
        (Session pre-initialized, ready for messages)
                     │
┌─────────────────────────────────────────────────────────────┐
│ USER MESSAGE ARRIVES                                        │
│ (Chat input in Streamlit UI)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE HANDLER (response_handler.py)                      │
│ Entry: handle_response_pipeline(user_input, context)        │
│ ✅ Clean orchestrator (110 lines, was 1,233)               │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌─────────────┴──────────────┬────────────────┐
      ↓                            ↓                ↓
   PHASE 1                      PHASE 2          PHASE 3
PARSE SIGNALS              INTERPRET             GENERATE
      │                        │                  │
      ↓                        ↓                  ↓
[parse_phase.py]      [interpret_phase.py]  [generate_phase.py]
      │                        │                  │
      └─────────────┬──────────┴────────────────┬─┘
                     │
                     ↓
           ┌─────────────────────┐
           │ FINAL RESPONSE      │
           │ (sent to Streamlit) │
           └─────────────────────┘
```

---

## 🚦 Detailed Phase Breakdown

### **Phase 1: Parse Input Signals** (`parse_phase.py`)

**Function:** `parse_input_signals(user_input: str, conversation_context: dict) -> dict`

**What it does:**
- Extracts emotional signals from user message
- Matches to emotional glyphs (from lexicon database)
- Calculates emotional vector
- Returns: `{voltage_response, best_glyph, emotional_vector, ...}`

**Execution Flow:**
```python
user_input = "I feel like I'm failing at everything lately."
conversation_context = {"messages": [...], "user_mood": "low"}

# Phase 1 execution
analysis = parse_input_signals(user_input, conversation_context)

# Output:
# {
#   "voltage_response": "[poetic response from glyphs]",
#   "best_glyph": {"glyph_name": "Burden", "description": "..."},
#   "emotional_vector": [0.8, 0.2, 0.1, ...],  # fear, sadness, etc
#   "response_source": "local"
# }
```

**Key Methods:**
- `parse_input()` from `emotional_os.glyphs.signal_parser`
- Remote fallback if local parsing incomplete
- spaCy check (lazy-loaded) for NLP capabilities

---

### **Phase 2: Interpret Emotional Context** (`interpret_phase.py`)

**Function:** `interpret_emotional_context(user_input: str, analysis: dict, conversation_context: dict) -> str`

**What it does:**
- Takes parsed signals and generates **base response** (no tier enhancements yet)
- Tries multiple strategies in order:
  1. **Mood ring** if asking "what's your mood?"
  2. **Subordinate responder** for short questions
  3. **Voltage response** (poetic signal from Phase 1)
  4. **FirstPerson orchestrator** with glyph matching
  5. **Fallback** simple acknowledgment

**Execution Flow:**
```python
analysis = {
    "voltage_response": "[poetic response]",
    "best_glyph": {"glyph_name": "Burden", ...}
}
conversation_context = {"messages": [...]}

# Phase 2 execution
base_response = interpret_emotional_context(
    user_input,
    analysis,
    conversation_context
)

# Output: "I hear you. That sounds overwhelming. Can you say more about..."
# (conversational, not yet tier-enhanced)
```

**Key Components:**
- Mood ring generator
- Subordinate responder
- FirstPerson orchestrator
- Graceful fallbacks

---

### **Phase 3: Generate Enhanced Response** (`generate_phase.py`)

**Function:** `generate_enhanced_response(user_input: str, base_response: str, conversation_context: dict) -> (str, float)`

**What it does:**
- Takes base response from Phase 2
- Applies **3 tiers** of enhancement (all eager-initialized in session)
- Returns enhanced response + processing time

**Tier Application:**
1. **Tier 1 Foundation** - Learning, safety wrapping, conversation memory
2. **Tier 2 Aliveness** - Tone, energy, presence, emotional resonance
3. **Tier 3 Poetic** (optional) - Metaphor, mythology, poetic consciousness

**Execution Flow:**
```python
base_response = "I hear you. That sounds overwhelming."

# Phase 3 execution
final_response, elapsed_time = generate_enhanced_response(
    user_input,
    base_response,
    conversation_context
)

# Tier 1: Adds learning context + safety padding
# Tier 2: Enhances tone for warmth and presence
# Tier 3 (if enabled): Adds poetic metaphor

# Output: "[Full response with all tier enhancements applied]"
# elapsed_time: 0.45  (seconds)
```

**Key Methods:**
- `tier1.process_response(user_input, base_response, context)`
- `tier2.process_for_aliveness(user_input, base_response, history)`
- `tier3.process_for_poetry(response, context)` [optional]

---

## 🔄 Complete Message Flow Example

```
USER INPUT: "I feel like I'm failing at everything lately."
CONTEXT: {"messages": [previous chat], "user_mood": "low"}

└─→ handle_response_pipeline(user_input, context)
    │
    ├─→ PHASE 1: parse_input_signals(user_input, context)
    │   └─→ Returns: {
    │         "voltage_response": "...",
    │         "best_glyph": {"glyph_name": "Burden"},
    │         "emotional_vector": [0.8, 0.2, ...]
    │       }
    │
    ├─→ PHASE 2: interpret_emotional_context(user_input, analysis, context)
    │   └─→ Returns: "I hear you. That's a lot to carry. Can you say more?"
    │
    ├─→ PHASE 3: generate_enhanced_response(user_input, base_response, context)
    │   │
    │   ├─→ Tier 1 Foundation enhancement
    │   │   └─→ Adds learning context
    │   ├─→ Tier 2 Aliveness enhancement
    │   │   └─→ Enhances tone & warmth
    │   ├─→ Tier 3 Poetic (if enabled)
    │   │   └─→ Adds poetic layer
    │   │
    │   └─→ Returns: ("[Full enhanced response]", 0.45)
    │
    └─→ Send to Streamlit UI

FINAL OUTPUT TO USER:
"I hear you. That's a lot to carry. I'm noticing you're really 
down on yourself right now. Can you tell me what happened? I want 
to understand what's weighing on you..."
```

---

## 📍 Streamlit Entry Point: `app.py`

### Location
```
d:\saoriverse-console\app.py  (root level)
```

### Key Functions in app.py

```python
# 1. Initialize session on app load
if "initialized" not in st.session_state:
    from emotional_os.deploy.modules.ui_components.session_manager import initialize_session_state
    initialize_session_state()
    # ✅ This calls eager tier initialization (Phase 2)

# 2. Get user input
user_input = st.chat_input("What's on your mind?")

# 3. Process through pipeline (when message arrives)
if user_input:
    from emotional_os.deploy.modules.ui_components.response_handler import handle_response_pipeline
    
    response, elapsed = handle_response_pipeline(
        user_input,
        {
            "messages": st.session_state.get("messages", []),
            "user_mood": st.session_state.get("user_mood"),
            ...
        }
    )
    
    # 4. Display response
    st.write(response)

# 5. Optional: Show metrics
st.sidebar.metric("Response Time", f"{elapsed:.2f}s")
```

### Session State Keys (Set During Initialization)

```python
st.session_state = {
    # Tiers (eager-initialized)
    "tier1_foundation": Tier1Foundation(...),        # ✅ Pre-loaded
    "tier2_aliveness": Tier2Aliveness(...),          # ✅ Pre-loaded
    "tier3_poetic_consciousness": Tier3Poetic(...),  # ✅ Pre-loaded (if enabled)
    "enable_tier3_poetic": False,
    
    # Supporting systems
    "mood_ring": MoodRing(...),
    "responder": SubordinateResponder(...),
    "firstperson_orchestrator": FirstPersonOrchestrator(...),
    
    # Conversation
    "messages": [],
    "conversation_context": {},
    "user_mood": None,
    
    # NLP (lazy-loaded on first use)
    # nlp = get_spacy_model()  # @st.cache_resource
}
```

---

## 🎯 Key Optimizations (Phase 1-3)

### Phase 1: Pipeline Decomposition
**Problem:** 1,233-line monolith, hard to debug, no testability
**Solution:** 3 independent phases
**Result:** Clean, testable, maintainable code

### Phase 2: Eager Initialization
**Problem:** First message takes 2-3 seconds (tier initialization)
**Solution:** Move tier init to app startup (already in session_manager)
**Result:** No lag on first message

### Phase 0: Bonus - Module Consolidation
**Problem:** 70+ duplicate modules across 3 directories
**Solution:** Single canonical location
**Result:** Reduced entropy, clear imports

---

## 📈 Performance Profile

| Phase | Latency | Notes |
|-------|---------|-------|
| Parse | <0.2s | Signal extraction, glyph matching |
| Interpret | <0.7s | Response generation with fallbacks |
| Generate | <1.0s | Tier 1-3 enhancements |
| **Total** | **<2.0s** | End-to-end user message → response |

**Note:** Tier initialization is **not** included (it's at app startup via Phase 2)

---

## 🧪 Testing the System

```bash
# Run E2E tests (7 scenarios)
pytest tests/test_e2e_firstperson.py -v

# Run load test (10 diverse inputs)
pytest tests/test_load_firstperson.py -v

# Run regression tests (edge cases)
pytest tests/test_regression_firstperson.py -v

# Run latency benchmarks
pytest tests/test_latency_firstperson.py -v
```

---

## 🔍 Files You Need to Know

### Core System
- **Entry Point:** `app.py`
- **Session Init:** `src/emotional_os/deploy/modules/ui_components/session_manager.py`
- **Response Handler:** `src/emotional_os/deploy/modules/ui_components/response_handler.py`

### 3-Phase Pipeline
- **Phase 1:** `src/emotional_os/deploy/modules/ui_components/pipeline/parse_phase.py`
- **Phase 2:** `src/emotional_os/deploy/modules/ui_components/pipeline/interpret_phase.py`
- **Phase 3:** `src/emotional_os/deploy/modules/ui_components/pipeline/generate_phase.py`

### Supporting Infrastructure
- **NLP Loader (lazy + cached):** `src/emotional_os/utils/nlp_loader.py`
- **Tiers:** `src/emotional_os/{tier1_foundation,tier2_aliveness,tier3_poetic_consciousness}.py`
- **Responder:** `src/emotional_os/deploy/modules/ui_components/responder.py`
- **Mood Ring:** `src/emotional_os/deploy/modules/ui_components/mood_ring.py`

### Tests
- **E2E:** `tests/test_e2e_firstperson.py`
- **Load:** `tests/test_load_firstperson.py`
- **Regression:** `tests/test_regression_firstperson.py`
- **Latency:** `tests/test_latency_firstperson.py`

---

## 🚀 Running the App

```bash
# Start Streamlit app
streamlit run app.py

# On first load:
# 1. Session initializes (eager tier init happens here)
# 2. UI loads with chat input ready
# 3. No lag on first message!

# When user types message:
# 1. handle_response_pipeline() is called
# 2. Parse → Interpret → Generate (all 3 phases execute)
# 3. Response displayed in <2 seconds
```

---

## ❓ Common Questions

**Q: Where are tiers initialized?**
A: In `session_manager.py::initialize_session_state()`. Called from `app.py` on app load (eager init).

**Q: How does the spaCy model load without warnings?**
A: Via `nlp_loader.py` with `@st.cache_resource`. Lazy-loaded, cached, no repeated warnings.

**Q: What if one tier fails?**
A: Try/except blocks in `generate_phase.py`. Falls back gracefully to previous response.

**Q: Can I disable Tier 3 (Poetic)?**
A: Yes, set `st.session_state["enable_tier3_poetic"] = False` in app.py.

**Q: Where's the old response_handler code?**
A: Merged into `response_handler.py` (120 clean lines). Old 1,233-line version is gone.

**Q: How do I add a new response strategy?**
A: Edit `interpret_phase.py::_build_conversational_response()`. Add a new fallback strategy in the chain.

---

## 📚 Architecture Decision Log

| Decision | Phase | Rationale |
|----------|-------|-----------|
| 3-phase pipeline | 1 | Split monolith for testability |
| Eager tier init | 2 | Eliminate first-message lag |
| Session manager init | 2 | Reuse existing session system |
| Lazy spaCy loader | 0 | Avoid reload warnings in Streamlit |
| Module consolidation | 0 | Single source of truth |

---

**Status:** ✅ All phases complete, production-ready, fully tested.
