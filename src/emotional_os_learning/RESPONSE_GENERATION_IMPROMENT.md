# Response Generation Improvement Checklist (ArchetypeResponseGenerator V2)

## Goal

Ensure generated responses feel relational, warm, and conversational — not like survey questions.

## Principles to Enforce

1. **Alternate cadence**
   - Do not end every turn with a question.
   - Pattern: Validation → Reflection → Gentle Inquiry → Affirmation.

2. **Ground in user language**
   - Only introduce concepts explicitly mentioned by the user.
   - Avoid steering into archetype arcs prematurely (e.g., don’t mention “creative spark” unless user does).

3. **Withness language**
   - Use phrases that show presence:
     - “I’m here with you in that heaviness.”
     - “That silence you described feels vivid.”

4. **Micro‑affirmations**
   - Insert short relational anchors between longer responses:
     - “That makes sense.”
     - “I hear the care in how you say that.”
     - “It sounds important.”

5. **Limit metaphors**
   - Mirror user metaphors only when they appear in input.
   - Avoid over‑poetic or abstract phrasing that rolls away from the user.

6. **Clarifying questions over assumptions**
   - Instead of: “It sounds like more than a hobby.”
   - Use: “Do you feel like drawing is more than a hobby for you?”

7. **Contextual continuity**
   - Carry forward themes naturally (stress → purpose → identity) without forcing leaps.
   - Ensure user’s response logically follows the system’s prompt.

## Implementation Notes

- Add variation logic so only ~50% of turns end with a question.
- Introduce a “reflection response type” that outputs a statement instead of a question.
- Track user metaphors/keywords and only reuse them when present.
- Add a check: if closing is a question, ensure the prior sentence is a reflection/validation.
- Enforce max one metaphor per response, grounded in user input.
- Add a “no premature arc” rule: don’t introduce archetype themes until user signals them.

##
