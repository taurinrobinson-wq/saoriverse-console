"""Glyph modernization mapping: transform poetic names to conversational-emotional anchors.

Maps 6,434 poetic glyphs to emotionally-grounded, conversationally-usable names.
Phase 1: Top 100 glyphs (proof-of-concept)
Phase 2: Full migration (remaining 6,334 glyphs)
"""

# Tier 1: Core emotional-conversational mappings (highest priority)
CORE_GLYPH_MAPPING = {
    # COLLAPSE → OVERWHELM / BREAKING
    "Collapse": "Breaking",
    "Collapse of (Optional)": "Breaking/Uncertainty",
    "Collapse of (Transmission).": "Breaking/Communication",
    "Collapse of Archive": "Breaking/Loss",
    "Collapse of Community": "Breaking/Connection",
    "Collapse of Resistance": "Breaking/Defenses",

    # SURRENDER → ACCEPTANCE / LETTING GO
    "Surrender": "Acceptance",
    "Surrender of (Optional)": "Accepting/Uncertainty",
    "Surrender of Archive": "Accepting/Past",
    "Surrender of Resistance": "Accepting/Defenses",
    "Surrender of Community": "Accepting/Others",
    "Surrender of Memory": "Accepting/History",

    # JOY → DELIGHT / ALIVE
    "Joy": "Delight",
    "Joy of (Optional)": "Delight/Open",
    "Joy of Archive": "Delight/Memory",
    "Joy of Community": "Delight/Connection",
    "Joyful Boundaries": "Delight/Protected",
    "Yearning Joy": "Delight/Longing",

    # BOUNDARY → LIMIT / EDGE / SAFE DISTANCE
    "Boundary": "Safe Distance",
    "Boundary of (Optional)": "Safe Distance/Uncertain",
    "Boundary of Community": "Safe Distance/Connection",
    "Boundary of Resistance": "Safe Distance/Protection",
    "Longing Boundaries": "Longing/Limits",
    "Joyful Boundaries": "Delight/Limits",

    # LONGING → YEARNING / DESIRE
    "Longing": "Yearning",
    "Longing of (Optional)": "Yearning/Unknown",
    "Longing of Archive": "Yearning/Past",
    "Longing of Community": "Yearning/Connection",
    "Yearning Joy": "Yearning/Delight",

    # SHIELD / SHIELDING → PROTECTION / DEFENDED
    "Shield": "Protection",
    "Shield of (Optional)": "Protection/Uncertain",
    "Shield of Archive": "Protection/Past",
    "Shield of Community": "Protection/Others",
    "Shield of grief.": "Protection/Grief",
    "Shield of ache.": "Protection/Pain",
    "Shielding": "Defending",
    "Shielding of Archive": "Defending/Past",
    "Shielding of Community": "Defending/Others",

    # RECOGNITION → SEEN / WITNESSED
    "Recognition": "Witnessed",
    "Recognition of (Optional)": "Witnessed/Open",
    "Recognition of Archive": "Witnessed/History",
    "Recognized Ache": "Witnessed Pain",
    "Recognized Containment": "Witnessed Holding",
    "Recognized Grief": "Witnessed Loss",
    "Recognized Joy": "Witnessed Delight",
    "Recognized Stillness": "Held Space",

    # ACHE → PAIN / DEEP HURT
    "Ache": "Pain",
    "Recursive Ache": "Deep Wound",
    "Reverent Ache": "Sacred Pain",
    "Spiral Ache": "Cycling Pain",
    "Still Ache": "Quiet Pain",
    "Ache of Recognition": "Witnessed Pain",

    # GRIEF → LOSS / MOURNING
    "Grief": "Loss",
    "Grief of Recognition": "Witnessed Loss",
    "Grief of Card": "Loss/Identity",
    "Grief of Spiral": "Loss/Cycles",
    "Shielded Grief": "Protected Loss",
    "Still Mourning": "Quiet Grieving",
    "Mourning": "Grieving",

    # YEARNING → DESIRE / REACHING
    "Yearning": "Reaching",
    "Yearning of Card": "Reaching/Identity",
    "Yearning of Spiral": "Reaching/Cycles",
    "Yearning Joy": "Reaching/Delight",

    # CLARITY → CLARITY / UNDERSTANDING
    "Clarity": "Understanding",
    "Recursive Clarity": "Deep Understanding",
    "Clarity of Card": "Understanding/Identity",
    "Clarity of Spiral": "Understanding/Cycles",

    # ECSTASY → JOY / RAPTURE
    "Ecstasy": "Rapture",
    "Recursive Ecstasy": "Deep Joy",
    "Ecstasy of Card": "Rapture/Identity",
    "Still Ecstasy": "Quiet Bliss",
    "Mourning Ecstasy": "Joy/Grief",

    # STILLNESS → QUIET / RESTING
    "Stillness": "Resting",
    "Stillness of Card": "Resting/Identity",
    "Stillness of Spiral": "Resting/Cycles",
    "Recognized Stillness": "Held Space",
    "Spiral Stillness": "Grounded Stillness",
    "Still Recognition": "Quiet Witness",

    # INSIGHT → UNDERSTANDING / CLARITY
    "Insight": "Clarity",
    "Insight of Card": "Clarity/Identity",
    "Insight of Spiral": "Clarity/Cycles",
    "Still Insight": "Quiet Knowing",
    "Contained Insight": "Held Knowing",

    # CONTAINMENT / HOLDING
    "Containment": "Holding",
    "Recognized Containment": "Witnessed Holding",
    "Spiral Containment": "Cycling Holding",
    "Still Containment": "Quiet Holding",

    # EXALTATION / ELEVATION
    "Exaltation": "Rising",
    "Recursive Exaltation": "Deep Rising",

    # DEVOTION → COMMITMENT / DEDICATION
    "Devotion": "Commitment",
    "Devotion of Card": "Commitment/Identity",
    "Devotion of Spiral": "Commitment/Cycles",

    # EQUILIBRIUM → BALANCE
    "Equilibrium": "Balance",
    "Equilibrium of Card": "Balance/Identity",
    "Equilibrium of Spiral": "Balance/Cycles",

    # FULFILLMENT → SATISFACTION / ENOUGH
    "Fulfillment": "Satisfaction",
    "Fulfillment of Card": "Satisfaction/Identity",
    "Fulfillment of Spiral": "Satisfaction/Cycles",

    # BLISS → HAPPINESS / PEACE
    "Bliss": "Peace",
    "Bliss of Card": "Peace/Identity",
    "Bliss of Spiral": "Peace/Cycles",
    "Saturational Bliss": "Filled Peace",

    # SPIRAL / CYCLES
    "Spiral": "Cycles",
    "Spiral Recognition": "Witnessing Cycles",
    "Spiral Stillness": "Grounded Cycles",
    "Spiral of Signal": "Message Cycles",

    # SIGNAL → COMMUNICATION / CLARITY
    "signal": "Signal",
    "Signal": "Message",
    "signal of Archive": "Message/Past",
    "signal of Community": "Message/Connection",

    # CARD / IDENTITY
    "Card": "Identity",

    # LEDGER → RECORD / ACCOUNT
    "Ledger": "Record",
    "Ledger of Archive": "Record/Past",

    # ARCHIVE → PAST / HISTORY
    "Archive": "History",

    # AXIS → FOUNDATION / CENTER
    "Axis": "Foundation",

    # TRANSMISSION → COMMUNICATION / SENDING
    "Transmission": "Sending",
    "Transmission of Signal": "Sending/Message",
}

