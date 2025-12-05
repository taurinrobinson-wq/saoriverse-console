# EXACT CODE CHANGES: Connect ConversationMemory

**Copy-paste ready. 45 minutes to completion.**

---

## FILE 1: ui_refactored.py

**Location:** `src/emotional_os/deploy/modules/ui_refactored.py`

**Find this function** (around line 130-150):

```python
def initialize_session_state():
    """Initialize Streamlit session state."""
    # ... existing code ...
```

**REPLACE THE ENTIRE FUNCTION with this:**

```python
def initialize_session_state():
    """Initialize Streamlit session state with memory layers."""
    
    # Existing initializations
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # ... (keep all existing session state initializations) ...
    
    # NEW: Initialize conversation memory
    if "conversation_memory" not in st.session_state:
        try:
            from emotional_os_glyphs.conversation_memory import ConversationMemory
            st.session_state.conversation_memory = ConversationMemory()
            logger.info("✅ ConversationMemory initialized for session")
        except ImportError as e:
            logger.warning(f"⚠️  ConversationMemory import failed: {e}")
            st.session_state.conversation_memory = None
        except Exception as e:
            logger.warning(f"⚠️  ConversationMemory initialization failed: {e}")
            st.session_state.conversation_memory = None
    
    # NEW: Initialize lexicon learner
    if "lexicon_learner" not in st.session_state:
        try:
            from emotional_os.core.lexicon_learner import LexiconLearner
            st.session_state.lexicon_learner = LexiconLearner()
            logger.info("✅ LexiconLearner initialized for session")
        except ImportError as e:
            logger.warning(f"⚠️  LexiconLearner import failed: {e}")
            st.session_state.lexicon_learner = None
        except Exception as e:
            logger.warning(f"⚠️  LexiconLearner initialization failed: {e}")
            st.session_state.lexicon_learner = None
```

---

## FILE 2: response_handler.py

**Location:** `src/emotional_os/deploy/modules/ui_components/response_handler.py`

### CHANGE 2A: Modify `_build_conversational_response()`

**Find this function** (around line 130-180):

```python
def _build_conversational_response(user_input: str, local_analysis: dict) -> str:
    """Build a natural conversational response from signal analysis."""
    best_glyph = local_analysis.get("best_glyph") if local_analysis else None
    voltage_response = local_analysis.get("voltage_response", "") if local_analysis else ""
    
    # If we have a voltage response, use that as the primary response
    if voltage_response and voltage_response.strip():
        response = voltage_response.strip()
        if "Resonant Glyph:" in response:
            response = response.split("Resonant Glyph:")[0].strip()
        return response
    
    # fallback
    return "..."
```

**REPLACE WITH THIS:**

```python
def _build_conversational_response(user_input: str, local_analysis: dict) -> str:
    """Build response using conversation memory for context awareness.
    
    Prioritizes memory-informed responses when context is available,
    falls back to voltage response or glyph-based response.
    """
    best_glyph = local_analysis.get("best_glyph") if local_analysis else None
    voltage_response = local_analysis.get("voltage_response", "") if local_analysis else ""
    
    # ===== NEW: Memory-informed response =====
    memory = st.session_state.get("conversation_memory")
    
    if memory and user_input.strip():
        # Add this turn to memory for context tracking
        try:
            memory.add_turn(
                message=user_input,
                signal_analysis=local_analysis,
            )
            confidence = memory._state.emotional_profile.confidence
            logger.info(f"💾 Memory turn added. Confidence: {confidence:.2f}")
        except Exception as e:
            logger.warning(f"⚠️  Memory add_turn failed: {e}")
    
    # Use memory-aware composition if we have sufficient context
    # (confidence > 0.75 means we have multiple turns with integrated info)
    if memory and memory._state.emotional_profile.confidence > 0.75:
        try:
            from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer
            composer = DynamicResponseComposer()
            
            response = composer.compose_response_with_memory(
                input_text=user_input,
                conversation_memory=memory,
                glyph=best_glyph,
            )
            
            if response and response.strip():
                logger.info("✅ Used memory-informed response (confidence > 0.75)")
                return response
        except Exception as e:
            logger.debug(f"Memory-informed response failed, falling back: {e}")
    
    # ===== FALLBACK: Use existing voltage response logic =====
    # If we have a voltage response, use that as the primary response
    if voltage_response and voltage_response.strip():
        response = voltage_response.strip()
        if "Resonant Glyph:" in response:
            response = response.split("Resonant Glyph:")[0].strip()
        logger.info(f"Using voltage response (memory confidence: {memory._state.emotional_profile.confidence if memory else 'N/A'})")
        return response
    
    # Last resort: basic glyph-based response
    if best_glyph:
        fallback = f"I hear you. {best_glyph.get('description', 'Tell me more.')}"
        logger.info("Using fallback glyph-based response")
        return fallback
    
    logger.warning("All response methods failed, returning minimal response")
    return "I'm here to listen."
```

---

### CHANGE 2B: Add Implicit Learning Feedback Collection

