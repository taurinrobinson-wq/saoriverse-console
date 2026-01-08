"""Glyph-Aware Response Composition for Phase 2.2.2.

Integrates modernized glyph names directly into response generation.
- Detects affect (tone, arousal, valence)
- Looks up modernized glyph via get_glyph_for_affect()
- Composes responses that reference the glyph
- Maintains conversational, emotional tone with glyph anchoring

Example:
  User: "I'm feeling so exhausted today"
  Affect: sad, arousal=0.3, valence=-0.8
  Glyph lookup: "Pain" or "Loss"
  Response: "I hear the Exhaustion in this. You're feeling something deep, like Loss. 
             How are you holding up?"
"""

from typing import Optional, Dict, Tuple
import re
from emotional_os.core.firstperson.glyph_modernizer import (
    get_glyph_for_affect,
)
from emotional_os.core.firstperson.response_rotator import (
    create_response_rotator,
)


def _apply_sprint5_prosody(user_input: str, tone: str, arousal: float, valence: float, tone_confidence: float) -> None:
    """Apply Sprint 5 prosody markers for high-emotion responses (side-effect).

    This function attempts to initialize and log prosody context for the response.
    Failures are logged but don't block response generation.
    """
    try:
        # Check if this is a high-emotion scenario warranting prosody
        is_high_emotion = (arousal > 0.6 and valence < 0) or (
            tone in ("sad", "anxious", "angry"))
        if not is_high_emotion or tone_confidence < 0.3:
            return

        # Try to initialize Sprint 5 if available
        try:
            from sprint5_integration import init_sprint5_systems, log_interaction
            init_sprint5_systems(enable_profiling=False)

            # Log this high-emotion interaction for prosody tracking
            log_interaction(
                user_text=user_input,
                assistant_response="[prosody context]",
                emotional_state={
                    "tone": tone,
                    "arousal": arousal,
                    "valence": valence,
                    "high_emotion": True
                },
                latency_ms=0,
                confidence=tone_confidence
            )
        except Exception:
            # Sprint 5 not available or logging failed, continue normally
            pass
    except Exception:
        # Any error in prosody application doesn't block response
        pass


def _enhance_with_prosody(response_text: str, user_input: str, tone: str, arousal: float, valence: float) -> str:
    """Enhance response with prosody metadata for TTS synthesis.

    For high-emotion responses, append prosody directives that TTS can interpret.
    """
    try:
        is_high_emotion = (arousal > 0.6 and valence < 0) or (
            tone in ("sad", "anxious", "angry"))
        if not is_high_emotion:
            return response_text

        # Try to generate prosody directives
        try:
            from enhanced_response_composer import EnhancedResponseComposer
            composer = EnhancedResponseComposer()

            # Create minimal glyph structure for prosody generation
            test_glyphs = [{
                'glyph_name': tone or 'emotion',
                'description': '',
                'gate': '',
                'response_template': '',
                'voltage': arousal,
                'tone': tone
            }]

            response_data = composer.compose_multi_glyph_response(
                user_input,
                test_glyphs,
                conversation_context=[],
                top_n=1,
                include_prosody=True
            )

            if isinstance(response_data, tuple) and len(response_data) > 1:
                _, prosody_directives = response_data
                if prosody_directives and isinstance(prosody_directives, dict):
                    # Append prosody metadata as hidden comment
                    import json
                    prosody_json = json.dumps(prosody_directives, default=str)
                    response_text = f"{response_text}\n\n[PROSODY:{prosody_json}]"
        except Exception:
            # Prosody enhancement failed, return original response
            pass
    except Exception:
        # Any error in enhancement doesn't block the response
        pass

    return response_text


