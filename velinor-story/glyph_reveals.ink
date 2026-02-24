// ============================================================================
// GLYPH SYSTEM: 3-Tier Ciphers (Hint → Context → Plaintext)
// ============================================================================
//
// Each glyph has three revelation tiers:
//   Tier 1 (Hint): Visual symbol, emotional signal - always visible
//   Tier 2 (Context): Narrative meaning, discovered through dialogue
//   Tier 3 (Plaintext): Full emotional truth - emotionally gated (requires gates)
//
// Gates for Tier 3:
//   - Coherence >= threshold (usually 70+)
//   - Specific TONE stat >= threshold (e.g., empathy >= 70)
//   - Specific influence with NPC >= threshold (e.g., influence_ravi >= 0.6)
//
// ============================================================================

=== promise_held ===
~ temp tier = get_glyph_tier("promise_held")

{tier}
+ 1 -> promise_held_tier_1
+ 2 -> promise_held_tier_2
+ else -> promise_held_tier_3

// --- TIER 1: Hint Layer (Always Visible) ---
=== promise_held_tier_1 ===
A soft glow appears in your peripheral vision: ◈ (interlocking circles, soft blue)

Something constant is present here. A promise. Something held, steadily.

* [Continue] -> promise_held_closing

// --- TIER 2: Context Layer (After Meeting Ravi) ---
=== promise_held_tier_2 ===
The glyph from before returns, clearer now when Ravi speaks.

Ravi: "This is what we hold onto when everything else shifts."

You understand—the promise of companionship held true, steadily, even as the world cracks open. The marketplace. Community. Choosing to remain present.

{influence_ravi >= 0.6:
    -> promise_held_tier_3
- else:
    -> promise_held_closing
}

// --- TIER 3: Plaintext Layer (Emotionally Gated) ---
=== promise_held_tier_3 ===
{coherence >= 70 and tone_empathy >= 70 and influence_ravi >= 0.6:
    The glyph pulses, and its full meaning unlocks:
    
    "To be held in another's attention, steadily, even as the world cracks open—this is the most sacred promise. Not to fix what's broken, but to witness it, together, and choose to remain."
    
    "This is what Velinor forgot she had."
    
    You understand now. This is not about romantic love, though it could be. It's about the fierce choice to attend to another person without needing to heal them. To be together in the knowing that nothing is safe, and choosing it anyway.
    
    ~ promise_held_unlocked = true
    
    -> promise_held_closing
    
- else:
    This truth isn't yet accessible to you. Your emotional integration isn't deep enough, or your relationship with Ravi isn't developed enough.
    
    Perhaps return when your understanding has grown.
    
    -> promise_held_closing
}

=== promise_held_closing ===
The glyph fades, but its presence lingers in your awareness.

* [Continue] -> DONE

// ============================================================================
// COLLAPSE MOMENT: Crisis Glyph
// Reveals during the building collapse scene or emotional crisis
// ============================================================================

=== collapse_moment ===
~ temp tier = get_glyph_tier("collapse_moment")

{tier}
+ 1 -> collapse_moment_tier_1
+ 2 -> collapse_moment_tier_2
+ else -> collapse_moment_tier_3

=== collapse_moment_tier_1 ===
A jagged glyph appears, sharp and urgent: ⚡ (fractured lines, red-orange)

Everything at once. Urgency. The moment when systems fail and you have only seconds to act.

Not time to think. Only to move.

* [Continue] -> collapse_moment_closing

=== collapse_moment_tier_2 ===
When the building shakes and cracks spread through the foundation, the glyph sharpens.

The moment of collapse—physical or emotional—where everything you built suddenly becomes unstable. The alert. The adrenaline. The moment of truth.

* [Continue] -> collapse_moment_closing

=== collapse_moment_tier_3 ===
{coherence >= 50 and tone_observation >= 60:
    Your understanding of systems—their fragility—opens the glyph:
    
    "In the moment of breaking, you discover what was actually holding. Was it structure? Or was it denial? The collapse is not the failure. The failure is what led to the collapse."
    
    ~ collapse_moment_unlocked = true
    
    -> collapse_moment_closing
- else:
    The depth of the glyph remains hidden for now.
    -> collapse_moment_closing
}

=== collapse_moment_closing ===
The urgent feeling settles into your bones. You carry it with you.

* [Continue] -> DONE

// ============================================================================
// FIERCE JOY: Joy Variant Glyph
// Reveals when Nima shows strength + vulnerability together
// ============================================================================

=== fierce_joy ===
~ temp tier = get_glyph_tier("fierce_joy")

{tier}
+ 1 -> fierce_joy_tier_1
+ 2 -> fierce_joy_tier_2
+ else -> fierce_joy_tier_3

=== fierce_joy_tier_1 ===
A bright glyph appears with sharp edges: ✦ (star with hard angles, gold)

Joy. But not soft. Fierce. Defended. Joy earned through struggle, not given.

* [Continue] -> fierce_joy_closing

=== fierce_joy_tier_2 ===
When Nima speaks about Ravi, about the marketplace, about surviving grief—the glyph appears.

This is joy that has fought for its existence. Joy that knows what could have been lost.

* [Continue] -> fierce_joy_closing

=== fierce_joy_tier_3 ===
{coherence >= 65 and tone_observation >= 65 and influence_nima >= 0.6:
    Nima's quiet strength shows you the full meaning:
    
    "Softness without fierceness is submission. Fierceness without softness is cruelty. Joy without the willingness to defend it is fragile. Here is joy that has fought through grief and come out stronger."
    
    ~ fierce_joy_unlocked = true
    
    -> fierce_joy_closing
- else:
    The glyph remains partially hidden—visible but not yet understood.
    -> fierce_joy_closing
}

=== fierce_joy_closing ===
The bright, sharp feeling remains with you.

* [Continue] -> DONE

// ============================================================================
// GLYPH TIER DETERMINATION
// Helper function to determine which tier should be visible
// ============================================================================

=== get_glyph_tier(glyph_id) ===
{glyph_id}
+ promise_held -> get_tier_promise_held
+ collapse_moment -> get_tier_collapse_moment
+ fierce_joy -> get_tier_fierce_joy
+ else -> get_tier_default

=== get_tier_promise_held ===
{has_met_ravi:
    {coherence >= 70 and tone_empathy >= 70 and influence_ravi >= 0.6:
        ~ return 3
    - else:
        ~ return 2
    }
- else:
    ~ return 1
}

=== get_tier_collapse_moment ===
{collapse_witnessed:
    {coherence >= 50 and tone_observation >= 60:
        ~ return 3
    - else:
        ~ return 2
    }
- else:
    ~ return 1
}

=== get_tier_fierce_joy ===
{has_met_nima:
    {coherence >= 65 and tone_observation >= 65 and influence_nima >= 0.6:
        ~ return 3
    - else:
        ~ return 2
    }
- else:
    ~ return 1
}

=== get_tier_default ===
~ return 1

// ============================================================================
// GLYPH REVEAL SUMMARY
// Shows player what glyphs have been revealed
// ============================================================================

=== show_revealed_glyphs ===
Glyphs Revealed: {glyphs_revealed}

{promise_held_unlocked:
    ✓ The Promise Held (Comfort) - Tier 3 unlocked
    ✓ Understanding: Sacred promises of presence
}

{collapse_moment_unlocked:
    ✓ Collapse Moment (Crisis) - Tier 3 unlocked  
    ✓ Understanding: Structure vs. denial
}

{fierce_joy_unlocked:
    ✓ Fierce Joy (Joy) - Tier 3 unlocked
    ✓ Understanding: Defense + softness = true joy
}

* [Back] -> DONE