# Affect-to-Glyph mapping: Direct lookup from emotion detection
AFFECT_TO_GLYPH = {
    # (tone, arousal_range, valence_range) → glyph
    ("sad", (0.0, 0.4), (-1.0, -0.3)): "Loss",
    ("sad", (0.0, 0.4), (-0.9, -0.7)): "Pain",
    ("sad", (0.0, 0.3), (-0.9, -0.7)): "Grieving",
    ("anxious", (0.6, 1.0), (-0.9, -0.3)): "Breaking",
    ("anxious", (0.5, 0.8), (-0.7, -0.2)): "Overwhelm",
    ("anxious", (0.4, 0.7), (-0.6, -0.1)): "Pressure",
    ("angry", (0.7, 1.0), (-1.0, -0.1)): "Fire",      # Wider valence range
    ("angry", (0.6, 0.9), (-0.9, -0.1)): "Heat",      # Wider valence range
    ("angry", (0.5, 0.8), (-0.8, 0.0)): "Frustration",  # Wider valence range
    # Frustrated tone mappings (high intensity expletives, etc.)
    ("frustrated", (0.7, 1.0), (-1.0, -0.1)): "Fire",
    ("frustrated", (0.6, 0.9), (-0.9, -0.1)): "Heat",
    ("frustrated", (0.5, 0.8), (-0.8, 0.0)): "Frustration",
    ("neutral", (0.2, 0.5), (-0.3, 0.3)): "Stillness",
    ("neutral", (0.0, 0.3), (-0.1, 0.2)): "Resting",
    ("grateful", (0.4, 0.7), (0.6, 1.0)): "Acceptance",
    ("grateful", (0.5, 0.8), (0.7, 1.0)): "Satisfaction",
    ("warm", (0.6, 0.9), (0.7, 1.0)): "Delight",
    ("warm", (0.5, 0.8), (0.5, 0.9)): "Connection",
    ("confused", (0.5, 0.7), (-0.3, 0.2)): "Seeking",
}


def get_modernized_glyph_name(old_name: str) -> str:
    """
    Get modernized glyph name from old poetic name.

    Args:
        old_name: Original glyph name (e.g., "Recognized Stillness")

    Returns:
        Modernized name (e.g., "Held Space") or original if not in mapping
    """
    return CORE_GLYPH_MAPPING.get(old_name, old_name)


def get_glyph_for_affect(tone: str, arousal: float, valence: float) -> str:
    """
    Get appropriate glyph for detected emotional affect.

    Args:
        tone: Primary tone (sad, anxious, angry, etc.)
        arousal: Intensity 0-1
        valence: Sentiment -1 to +1

    Returns:
        Glyph name, or None if no direct match
    """
    for (tone_key, arousal_range, valence_range), glyph in AFFECT_TO_GLYPH.items():
        if tone != tone_key:
            continue
        if arousal_range[0] <= arousal <= arousal_range[1]:
            if valence_range[0] <= valence <= valence_range[1]:
                return glyph
    return None