def _is_vague_emotional_input(user_input: str, tone: str, arousal: float) -> bool:
    """Detect if input is emotionally charged but contextually vague.

    Vague high-emotion input:
    - Very short (< 20 words typical, sometimes just expletives)
    - No concrete subject ("this", "it", "that" without context)
    - High emotional intensity but no object/target
    - Primary content is emotion/opinion, not specific description

    Examples of VAGUE (trigger curiosity):
    - "this is bullshit"
    - "what a freakin day"
    - "shit"
    - "what the fuck"

    Examples of NOT VAGUE (use affect response):
    - "I am so frustrated with the project"
    - "I hate this situation with my team"
    - "the meeting yesterday was ridiculous"

    Args:
        user_input: The user's message
        tone: Detected emotional tone
        arousal: Emotional arousal level (0-1)

    Returns:
        True if input appears emotionally charged but vague/ambiguous
    """
    # Only flag high-arousal emotional input as potentially vague
    if arousal < 0.6 or tone in ("neutral", "warm", "grateful"):
        return False

    words = user_input.lower().split()

    # Count expletives and intensifiers
    expletives = {"bullshit", "shit", "fuck", "fucking",
                  "damn", "hell", "crap", "whatever"}
    intensifiers = {"really", "so", "very",
                    "super", "extremely", "absolutely", "freakin", "freakin'", "what"}

    expletive_count = sum(1 for w in words if w.strip('.,!?') in expletives)
    intensifier_count = sum(
        1 for w in words if w.strip('.,!?\'') in intensifiers)

    # Short messages with expletives/intensifiers = likely vague
    # (unless there's a specific subject like a person's name, concrete object, or action)
    if len(words) <= 5:
        if expletive_count > 0 or intensifier_count > 1:
            # Check for specific subjects that ground the complaint
            # (not just generic words like "day", "time", "it", "this")
            concrete_subjects = {
                "work", "project", "situation", "person", "meeting",
                "team", "boss", "friend", "family", "school", "code", "test",
                "deadline", "presentation", "system", "app", "feature", "bug",
                "client", "manager", "user", "rule", "policy", "file", "commit"
            }
            has_specific_subject = any(
                w.strip('.,!?') in concrete_subjects for w in words)

            if not has_specific_subject:
                return True

    # Vague pronouns without clear referent
    if any(phrase in user_input.lower() for phrase in ["this is", "that's", "it's all"]):
        # These are vague unless followed by a specific descriptor
        if not any(concrete in user_input.lower()
                   for concrete in ["work", "person", "situation", "problem", "meeting",
                                    "project", "team", "my", "me", "we", "happening"]):
            return True

    return False


def _get_curiosity_response(user_input: str, tone: str, arousal: float) -> Tuple[str, Optional[str]]:
    """Generate curiosity-first response for vague high-emotion input.

    When someone says "this is bullshit" without context, ask what they mean
    instead of assuming. These responses acknowledge the emotion but ask for info.

    Args:
        user_input: The user's message
        tone: Detected emotional tone
        arousal: Emotional arousal level

    Returns:
        Tuple of (response, glyph) where glyph is None for curiosity responses
    """
    # Tone-specific curiosity responses
    curiosity_responses = {
        "angry": [
            "Oh yeah? What's got you heated?",
            "That's real. What happened?",
            "I hear the anger. What's going on?",
            "That's intense. Tell me what's behind it.",
            "Yeah? What's fueling that?",
        ],
        "frustrated": [
            "What's getting to you?",
            "I feel that. What's the main thing?",
            "Yeah, talk to me. What's going on?",
            "That frustration is clear. What's at the core?",
            "What's the most frustrating part?",
        ],
        "anxious": [
            "What's worrying you most?",
            "I hear the stress. What's the pressure about?",
            "That's real tension. What's driving it?",
            "What feels most fragile right now?",
            "Talk to me. What's the concern?",
        ],
        "sad": [
            "That sounds heavy. What's underneath it?",
            "I hear the sadness. What's the loss?",
            "What's hurting?",
            "That pain is real. What's at the core?",
            "What are you grieving?",
        ],
        "confused": [
            "What's unclear about it?",
            "Help me understand. What's confusing?",
            "What do you need to figure out?",
            "Tell me more. What's the confusion?",
        ],
    }

    import random
    responses = curiosity_responses.get(tone, [
        "Tell me more. What's happening?",
        "I'm listening. What's going on?",
        "Help me understand.",
        "What do you mean?",
    ])

    response = random.choice(responses)

    # For curiosity responses, add light prosody but mark as seeking input
    response = _enhance_with_prosody(response, user_input, tone, arousal, -0.5)

    return response, None