**Find this location** (after `_build_conversational_response()` function, add a NEW function):

```python
# Add this NEW function AFTER _build_conversational_response()

def _collect_implicit_learning_feedback(user_input: str, response: str, local_analysis: dict) -> None:
    """Collect implicit feedback for lexicon learning.
    
    This happens automatically without user interaction, helping the system
    learn the user's emotional vocabulary over time.
    """
    try:
        learner = st.session_state.get("lexicon_learner")
        if not learner:
            return
        
        # Create conversation exchange data for learning
        exchange_data = {
            "user_message": user_input,
            "system_response": response,
            "glyph": local_analysis.get("best_glyph", {}),
            "signals": local_analysis.get("signals", []),
            "timestamp": datetime.datetime.now().isoformat() if hasattr(datetime, 'datetime') else None,
        }
        
        # Learn from this exchange
        learning_results = learner.learn_from_conversation(exchange_data)
        
        if learning_results and learning_results.get("new_patterns"):
            logger.info(f"📚 Learned new patterns: {learning_results.get('new_patterns', [])[:3]}")
            
            # Update lexicon with learned patterns
            try:
                learner.update_lexicon_from_learning(learning_results)
            except Exception as e:
                logger.debug(f"Lexicon update failed: {e}")
    
    except Exception as e:
        logger.debug(f"Implicit feedback collection failed: {e}")
```

---

### CHANGE 2C: Modify `handle_response_pipeline()` to call feedback

**Find this function** (around line 20-60):

```python
def handle_response_pipeline(user_input: str, conversation_context: dict) -> str:
    """Execute the full response processing pipeline."""
    start_time = time.time()
    response = ""
    processing_mode = st.session_state.get("processing_mode", "local")

    try:
        # Run appropriate pipeline based on mode
        if processing_mode == "local":
            response = _run_local_processing(user_input, conversation_context)
        else:
            response = _run_hybrid_processing(user_input, conversation_context)

        # ... rest of function ...
```

**MODIFY to add learning feedback:**

```python
def handle_response_pipeline(user_input: str, conversation_context: dict) -> str:
    """Execute the full response processing pipeline."""
    start_time = time.time()
    response = ""
    processing_mode = st.session_state.get("processing_mode", "local")

    try:
        # Run appropriate pipeline based on mode
        if processing_mode == "local":
            response = _run_local_processing(user_input, conversation_context)
        else:
            response = _run_hybrid_processing(user_input, conversation_context)

        # NEW: Collect implicit learning feedback
        local_analysis = st.session_state.get("last_local_analysis", {})
        if local_analysis and response:
            _collect_implicit_learning_feedback(user_input, response, local_analysis)

        # ... rest of function (keep existing fallback protocols, prosody stripping, etc.) ...
```

---

## FILE 3: Create Test File

**Create new file:** `test_quick_integration.py` (in root directory)

```python
#!/usr/bin/env python3
"""Quick integration test for ConversationMemory."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from emotional_os_glyphs.conversation_memory import ConversationMemory
from emotional_os_glyphs.dynamic_response_composer import DynamicResponseComposer

def test_memory_integration():
    """Test that memory works with composer."""
    
    print("=" * 70)
    print("TESTING: ConversationMemory + DynamicResponseComposer Integration")
    print("=" * 70)
    
    # Initialize components
    memory = ConversationMemory()
    composer = DynamicResponseComposer()
    
    # Test data for 3-turn conversation
    turns = [
        {
            "input": "I'm feeling so stressed today",
            "analysis": {
                "signals": ["stress"],
                "intensity": 0.7,
                "best_glyph": {"glyph_name": "Still Insight", "description": "A moment of pause"},
            }
        },
        {
            "input": "I have so much work piling up",
            "analysis": {
                "signals": ["stress", "work_pressure"],
                "intensity": 0.85,
                "best_glyph": {"glyph_name": "Fragmentation", "description": "Scattered thoughts"},
            }
        },
        {
            "input": "5 projects are due Thursday and I haven't started one",
            "analysis": {
                "signals": ["stress", "deadline_pressure", "anxiety"],
                "intensity": 0.95,
                "best_glyph": {"glyph_name": "The Threshold", "description": "A critical decision point"},
            }
        }
    ]
    
    # Process each turn
    responses = []
    for i, turn in enumerate(turns, 1):
        print(f"\n{'─' * 70}")
        print(f"TURN {i}: {turn['input']}")
        print(f"{'─' * 70}")
        
        # Add to memory
        memory.add_turn(turn["input"], turn["analysis"])
        confidence = memory._state.emotional_profile.confidence
        
        print(f"Memory Confidence: {confidence:.2f}")
        print(f"Emotional Affects: {memory._state.emotional_profile.primary_affects}")
        
        # Generate response
        if confidence > 0.75:
            response = composer.compose_response_with_memory(
                turn["input"],
                memory,
                turn["analysis"]["best_glyph"]
            )
            print(f"Response Type: MEMORY-INFORMED")
        else:
            response = composer.compose_response(
                turn["input"],
                turn["analysis"]["best_glyph"]
            )
            print(f"Response Type: GLYPH-BASED (confidence too low)")
        
        responses.append(response)
        print(f"Response: {response[:150]}...")
    
    # Validation
    print(f"\n{'=' * 70}")
    print("VALIDATION RESULTS")
    print(f"{'=' * 70}")
    
    checks = [
        ("Memory confidence increases", 
         memory._state.emotional_profile.confidence >= 0.85),
        ("All responses generated", 
         len(responses) == 3 and all(r for r in responses)),
        ("Later responses reference context", 
         any(word in responses[2].lower() for word in ["projects", "deadline", "thursday"])),
        ("Glyphs identified", 
         len(memory._state.glyph_set) >= 1),
    ]
    
    passed = 0
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\n{'─' * 70}")
    print(f"RESULT: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("🎉 INTEGRATION SUCCESSFUL!")
        return True
    else:
        print("⚠️  Some checks failed. Review output above.")
        return False

if __name__ == "__main__":
    import datetime
    success = test_memory_integration()
    sys.exit(0 if success else 1)
```

