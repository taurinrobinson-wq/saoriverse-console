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
VAR tone_empathy = 50
VAR tone_skepticism = 50
VAR tone_integration = 50
VAR tone_awareness = 50

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
{stat == "empathy":
    ~ tone_empathy = clamp(tone_empathy + delta, 0, 100)
- stat == "skepticism":
    ~ tone_skepticism = clamp(tone_skepticism + delta, 0, 100)
- stat == "integration":
    ~ tone_integration = clamp(tone_integration + delta, 0, 100)
- stat == "awareness":
    ~ tone_awareness = clamp(tone_awareness + delta, 0, 100)
- else:
}

=== adjust_influence(npc_name, delta) ===
{npc_name == "ravi":
    ~ influence_ravi = clamp(influence_ravi + delta, 0.0, 1.0)
- npc_name == "nima":
    ~ influence_nima = clamp(influence_nima + delta, 0.0, 1.0)
- npc_name == "saori":
    ~ influence_saori = clamp(influence_saori + delta, 0.0, 1.0)
- else:
}

// Cascade influence: when one NPC's influence increases, nearby NPCs gain secondary boost
=== cascade_influence(npc_name, primary_delta) ===
~ adjust_influence(npc_name, primary_delta)

{npc_name == "ravi":
    ~ adjust_influence("nima", primary_delta * 0.7)  // Nima gets 70% of Ravi's boost (couple)
    ~ adjust_influence("sera", primary_delta * 0.5)  // Sera gets 50% (learning from Ravi)
- npc_name == "nima":
    ~ adjust_influence("ravi", primary_delta * 0.7)  // Symmetrical
- npc_name == "malrik":
    ~ adjust_influence("elenya", primary_delta * 0.8)  // Strong connection
    ~ adjust_influence("nordia", primary_delta * 0.5)
- else:
}

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
    ~ temp mean = (tone_empathy + tone_skepticism + tone_integration + tone_awareness) / 4
    ~ temp dev_e = absolute(tone_empathy - mean)
    ~ temp dev_s = absolute(tone_skepticism - mean)
    ~ temp dev_i = absolute(tone_integration - mean)
    ~ temp dev_a = absolute(tone_awareness - mean)
    ~ temp avg_dev = (dev_e + dev_s + dev_i + dev_a) / 4
    ~ coherence = 100 - avg_dev
    ~ return coherence

// ============================================================================
// CHOICE IMPACT TEMPLATES
// These are example patterns for how choices affect TONE
// Use these patterns throughout the story
// ============================================================================

=== choice_empathy_care ===
// "I want to help you"
~ adjust_tone("empathy", 8)
~ adjust_tone("integration", 5)
~ coherence = calculate_coherence()

=== choice_skepticism_question ===
// "Why should I believe you?"
~ adjust_tone("skepticism", 8)
~ adjust_tone("awareness", 3)
~ coherence = calculate_coherence()

=== choice_integration_both ===
// "Both are right in different ways"
~ adjust_tone("integration", 10)
~ adjust_tone("empathy", 3)
~ adjust_tone("skepticism", 3)
~ coherence = calculate_coherence()

=== choice_awareness_reflect ===
// "I need to understand myself first"
~ adjust_tone("awareness", 8)
~ adjust_tone("integration", 4)
~ coherence = calculate_coherence()

=== choice_neutral ===
// "I'll listen without judging"
~ adjust_tone("awareness", 2)
~ coherence = calculate_coherence()

// ============================================================================
// TONE DESCRIPTION FUNCTIONS (for flavor text)
// ============================================================================

=== describe_tone_state ===
{tone_empathy > 70:
    You feel open and compassionate.
- tone_empathy < 30:
    You feel guarded and distant.
- else:
    You feel uncertain about others.
}

{tone_skepticism > 70:
    You question everything.
- tone_skepticism < 30:
    You accept what you're told.
- else:
    You try to balance belief and doubt.
}

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