def normalize_glyph_capitalization(text: str) -> str:
    """Normalize glyph name capitalization for grammatical correctness.

    Rules:
    - Glyph names at sentence start: Capitalize (e.g., "Anxiety is...")
    - Glyph names mid-sentence after conjunctions: lowercase (e.g., "and the anxiety")
    - Glyph names after "the": lowercase (e.g., "feel the breaking")
    - Glyph names in parenthetical: lowercase (e.g., "(the loss)")
    - Glyph names at end of clause before punctuation: title case

    Args:
        text: Response text with glyph names

    Returns:
        Text with grammatically correct capitalization
    """
    # Known glyph names (modernized)
    glyphs = [
        "Loss", "Pain", "Overwhelm", "Grieving", "Breaking", "Pressure",
        "Seeking", "Resting", "Fire", "Heat", "Frustration", "Resistance",
        "Held Space", "Joy", "Gratitude", "Wonder", "Confusion", "Doubt",
        "Ache"
    ]

    # Pattern 1: "and the Glyph" -> "and the glyph" (mid-sentence)
    for glyph in glyphs:
        text = re.sub(
            rf'\band the {re.escape(glyph)}\b',
            f'and the {glyph.lower()}',
            text
        )

    # Pattern 2: "the Glyph " -> "the glyph " (after articles)
    for glyph in glyphs:
        text = re.sub(
            rf'\bthe {re.escape(glyph)}\b(?![\.\?\!])',
            f'the {glyph.lower()}',
            text
        )

    # Pattern 3: "I hear the Glyph and the Glyph" -> "I hear the glyph and the glyph"
    for glyph in glyphs:
        text = re.sub(
            rf'(\bhear\b.*?\bthe\s+){re.escape(glyph)}(\s+and)',
            rf'\1{glyph.lower()}\2',
            text
        )

    # Pattern 4: Start of sentence should keep capitalization
    # (handled by keeping natural capitalization at sentence boundaries)

    return text


# Glyph-aware response templates that embed modernized glyph names
GLYPH_AWARE_RESPONSES = {
    "exhaustion": {
        "Loss": [
            "That sounds heavy. I hear the exhaustion in it. What's it like for you right now?",
            "That's a lot of weight to carry. How are you holding up?",
        ],
        "Pain": [
            "That sounds painful. I hear the tiredness layered in it. What does that feel like?",
            "That's draining. Where does it hurt most?",
        ],
        "Overwhelm": [
            "That sounds like too much. I hear the exhaustion. What's the heaviest part?",
            "That's a lot at once. How are you managing?",
        ],
        "Grieving": [
            "That sounds like loss. I hear the grief in the tiredness. What are you missing?",
            "There's sadness in that exhaustion. What's underneath it?",
        ],
    },
    "anxiety": {
        "Breaking": [
            "That sounds stressful. I hear the worry in it. What feels most fragile right now?",
            "That's a lot of tension. What's threatening to crack?",
        ],
        "Overwhelm": [
            "That sounds like a lot. I hear the anxiety building. What feels biggest?",
            "That's too much at once. What's piling up?",
        ],
        "Pressure": [
            "That sounds tight. I hear the pressure in it. What's squeezing you?",
            "That feels pressurized. What's the tightest part?",
        ],
        "Seeking": [
            "That sounds uncertain. I hear the worry looking for solid ground. What do you need to know?",
            "That's confusing. What are you trying to figure out?",
        ],
    },
    "sadness": {
        "Loss": [
            "That sounds heavy. I hear the sadness in it. What's been taken from you?",
            "That's painful. Where's it hitting deepest?",
        ],
        "Grieving": [
            "That sounds like grief. What are you mourning?",
            "There's real sadness there. What are you missing?",
        ],
        "Pain": [
            "That sounds like it aches. I hear the sadness and the pain together. How are you managing?",
            "That hurts. What's the pain about?",
        ],
        "Resting": [
            "That sounds like you need to slow down. I hear the sadness in that need. What do you need from yourself right now?",
            "That's a pause, not a crisis. What would help?",
        ],
    },
    "anger": {
        "Fire": [
            "That's heat. I hear the anger burning. What's fueling it most?",
            "That's strong. What's at the heart of it?",
        ],
        "Heat": [
            "That's intensity. I hear the frustration building. What's underneath?",
            "That's real frustration. What needs to shift?",
        ],
        "Frustration": [
            "That's frustrating. I hear it clearly. What's driving it?",
            "That's a lot of intensity. What's in the center of it?",
        ],
        "Resistance": [
            "That's a strong stance. I hear you pushing back. What are you defending?",
            "That's real resistance. What are you saying no to?",
        ],
    },
    "calm": {
        "Stillness": [
            "That sounds grounded. I hear the calm in it. What helped you find that?",
            "That's peaceful. How are you holding that?",
        ],
        "Resting": [
            "That sounds like ease. I hear you resting. What's supporting that?",
            "That's a good breath. What made that possible?",
        ],
        "Acceptance": [
            "That sounds settled. I hear the peace in it. How did you get there?",
            "That's real acceptance. What did that take?",
        ],
    },
    "joy": {
        "Delight": [
            "That's bright. I hear the spark in it. What's bringing that up?",
            "That's alive. What's making it shine?",
        ],
        "Connection": [
            "That sounds good. I hear the connection you're naming. What's resonating?",
            "That's meaningful. What's connecting for you?",
        ],
        "Satisfaction": [
            "That sounds complete. I hear the satisfaction. What came together?",
            "That's real joy. What fulfilled that?",
        ],
    },
    "grateful": {
        "Acceptance": [
            "That's gratitude. I hear it settling in you. What opened that up?",
            "That's real thanks. What made you feel grateful?",
        ],
        "Connection": [
            "That's connection. I hear the gratitude in it. Who or what matters here?",
            "That's meaningful. What's connecting for you?",
        ],
    },
    "confused": {
        "Seeking": [
            "That's uncertain. I hear you looking for ground. What do you need to understand?",
            "That's unclear. What are you trying to figure out?",
        ],
    },
}


