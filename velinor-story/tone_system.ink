// ============================================================================
// TONE SYSTEM: Emotional OS Variables & Mechanics
// ============================================================================
//
// The four TONE dimensions that drive Velinor's narrative.
// Every choice modifies these stats.
// Coherence (harmony between stats) determines which dialogue unlocks.
//
// ============================================================================

// --- TONE Stats (0-100) ---
VAR tone_trust = 50
VAR tone_observation = 50
VAR tone_empathy = 50
VAR tone_narrative_presence = 50

// --- Coherence Value (updated after each choice) ---
VAR coherence = 100

// --- Glyph Tracking ---
VAR glyphs_revealed = 0
VAR promise_held_unlocked = false
VAR collapse_moment_unlocked = false
VAR fierce_joy_unlocked = false

// --- NPC Influence (0.0 - 1.0, starts at 0.5 neutral) ---
VAR influence_saori = 0.5
VAR influence_ravi = 0.5
VAR influence_nima = 0.5
VAR influence_malrik = 0.5
VAR influence_elenya = 0.5
VAR influence_nordia = 0.5
VAR influence_sealina = 0.5
VAR influence_lark = 0.5
VAR influence_rasha = 0.5
VAR influence_sera = 0.5
VAR influence_inodora = 0.5
VAR influence_helia = 0.5
VAR influence_elka = 0.5
VAR influence_kaelen = 0.5
VAR influence_mariel = 0.5
VAR influence_dalen = 0.5
VAR influence_drossel = 0.5
VAR influence_korrin = 0.5
VAR influence_veynar = 0.5
VAR influence_coren = 0.5
VAR influence_juria = 0.5

// --- Story Progression ---
VAR has_met_ravi = false
VAR has_met_nima = false
VAR has_met_saori = true  // Starts with Saori
VAR marketplace_visited = false
VAR collapse_witnessed = false

// ============================================================================
// TONE ADJUSTMENT FUNCTIONS
// ============================================================================

=== adjust_tone(stat, delta) ===
{stat}
+ trust -> adjust_tone_trust
+ observation -> adjust_tone_observation
+ empathy -> adjust_tone_empathy
+ else -> adjust_tone_narrative_presence

=== adjust_tone_trust ===
~ tone_trust = clamp(tone_trust + delta, 0, 100)
-> DONE

=== adjust_tone_observation ===
~ tone_observation = clamp(tone_observation + delta, 0, 100)
-> DONE

=== adjust_tone_empathy ===
~ tone_empathy = clamp(tone_empathy + delta, 0, 100)
-> DONE

=== adjust_tone_narrative_presence ===
~ tone_narrative_presence = clamp(tone_narrative_presence + delta, 0, 100)
-> DONE

=== adjust_influence(npc_name, delta) ===
{npc_name}
+ ravi -> adjust_influence_ravi
+ nima -> adjust_influence_nima
+ saori -> adjust_influence_saori
+ malrik -> adjust_influence_malrik
+ elenya -> adjust_influence_elenya
+ nordia -> adjust_influence_nordia
+ sealina -> adjust_influence_sealina
+ lark -> adjust_influence_lark
+ rasha -> adjust_influence_rasha
+ sera -> adjust_influence_sera
+ inodora -> adjust_influence_inodora
+ helia -> adjust_influence_helia
+ elka -> adjust_influence_elka
+ kaelen -> adjust_influence_kaelen
+ mariel -> adjust_influence_mariel
+ dalen -> adjust_influence_dalen
+ drossel -> adjust_influence_drossel
+ korrin -> adjust_influence_korrin
+ veynar -> adjust_influence_veynar
+ coren -> adjust_influence_coren
+ juria -> adjust_influence_juria
+ else -> adjust_influence_default

