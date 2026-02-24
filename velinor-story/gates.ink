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
{stat}
+ trust -> check_tone_trust
+ observation -> check_tone_observation
+ narrative_presence -> check_tone_narrative_presence
+ else -> check_tone_empathy

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
{npc_name}
+ ravi -> check_influence_ravi
+ nima -> check_influence_nima
+ saori -> check_influence_saori
+ malrik -> check_influence_malrik
+ else -> check_influence_elenya

=== check_influence_ravi ===
~ temp influence_value = influence_ravi
~ temp passes = influence_value >= threshold
~ return passes

=== check_influence_nima ===
~ temp influence_value = influence_nima
~ temp passes = influence_value >= threshold
~ return passes

=== check_influence_saori ===
~ temp influence_value = influence_saori
~ temp passes = influence_value >= threshold
~ return passes

=== check_influence_malrik ===
~ temp influence_value = influence_malrik
~ temp passes = influence_value >= threshold
~ return passes

=== check_influence_elenya ===
~ temp influence_value = influence_elenya
~ temp passes = influence_value >= threshold
~ return passes

// ============================================================================
// GATE DESCRIPTIONS (for feedback)
// ============================================================================

=== describe_gate_requirement(gate_type, stat_or_npc, threshold) ===
{gate_type}
+ coherence -> describe_coherence_gate
+ tone -> describe_tone_gate
+ else -> describe_influence_gate

=== describe_coherence_gate ===
You need coherence {threshold}+. Current: {coherence}
-> DONE

=== describe_tone_gate(stat_or_npc, threshold) ===
You need {stat_or_npc} {threshold}+. Current: {get_tone_value(stat_or_npc)}
-> DONE

=== describe_influence_gate(stat_or_npc, threshold) ===
You need {stat_or_npc} trust {threshold}+. Current: {get_influence_value(stat_or_npc)}
-> DONE

=== get_tone_value(stat) ===
{stat}
+ trust -> return_tone_trust
+ observation -> return_tone_observation
+ narrative_presence -> return_tone_narrative_presence
+ else -> return_tone_empathy

=== return_tone_trust ===
~ return tone_trust

=== return_tone_observation ===
~ return tone_observation

=== return_tone_narrative_presence ===
~ return tone_narrative_presence

=== return_tone_empathy ===
~ return tone_empathy

=== get_influence_value(npc_name) ===
{npc_name}
+ ravi -> return_influence_ravi
+ nima -> return_influence_nima
+ saori -> return_influence_saori
+ else -> return_influence_default

=== return_influence_ravi ===
~ return influence_ravi

=== return_influence_nima ===
~ return influence_nima

=== return_influence_saori ===
~ return influence_saori

=== return_influence_default ===
~ return 0.5

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
{stat}
+ trust -> tone_gate_trust
+ observation -> tone_gate_observation
+ narrative_presence -> tone_gate_narrative_presence
+ else -> tone_gate_empathy

=== tone_gate_trust ===
{tone_trust >= threshold:
    {dialogue}
- else:
    This path isn't accessible to you yet.
}
-> DONE

=== tone_gate_observation ===
{tone_observation >= threshold:
    {dialogue}
- else:
    This path isn't accessible to you yet.
}
-> DONE

=== tone_gate_narrative_presence ===
{tone_narrative_presence >= threshold:
    {dialogue}
- else:
    This path isn't accessible to you yet.
}
-> DONE

=== tone_gate_empathy ===
{tone_empathy >= threshold:
    {dialogue}
- else:
    This path isn't accessible to you yet.
}
-> DONE

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
{reason}
+ low_coherence -> explain_low_coherence
+ low_empathy -> explain_low_empathy
+ low_observation -> explain_low_observation
+ low_narrative_presence -> explain_low_narrative_presence
+ low_trust -> explain_low_trust
+ low_influence -> explain_low_influence
+ else -> explain_default

=== explain_low_coherence ===
Your emotional conflict is too great right now. You need to find more harmony between your different feelings before this wisdom can reach you.
-> DONE

=== explain_low_empathy ===
Your heart is guarded right now. This dialogue requires vulnerability.
-> DONE

=== explain_low_observation ===
You're not paying close enough attention. This person needs to know you see clearly.
-> DONE

=== explain_low_narrative_presence ===
You can't hold both sides of this truth yet. You need to integrate your different perspectives first.
-> DONE

=== explain_low_trust ===
You don't yet believe in the possibility of change. Look within before looking outward.
-> DONE

=== explain_low_influence ===
This person doesn't trust you yet. Relationship takes time.
-> DONE

=== explain_default ===
This path isn't accessible to you right now.
-> DONE
