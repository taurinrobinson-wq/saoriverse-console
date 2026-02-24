// ============================================================================
// VELINOR: REMNANTS OF THE TONE - INK NARRATIVE ENGINE
// ============================================================================
// 
// Entry point: Includes all sub-modules and starts the story
// 
// Structure:
//   tone_system.ink      → TONE variables, coherence formula
//   npc_profiles.ink    → NPC dialogue blocks  
//   glyph_reveals.ink   → 3-tier glyph system
//   gates.ink           → Gate checking functions
//   utilities.ink       → Math & helper functions
//   marketplace.ink     → Hub and location scenes
//
// Play in Inky: Build → Click Play button → Enjoy!
//
// ============================================================================

INCLUDE tone_system.ink
INCLUDE npc_profiles.ink
INCLUDE glyph_reveals.ink
INCLUDE gates.ink
INCLUDE utilities.ink
INCLUDE marketplace.ink

=== STORY_START ===
Welcome to Velinor: Remnants of the Tone.

This is the Act I vertical slice. Everything you do shapes your emotional coherence.

~ coherence = calculate_coherence()

Let's begin.

-> saori_encounter

=== STORY_END ===
Thank you for playing.

Final Stats:
  Trust: {tone_trust}
  Observation: {tone_observation}
  Narrative Presence: {tone_narrative_presence}
  Empathy: {tone_empathy}
  Coherence: {coherence}

Glyphs Revealed: {glyphs_revealed}

-> END

// ============================================================================
// NAVIGATION & TESTING
// ============================================================================
// Uncomment any line below to jump directly to a scene for testing

// -> TEST_SCENE_SELECT

=== TEST_SCENE_SELECT ===
[Testing mode: Jump to any scene]

* [Saori Encounter] -> saori_encounter
* [Marketplace Hub] -> marketplace_hub
* [Marketplace: Market Stalls] -> market_stalls
* [Marketplace: Shrine Area] -> shrine_area
* [Marketplace: Collapsed Building] -> collapsed_building
* [Ravi Dialogue] -> ravi_dialogue
* [Nima Dialogue] -> nima_dialogue
* [Test Glyph: The Promise Held] -> promise_held
* [Test Coherence Gate] -> test_coherence_gate
* [Test Influence Gate] -> test_influence_gate
* [View Stats] -> show_stats
* [View Glyphs] -> show_glyphs

=== show_stats ===
Current Emotional State:
  Trust: {tone_trust}
  Observation: {tone_observation}
  Narrative Presence: {tone_narrative_presence}
  Empathy: {tone_empathy}
  Coherence: {calculate_coherence()}

* [Back] -> TEST_SCENE_SELECT

=== show_glyphs ===
Glyphs Revealed: {glyphs_revealed}

{glyphs_revealed > 0:
    -> SHOW_GLYPH_LIST
}

* [Back] -> TEST_SCENE_SELECT

=== SHOW_GLYPH_LIST ===
- The Promise Held (Comfort): {promise_held_unlocked}
- Collapse Moment (Crisis): {collapse_moment_unlocked}
- Fierce Joy (Joy): {fierce_joy_unlocked}
-> DONE

=== test_coherence_gate ===
[Testing coherence gate: requires >= 70]

~ temp passes = check_coherence_gate(70)

{passes:
  Your coherence is high ({calculate_coherence()}). Deep dialogue available.
- else:
  Your coherence is low ({calculate_coherence()}). Develop more harmony.
}

* [Back] -> TEST_SCENE_SELECT

=== test_influence_gate ===
[Testing influence gate: requires >= 0.6 with Ravi]

~ temp passes = check_influence_gate("ravi", 0.6)

{passes:
  Ravi trusts you ({influence_ravi}). Personal stories become available.
- else:
  Ravi is still cautious ({influence_ravi}). Build more trust.
}

* [Back] -> TEST_SCENE_SELECT