=== adjust_influence_ravi ===
~ influence_ravi = clamp(influence_ravi + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_nima ===
~ influence_nima = clamp(influence_nima + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_saori ===
~ influence_saori = clamp(influence_saori + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_malrik ===
~ influence_malrik = clamp(influence_malrik + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_elenya ===
~ influence_elenya = clamp(influence_elenya + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_nordia ===
~ influence_nordia = clamp(influence_nordia + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_sealina ===
~ influence_sealina = clamp(influence_sealina + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_lark ===
~ influence_lark = clamp(influence_lark + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_rasha ===
~ influence_rasha = clamp(influence_rasha + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_sera ===
~ influence_sera = clamp(influence_sera + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_inodora ===
~ influence_inodora = clamp(influence_inodora + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_helia ===
~ influence_helia = clamp(influence_helia + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_elka ===
~ influence_elka = clamp(influence_elka + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_kaelen ===
~ influence_kaelen = clamp(influence_kaelen + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_mariel ===
~ influence_mariel = clamp(influence_mariel + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_dalen ===
~ influence_dalen = clamp(influence_dalen + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_drossel ===
~ influence_drossel = clamp(influence_drossel + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_korrin ===
~ influence_korrin = clamp(influence_korrin + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_veynar ===
~ influence_veynar = clamp(influence_veynar + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_coren ===
~ influence_coren = clamp(influence_coren + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_juria ===
~ influence_juria = clamp(influence_juria + delta, 0.0, 1.0)
-> DONE

=== adjust_influence_default ===
-> DONE

// Cascade influence: when one NPC's influence increases, nearby NPCs gain secondary boost
=== cascade_influence(npc_name, primary_delta) ===
~ adjust_influence(npc_name, primary_delta)
{npc_name}
+ ravi -> cascade_ravi
+ nima -> cascade_nima
+ malrik -> cascade_malrik
+ else -> cascade_default

=== cascade_ravi ===
~ adjust_influence("nima", primary_delta * 0.7)
~ adjust_influence("sera", primary_delta * 0.5)
-> DONE

=== cascade_nima ===
~ adjust_influence("ravi", primary_delta * 0.7)
-> DONE

=== cascade_malrik ===
~ adjust_influence("elenya", primary_delta * 0.8)
~ adjust_influence("nordia", primary_delta * 0.5)
-> DONE

=== cascade_default ===
-> DONE

// ============================================================================
// COHERENCE CALCULATION
// ============================================================================
//
// Formula: coherence = 100 - average_deviation(empathy, skepticism, integration, awareness)
// 
// High coherence (80+): Emotionally integrated, can hold multiple truths
// Medium coherence (50-80): Growing alignment
// Low coherence (0-50): Conflict, fragmentation
//
// ============================================================================

=== calculate_coherence() ===
    ~ temp mean = (tone_trust + tone_observation + tone_empathy + tone_narrative_presence) / 4
    ~ temp dev_t = absolute(tone_trust - mean)
    ~ temp dev_o = absolute(tone_observation - mean)
    ~ temp dev_e = absolute(tone_empathy - mean)
    ~ temp dev_n = absolute(tone_narrative_presence - mean)
    ~ temp avg_dev = (dev_t + dev_o + dev_e + dev_n) / 4
    ~ coherence = 100 - avg_dev
    ~ return coherence

// ============================================================================
// CHOICE IMPACT TEMPLATES
// These are example patterns for how choices affect TONE
// Use these patterns throughout the story
// ============================================================================

=== choice_trust_connection ===
// "I want to connect with you"
~ adjust_tone("trust", 8)
~ adjust_tone("empathy", 5)
~ coherence = calculate_coherence()

=== choice_observation_question ===
// "Why should I believe you?"
~ adjust_tone("observation", 8)
~ adjust_tone("narrative_presence", 3)
~ coherence = calculate_coherence()

=== choice_empathy_balanced ===
// "Both are right in different ways"
~ adjust_tone("empathy", 10)
~ adjust_tone("observation", 3)
~ adjust_tone("trust", 3)
~ coherence = calculate_coherence()

=== choice_narrative_presence_reflect ===
// "I need to understand myself first"
~ adjust_tone("narrative_presence", 8)
~ adjust_tone("empathy", 4)
~ coherence = calculate_coherence()

=== choice_neutral ===
// "I'll listen without judging"
~ adjust_tone("observation", 2)
~ coherence = calculate_coherence()

// ============================================================================
// TONE DESCRIPTION FUNCTIONS (for flavor text)
// ============================================================================

=== describe_tone_state ===
{tone_trust > 70:
    You feel open to connection with others.
- tone_trust < 30:
    You feel defensive and wary of others.
- else:
    You're cautious but not completely closed off.
}
-> DONE

{tone_observation > 70:
    You pick up on subtle details and nuances.
- tone_observation < 30:
    You see things in broad strokes.
- else:
    You notice some things but miss others.
}
-> DONE

{tone_empathy > 70:
    You feel deeply attuned to others' emotions.
- tone_empathy < 30:
    You feel distant from others' feelings.
- else:
    You have some emotional awareness.
}
-> DONE

{tone_narrative_presence > 70:
    You project a commanding, visible presence.
- tone_narrative_presence < 30:
    You fade into the background.
- else:
    You're neither particularly visible nor hidden.
}
-> DONE

=== describe_coherence ===
{coherence >= 80:
    You feel emotionally integrated. Multiple truths can coexist within you.
- coherence >= 60:
    You're finding your balance, but conflicting feelings still pull at you.
- coherence >= 40:
    You're fragmented. Contradictions feel impossible to hold.
- else:
    You are emotionally fractured. Nothing makes sense.
}
