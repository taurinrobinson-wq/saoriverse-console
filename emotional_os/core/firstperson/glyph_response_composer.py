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
  Response: "I hear the Exhaustion in this. You're feeling something deep—like Loss. 
             How are you holding up?"
"""

from typing import Optional, Dict, Tuple
from emotional_os.core.firstperson.glyph_modernizer import (
    get_glyph_for_affect,
)
from emotional_os.core.firstperson.response_rotator import (
    create_response_rotator,
)


# Glyph-aware response templates that embed modernized glyph names
GLYPH_AWARE_RESPONSES = {
    "exhaustion": {
        "Loss": [
            "I hear the Exhaustion in this. You're carrying Loss—that deep depletion. How are you holding up?",
            "I feel the weight. It's Loss layered with fatigue. Tell me more about what you're carrying.",
        ],
        "Pain": [
            "That sounds draining. There's Pain underneath the tiredness. What's at the core for you?",
            "I hear the Exhaustion mixed with Pain. That's a lot to hold. Where does it hurt most?",
        ],
        "Overwhelm": [
            "I hear the Exhaustion. There's Overwhelm in there too—breaking point territory. What's the heaviest part?",
            "That sounds like breaking. Exhaustion + Overwhelm is a lot. How are you managing it?",
        ],
        "Grieving": [
            "I hear the deep tiredness. There's Grieving underneath. What are you mourning right now?",
            "That Exhaustion sounds like Grieving too—like you're mourning something. Tell me?",
        ],
    },
    "anxiety": {
        "Breaking": [
            "I can feel the worry. There's Breaking happening too—like something's fragmenting. What's unraveling?",
            "I hear the Anxiety and the Breaking underneath. What's threatening to crack?",
        ],
        "Overwhelm": [
            "That sounds uneasy. There's Overwhelm in there—too much at once. What feels biggest?",
            "I hear the Anxiety layered with Overwhelm. What's piling up the most?",
        ],
        "Pressure": [
            "I hear the tension. There's Pressure building. What's squeezing the most?",
            "That anxiety feels pressurized. What's the tightest part for you right now?",
        ],
        "Seeking": [
            "I hear the confusion in the worry. There's Seeking happening—searching for ground. What are you looking for?",
            "I feel the Anxiety and the Seeking. What do you need to find right now?",
        ],
    },
    "sadness": {
        "Loss": [
            "I hear the sadness. There's Loss here—something deeply mourned. What's been taken?",
            "I can sense the sorrow and Loss. Where's it hitting deepest for you?",
        ],
        "Grieving": [
            "I hear the Grieving in your sadness. What are you mourning?",
            "That's real grief. The Grieving is showing. Do you want to stay with that?",
        ],
        "Pain": [
            "I hear the sadness layered with Pain. It feels deep and aching. How is it showing up?",
            "That Sadness + Pain combination hits hard. What's the ache about for you?",
        ],
        "Resting": [
            "I hear the sadness, and there's rest in it too—like you need to pause. What do you need right now?",
            "There's sadness here, but it feels more like Resting than crisis. Tell me what that's like?",
        ],
    },
    "anger": {
        "Fire": [
            "That's strong anger. I hear the Fire in it—real heat. What's at the heart of it?",
            "I feel that Fire. The anger is burning. What's fueling it most?",
        ],
        "Heat": [
            "I hear the intensity. There's Heat in your frustration. Where's it burning?",
            "That's real frustration—Heat building. What's underneath for you?",
        ],
        "Frustration": [
            "I hear the anger and the Frustration. What's driving it right now?",
            "That intensity matters. The Frustration is real. What needs to shift?",
        ],
        "Resistance": [
            "I hear the Fire and the Resistance underneath. What are you pushing back against?",
            "That anger has Resistance in it—taking a stand. What are you defending?",
        ],
    },
    "calm": {
        "Stillness": [
            "I hear the calm. There's Stillness in it—like the water settled. What helped?",
            "That feels grounded. The Stillness is real. How are you holding that?",
        ],
        "Resting": [
            "I hear the ease in your words. That Resting feels good. What's supporting it?",
            "That sounds peaceful. You're Resting into it. What made that possible?",
        ],
        "Acceptance": [
            "I hear the calm and the Acceptance. There's peace in letting it be. How did you get there?",
            "That Acceptance comes through. It feels settled. Tell me more about it?",
        ],
    },
    "joy": {
        "Delight": [
            "I hear the spark in your words. That Delight feels alive. What's bringing it up?",
            "That brightness comes through. The Delight is real. What's making it shine?",
        ],
        "Connection": [
            "I hear the joy in that. There's Connection underneath—something resonating. What's connecting?",
            "That energy feels like Connection—linking to something bigger. What's that about?",
        ],
        "Satisfaction": [
            "I hear the joy. There's Satisfaction in it—like something's complete. What's fulfilled?",
            "That feels like real Satisfaction. Something's coming together for you. Tell me?",
        ],
    },
    "grateful": {
        "Acceptance": [
            "I hear the gratitude and the Acceptance underneath. What's settled for you?",
            "That comes through—real Acceptance and thanks. What opened that up?",
        ],
        "Connection": [
            "I hear the gratitude. There's Connection in it—linking to what matters. Who or what's that about?",
            "That Gratitude has Connection in it. What's connecting for you right now?",
        ],
    },
    "confused": {
        "Seeking": [
            "I hear the confusion. There's Seeking underneath—looking for ground. What are you trying to understand?",
            "I feel the uncertainty and the Seeking. What's most unclear right now?",
        ],
    },
}


def compose_glyph_aware_response(
    user_input: str,
    affect_analysis: Optional[Dict] = None,
    use_rotator: bool = True,
) -> Tuple[str, Optional[str]]:
    """Compose a response that embeds modernized glyph names.

    Args:
        user_input: The user's input message
        affect_analysis: Dict with tone, arousal, valence, tone_confidence
        use_rotator: Whether to use ResponseRotator as fallback

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

    # Get modernized glyph for the detected affect
    glyph = get_glyph_for_affect(tone, arousal, valence)

    # Map affect tone to response category name
    # (tones from affect parser to glyph-aware response categories)
    tone_to_category = {
        "sad": "exhaustion" if arousal < 0.5 else "sadness",
        "anxious": "anxiety",
        "angry": "anger",
        "grateful": "grateful",
        "warm": "joy",
        "confused": "confused",
        "neutral": "calm",
    }
    response_category = tone_to_category.get(tone, tone)

    # Look up glyph-aware responses for this tone category
    tone_responses = GLYPH_AWARE_RESPONSES.get(response_category, {})

    if glyph and glyph in tone_responses:
        # Use glyph-specific response
        import random
        response = random.choice(tone_responses[glyph])
        return response, glyph
    elif glyph and tone_responses:
        # Glyph not in specific map, try first available
        first_glyph = list(tone_responses.keys())[0]
        import random
        response = random.choice(tone_responses[first_glyph])
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
