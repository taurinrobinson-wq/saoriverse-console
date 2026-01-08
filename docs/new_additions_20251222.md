---
# New additions — 2025-12-22

This document collects recent ideas and proposals for the Saonyx Emotional OS: a Pun Interjector behavioral layer and a Mutual Joy Handler module. The text below has been structured into clear sections so you can drop the implementations into the codebase or use the content for design discussions.

## Pun Interjector — overview

The Pun Interjector is a behavioral layer that injects short, contextual, and safe puns into conversation when the emotional context supports levity. It is not a random joke generator — it subscribes to the signal bus and follows safety, frequency, and escalation rules.

### Trigger conditions
- Primary triggers: mild frustration, warmth/playfulness, low-stakes vulnerability, energy dip.
- Hard no triggers: grief, trauma, panic, anger, existential distress, or any safety-critical state.

### Glyphs
- `LEVITY` — light, harmless humor.
- `WORDPLAY` — escalation of user wordplay.
- `DEFUSION` — humor to reduce intensity.
- `WARM_MIRROR` — playful reflection of user tone.

Each glyph contains templates, tone rules, escalation limits, and safety constraints.

### Architecture
- Model a pun as a layered object: `setup`, `twist`, `callback`, `tone`, `intensity`.
- Frequency rules: max 1 pun per 8–12 turns unless user signals escalation. Never during sanctuary or Tier 3 states.

### Integration points
- Signal parser, glyph selector, dynamic composer, tone adapter, safety layer.

## Mutual Joy Handler — overview

The Mutual Joy Handler is a relational module that mirrors and gently amplifies earned joy, especially after long struggle or meaningful progress. It celebrates breakthroughs in a grounded, authentic way.

### Trigger conditions
- Primary triggers: breakthrough after struggle, completion of long effort, self-recognition, positive emotional shift.
- Secondary triggers: user shares good news, expresses excitement or gratitude.
- Hard no triggers: Tier 3 states, crisis, grief, sanctuary mode, high-intensity vulnerability.

### Core behavior
The handler performs three actions: emotional mirroring, amplification (small and authentic), and shared presence. The result should feel like companionship, not praise.

### Tone constraints
- Avoid hype or generic praise. Prefer grounded warmth, quiet delight, subtle awe, and gentle humor.
- Use exclamation marks sparingly and only when the emotional lift is earned (see exclamation rule below).

### Module components
- `detector.py` — monitors emotional deltas and long-arc struggle→breakthrough events.
- `amplifier.py` — chooses tone and intensity.
- `templates.py` — stores short, grounded templates (exclamation-permitted and period-safe lists).
- `integrator.py` — injects into the response pipeline, respecting safety and frequency rules.

## Exclamation mark rule (Mutual Joy Handler)

Use exclamation marks only when mirroring genuine positive surprise, relief, or delight. Steps to decide:
1. Detect positive lift (relief, amazement, pride, gratitude). If not present, no exclamation.
2. Confirm long-arc or meaningful context (breakthrough, recognition). If not, no exclamation.
3. Ensure safety/context is clear (no Tier 3 distress, no sanctuary, no ambivalence).
4. Check frequency (max 1 per response, max 1 every 6–10 turns, never consecutive system turns).
5. Calibrate tone and final wording. Prefer period if the moment would feel hypey.

Example accepted line: “Then I’m so happy for you. Feels like a solid breakthrough!”

## Templates (clean, no em-dashes rule enforced)

Exclamation-permitted (used only when the lift is earned):
- “I’m really glad that happened for you!”
- “Feels like a real shift!”
- “That must have felt incredible!”
- “I’m so happy you got that moment!”
- “You’ve been working toward this. I’m thrilled for you!”
- “That’s such a meaningful win!”

Period-safe (softer):
- “I’m really glad that happened for you.”
- “Feels like a real shift.”
- “That must have felt incredible.”
- “I’m so happy you got that moment.”
- “You’ve been working toward this. I’m really glad you reached it.”
- “That’s a meaningful win.”

## Saonyx Style Guide summary

- One-paragraph responses by default.
- No em dashes anywhere; prefer natural sentence breaks, commas, or short second sentences.
- Felt first, read second: prioritize emotional resonance over clever phrasing.
- Humor is connection, not distraction.

---

If you want, I can now add minimal Python stubs for the Pun Interjector and the Mutual Joy Handler so this can be dropped directly into the codebase.