def compose_glyph_aware_response(
    user_input: str,
    affect_analysis: Optional[Dict] = None,
    use_rotator: bool = True,
    suggested_glyph: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    """Compose a response that embeds modernized glyph names with emotional prosody.

    Args:
        user_input: The user's input message
        affect_analysis: Dict with tone, arousal, valence, tone_confidence
        use_rotator: Whether to use ResponseRotator as fallback
        suggested_glyph: Optional glyph override from repair orchestrator

    Returns:
        Tuple of (response_text, glyph_used)
    """
    if not affect_analysis:
        if use_rotator:
            rotator = create_response_rotator()
            return rotator.get_response("neutral"), None
        return "I'm here to listen. What's on your mind?", None

    tone = affect_analysis.get("tone")
    arousal = affect_analysis.get("arousal", 0)
    valence = affect_analysis.get("valence", 0)
    tone_confidence = affect_analysis.get("tone_confidence", 0)

    # Check for vague high-emotion input (e.g., "this is bullshit" without context)
    # If detected, use curiosity-first response instead of assuming affect
    if _is_vague_emotional_input(user_input, tone, arousal):
        return _get_curiosity_response(user_input, tone, arousal)

    # Get modernized glyph for the detected affect
    glyph = suggested_glyph or get_glyph_for_affect(tone, arousal, valence)

    # Map affect tone to response category name
    # (tones from affect parser to glyph-aware response categories)
    tone_to_category = {
        "sad": "exhaustion" if arousal < 0.5 else "sadness",
        "anxious": "anxiety",
        "angry": "anger",
        "frustrated": "anger",  # Map frustrated → anger category
        "grateful": "grateful",
        "warm": "joy",
        "confused": "confused",
        "neutral": "calm",
    }
    response_category = tone_to_category.get(tone, tone)

    # Look up glyph-aware responses for this tone category
    tone_responses = GLYPH_AWARE_RESPONSES.get(response_category, {})

    # Sprint 5 Integration: Apply advanced prosody for high-emotion responses
    _apply_sprint5_prosody(user_input, tone, arousal, valence, tone_confidence)

    if glyph and glyph in tone_responses:
        # Use glyph-specific response
        import random
        response = random.choice(tone_responses[glyph])
        response = normalize_glyph_capitalization(response)
        response = _enhance_with_prosody(
            response, user_input, tone, arousal, valence)
        return response, glyph
    elif glyph and tone_responses:
        # Glyph not in specific map, try first available
        first_glyph = list(tone_responses.keys())[0]
        import random
        response = random.choice(tone_responses[first_glyph])
        response = normalize_glyph_capitalization(response)
        response = _enhance_with_prosody(
            response, user_input, tone, arousal, valence)
        return response, first_glyph
    elif use_rotator:
        # Fallback to ResponseRotator
        rotator = create_response_rotator()
        glyph_category = {
            "sad": "exhaustion" if arousal < 0.5 else "sadness",
            "anxious": "anxiety",
            "angry": "anger",
            "grateful": "joy",
            "confused": "neutral",
            "neutral": "neutral",
            "warm": "joy",
        }.get(tone, "neutral")
        response = rotator.get_response(glyph_category, strategy="weighted")
        return response, None
    else:
        return "I'm here to listen. What's on your mind?", None


def should_use_glyph_responses(
    tone_confidence: float = 0.0,
    arousal: float = 0.0,
    valence: float = 0.0,
) -> bool:
    """Determine if we should use glyph-aware responses vs generic ones.

    Glyph responses are best for:
    - Clear emotional signal (confidence > 0.3)
    - Simple check-ins (arousal < 0.7, valence < 0.1)
    - Or acute stress (arousal > 0.6, valence < 0)

    Args:
        tone_confidence: Confidence in tone detection (0-1)
        arousal: Intensity (0-1)
        valence: Sentiment (-1 to +1)

    Returns:
        True if glyph responses should be used
    """
    if tone_confidence < 0.3:
        return False

    is_simple_checkin = valence < 0.1 and arousal < 0.7
    is_stressed_checkin = arousal > 0.6 and valence < 0
    return is_simple_checkin or is_stressed_checkin
