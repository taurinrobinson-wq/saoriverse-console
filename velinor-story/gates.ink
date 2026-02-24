// ============================================================================
// GATES: Emotional Gate Helper Functions
// ============================================================================
//
// Three types of gates:
//   1. TONE Gates — Require specific stat level
//   2. Coherence Gates — Require emotional harmony
//   3. Influence Gates — Based on relationship with specific NPC
//
// Gates determine which dialogue, choices, and glyphs are accessible
//
// ============================================================================

=== check_coherence_gate(threshold) ===
~ temp passes = coherence >= threshold
~ return passes

=== check_tone_gate(stat, threshold) ===
{
    - stat == "trust":
        -> check_tone_trust
    - stat == "observation":
        -> check_tone_observation
    - stat == "narrative_presence":
        -> check_tone_narrative_presence
    - else:
        -> check_tone_empathy
}

=== check_tone_trust ===
~ temp stat_value = tone_trust
~ temp passes = stat_value >= threshold
~ return passes

=== check_tone_observation ===
~ temp stat_value = tone_observation
~ temp passes = stat_value >= threshold
~ return passes

=== check_tone_narrative_presence ===
~ temp stat_value = tone_narrative_presence
~ temp passes = stat_value >= threshold
~ return passes

=== check_tone_empathy ===
~ temp stat_value = tone_empathy
~ temp passes = stat_value >= threshold
~ return passes

=== check_influence_gate(npc_name, threshold) ===
{npc_name == "ravi":
    ~ temp influence_value = influence_ravi
- npc_name == "nima":
    ~ temp influence_value = influence_nima
- npc_name == "saori":
    ~ temp influence_value = influence_saori
- npc_name == "malrik":
    ~ temp influence_value = influence_malrik
- else:
    ~ temp influence_value = influence_elenya
}

~ temp passes = influence_value >= threshold
~ return passes

// ============================================================================
// GATE DESCRIPTIONS (for feedback)
// ============================================================================

=== describe_gate_requirement(gate_type, stat_or_npc, threshold) ===
{gate_type == "coherence":
    You need coherence {threshold}+. Current: {coherence}
- gate_type == "tone":
    You need {stat_or_npc} {threshold}+. Current: {get_tone_value(stat_or_npc)}
- else:
    You need {stat_or_npc} trust {threshold}+. Current: {get_influence_value(stat_or_npc)}
}

=== get_tone_value(stat) ===
{
    - stat == "trust":
        ~ return tone_trust
    - stat == "observation":
        ~ return tone_observation
    - stat == "narrative_presence":
        ~ return tone_narrative_presence
    - else:
        ~ return tone_empathy
}

=== get_influence_value(npc_name) ===
{npc_name == "ravi":
    ~ return influence_ravi
- npc_name == "nima":
    ~ return influence_nima
- npc_name == "saori":
    ~ return influence_saori
- else:
    ~ return 0.5
}

// ============================================================================
// GATE OUTCOMES
// What happens when you pass/fail various gates
// ============================================================================

=== coherence_gate_unlocked(dialogue) ===
{coherence >= 70:
    You feel emotionally integrated. The deeper truth becomes accessible.
    {dialogue}
- else:
    This wisdom isn't yet accessible to you. Your emotional foundations aren't stable enough.
}

=== tone_gate_unlocked(stat, threshold, dialogue) ===
{
    - stat == "trust":
        ~ temp stat_value = tone_trust
    - stat == "observation":
        ~ temp stat_value = tone_observation
    - stat == "narrative_presence":
        ~ temp stat_value = tone_narrative_presence
    - else:
        ~ temp stat_value = tone_empathy
}

{stat_value >= threshold:
    {dialogue}
- else:
    This path isn't accessible to you yet.
}

=== influence_gate_unlocked(npc, threshold, dialogue) ===
~ temp influence_value = get_influence_value(npc)

{influence_value >= threshold:
    {npc} trusts you enough to share this.
    {dialogue}
- else:
    {npc} doesn't know you well enough yet.
}

// ============================================================================
// COMPLEX GATES (Multiple Conditions)
// ============================================================================

=== deep_dialogue_gate(npc, coherence_req, influence_req) ===
{coherence >= coherence_req and get_influence_value(npc) >= influence_req:
    ~ return true
- else:
    ~ return false
}

=== integration_check(min_empathy, min_observation, min_narrative_presence) ===
{tone_empathy >= min_empathy and tone_observation >= min_observation and tone_narrative_presence >= min_narrative_presence:
    ~ return true
- else:
    ~ return false
}

// ============================================================================
// GATE NARRATIVE EXPLANATIONS
// When a gate is not passed, explain why to the player
// ============================================================================

=== explain_unmet_gate(reason) ===
{reason == "low_coherence":
    Your emotional conflict is too great right now. You need to find more harmony between your different feelings before this wisdom can reach you.
    
- reason == "low_empathy":
    Your heart is guarded right now. This dialogue requires vulnerability.
    
- reason == "low_observation":
    You're not paying close enough attention. This person needs to know you see clearly.
    
- reason == "low_narrative_presence":
    You can't hold both sides of this truth yet. You need to integrate your different perspectives first.
    
- reason == "low_trust":
    You don't yet believe in the possibility of change. Look within before looking outward.
    
- reason == "low_influence":
    This person doesn't trust you yet. Relationship takes time.
    
- else:
    This path isn't accessible to you right now.
}