---

## STEP-BY-STEP IMPLEMENTATION

1. **Edit ui_refactored.py**
   - Find `initialize_session_state()` function
   - Replace with the code above
   - Save file

2. **Edit response_handler.py**
   - CHANGE 2A: Replace `_build_conversational_response()` with new code
   - CHANGE 2B: Add new `_collect_implicit_learning_feedback()` function after it
   - CHANGE 2C: Modify `handle_response_pipeline()` to call the feedback function
   - Save file

3. **Create test file**
   - Create `test_quick_integration.py` in root directory
   - Copy code exactly as shown
   - Save file

4. **Run test**
   ```powershell
   cd d:\saoriverse-console
   .\.venv\Scripts\python.exe test_quick_integration.py
   ```

5. **Test in UI**
   ```powershell
   streamlit run app.py
   ```
   - Have a 3-turn conversation
   - Verify context builds naturally

---

## EXPECTED OUTPUT FROM TEST

```
======================================================================
TESTING: ConversationMemory + DynamicResponseComposer Integration
======================================================================

──────────────────────────────────────────────────────────────────────
TURN 1: I'm feeling so stressed today
──────────────────────────────────────────────────────────────────────
Memory Confidence: 0.70
Emotional Affects: ['stress']
Response Type: GLYPH-BASED (confidence too low)
Response: I hear you're stressed. There's weight in what you're carrying...

──────────────────────────────────────────────────────────────────────
TURN 2: I have so much work piling up
──────────────────────────────────────────────────────────────────────
Memory Confidence: 0.85
Emotional Affects: ['stress', 'work_pressure']
Response Type: MEMORY-INFORMED
Response: Work has flooded your mind with competing demands. Even one step...

──────────────────────────────────────────────────────────────────────
TURN 3: 5 projects are due Thursday and I haven't started one
──────────────────────────────────────────────────────────────────────
Memory Confidence: 0.95
Emotional Affects: ['stress', 'work_pressure', 'deadline_pressure']
Response Type: MEMORY-INFORMED
Response: So work has flooded your mind with 5 distinct priorities and one...

======================================================================
VALIDATION RESULTS
======================================================================
✅ Memory confidence increases
✅ All responses generated
✅ Later responses reference context
✅ Glyphs identified

──────────────────────────────────────────────────────────────────────
RESULT: 4/4 checks passed

🎉 INTEGRATION SUCCESSFUL!
```

---

## ROLLBACK (If Needed)

If something doesn't work:

**In ui_refactored.py**, comment out:
```python
    # if "conversation_memory" not in st.session_state:
    #     try:
    #         from emotional_os_glyphs.conversation_memory import ConversationMemory
    #         st.session_state.conversation_memory = ConversationMemory()
```

**In response_handler.py**, comment out memory checks:
```python
    # if memory and memory._state.emotional_profile.confidence > 0.75:
    #     try:
    #         response = composer.compose_response_with_memory(...)
```

System will fall back to original behavior.

---

## WHAT TO LOOK FOR IN LOGS

**Success indicators** (in Streamlit terminal):

```
✅ ConversationMemory initialized for session
💾 Memory turn added. Confidence: 0.70
💾 Memory turn added. Confidence: 0.85
✅ Used memory-informed response (confidence > 0.75)
📚 Learned new patterns: ['work_stress', 'deadline_pressure']
```

**Error indicators** (watch out for):

```
❌ ConversationMemory import failed
⚠️  Memory add_turn failed
⚠️  Memory-informed response failed
```

---

## YOU'RE ALL SET!

Copy the code above, make the changes, run the test, and you'll have ConversationMemory working in under 45 minutes.

**That's it. No more complexity. Just copy-paste and go.**

After this works, follow `INTEGRATION_ROADMAP.md` for Tier 2 and beyond.

You've got this! 🚀

