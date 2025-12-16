# Integration Guide: Adding Dynamic Learning to Main Response Pipeline

This guide shows how to integrate the learning module into the existing `signal_parser.py` response generation.

## Overview

The learning module should work alongside (not replace) the existing glyph-based response system. It provides an additional layer that:

1. **Tries archetype-based response first** (if a good match exists)
2. **Falls back to glyph-based response** (existing system)
3. **Logs all responses** for automatic learning

## Step 1: Add Learning Module to signal_parser.py

At the top of `signal_parser.py`:

```python
from emotional_os.learning import (
    get_archetype_response_generator,
    get_conversation_learner,
)
```



## Step 2: Create a Wrapper Function

Add this function to `signal_parser.py`:

```python
def _compose_response_with_learning(
    input_text: str,
    glyph: Optional[Dict[str, Any]] = None,
    conversation_context: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Optional[str]]:
    """
    Compose response using archetype-driven learning when available,
    fall back to glyph-based response.

    Returns:
        (response_text, archetype_name_used)
    """
    # Try archetype-based response first
    generator = get_archetype_response_generator()
    prior_context = None

    if conversation_context:
        # Extract prior context for continuity
        prev_user = conversation_context.get("last_user_message")
        if prev_user:
            prior_context = prev_user

    archetype_response = generator.generate_archetype_aware_response(
        user_input=input_text,
        prior_context=prior_context,
        glyph=glyph,
    )

    if archetype_response:
        # Successfully generated from archetype
        return archetype_response, generator.library.get_best_match(
            input_text, prior_context
        ).name if generator.library.get_best_match(input_text, prior_context) else None

    # Fall back to glyph-based response (existing system)
    return None, None
```



## Step 3: Update Response Building Logic

In the `_respond_to_emotional_input` function, modify where responses are generated:

```python

# OLD: Just use glyph-based response

# response = composer.compose_response(input_text, glyph, ...)

# NEW: Try learning-based first, fall back to glyph-based
learning_response, archetype_used = _compose_response_with_learning(
    input_text=input_text,
    glyph=glyph,
    conversation_context=conversation_context,
)

if learning_response:
    response = learning_response
    response_source = f"archetype:{archetype_used}"
else:
    # Fall back to existing glyph-based system
    response = composer.compose_response(
        input_text=input_text,
        glyph=glyph,
        feedback_detected=feedback_data.get("is_correction", False),
        feedback_type=feedback_data.get("contradiction_type"),
        conversation_context=conversation_context,
    )
    response_source = "glyph_composer"
```



## Step 4: Add Learning Logging

After a response is generated, log it for automatic learning:

```python
def _log_response_for_learning(
    user_input: str,
    system_response: str,
    turn_number: int = 1,
) -> None:
    """Log response for async learning (can be called post-response)."""
    # This runs independently and learns patterns from conversations
    # Could be called in a background task or at conversation end
    learner = get_conversation_learner()

    # TODO: Store turn history and call learn_from_conversation()
    # when conversation ends or after N turns
```



## Step 5: Store Conversation History for Learning

To enable learning, store conversation turns:

```python

# In your conversation context or session management
conversation_turns = [
    {"role": "user", "content": input_text},
    {"role": "assistant", "content": response},
]

# At conversation end or after 5+ turns:
learner = get_conversation_learner()
learned = learner.learn_from_conversation(
    turns=conversation_turns,
    user_rating=user_feedback_score,  # Optional: 0-1 scale
)

if learned:
    print(f"System learned new archetype: {learned}")
```



## Step 6: Expose Archetype Information (Optional)

Make the learning visible to users in the UI:

```python
def get_response_metadata(archetype_name: Optional[str] = None) -> Dict[str, Any]:
    """Get metadata about how response was generated."""
    if archetype_name:
        library = get_archetype_library()
        archetype = library.archetypes.get(archetype_name)
        if archetype:
            return {
                "type": "archetype-driven",
                "archetype": archetype_name,
                "principles": archetype.response_principles[:2],
                "confidence": archetype.success_weight,
            }

    return {
        "type": "glyph-based",
        "archetype": None,
    }
```



## Integration Points

### Option A: Minimal Integration (Start Here)
- Just add archetype response generation as fallback
- Don't worry about learning initially
- See if responses improve just from the pre-loaded `ReliefToGratitude` archetype

### Option B: Full Integration
- Add learning logging after each conversation
- Store turns in session
- Call learner.learn_from_conversation() at conversation end
- System auto-improves over time

### Option C: Advanced Integration
- Real-time turn logging
- Expose archetype name in UI responses
- Let users rate whether archetype response was good
- Immediate feedback loop

## Testing

```bash

# Test the learning-integrated response
python -c "
from emotional_os.core.signal_parser import parse_input

# Test with phrase that matches ReliefToGratitude archetype
result = parse_input('My child hugged me and I felt grateful despite the stress')
print(f'Response: {result.get(\"voltage_response\")}')
print(f'Source: {result.get(\"response_source\")}')
"
```



## Expected Behavior After Integration

**First Turn**:
- User: "I feel overwhelmed today"
- System: Uses existing `ReliefToGratitude` or falls back to glyph
- Response: "I hear you. What feels heaviest?"

**Following Turns**:
- User: "But my partner just surprised me with something kind"
- System: Matches to `ReliefToGratitude` archetype (mixed emotions detected)
- Response: "That kindness cuts through the weight. How did that land for you?"

**Over Time**:
- Each good conversation teaches the system new archetypes
- Library grows with patterns from your actual conversations
- System becomes increasingly personalized to how you actually talk
##

**Key Insight**: The learning system amplifies what already works. It doesn't replace glyphs — it adds another layer that learns from lived dialogue.
