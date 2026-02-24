// ============================================================================
// UTILITIES: Math Helpers & Shared Functions
// ============================================================================

// ============================================================================
// MATH FUNCTIONS
// ============================================================================

=== absolute(value) ===
{value < 0:
    ~ return value * -1
- else:
    ~ return value
}

=== round(value) ===
{value - floor(value) >= 0.5:
    ~ return floor(value) + 1
- else:
    ~ return floor(value)
}

=== clamp(value, min_val, max_val) ===
{value < min_val:
    ~ return min_val
- else:
    {value > max_val:
        ~ return max_val
    - else:
        ~ return value
    }
}

=== average(a, b, c, d) ===
~ return (a + b + c + d) / 4

=== percentage(part, whole) ===
~ return round((part / whole) * 100)

// ============================================================================
// COHERENCE CALCULATION
// Core formula: coherence = 100 - average_deviation
// ============================================================================

=== calculate_coherence() ===
~ temp mean = average(tone_trust, tone_observation, tone_empathy, tone_narrative_presence)
~ temp dev_t = absolute(tone_trust - mean)
~ temp dev_o = absolute(tone_observation - mean)
~ temp dev_e = absolute(tone_empathy - mean)
~ temp dev_n = absolute(tone_narrative_presence - mean)
~ temp avg_dev = average(dev_t, dev_o, dev_e, dev_n)
~ coherence = round(100 - avg_dev)
~ return coherence

// ============================================================================
// TONE STAT UTILITIES
// ============================================================================

=== tone_summary() ===
Trust: {tone_trust}
Observation: {tone_observation}
Narrative Presence: {tone_narrative_presence}
Empathy: {tone_empathy}
Coherence: {coherence}

=== highest_tone() ===
{tone_empathy > tone_observation and tone_empathy > tone_narrative_presence and tone_empathy > tone_trust:
    ~ return "empathy"
- else:
    {tone_observation > tone_narrative_presence and tone_observation > tone_trust:
        ~ return "observation"
    - else:
        {tone_narrative_presence > tone_trust:
            ~ return "narrative_presence"
        - else:
            ~ return "trust"
        }
    }
}

=== lowest_tone() ===
{tone_empathy < tone_observation and tone_empathy < tone_narrative_presence and tone_empathy < tone_trust:
    ~ return "empathy"
- else:
    {tone_observation < tone_narrative_presence and tone_observation < tone_trust:
        ~ return "observation"
    - else:
        {tone_narrative_presence < tone_trust:
            ~ return "narrative_presence"
        - else:
            ~ return "trust"
        }
    }
}

=== get_tone_name(stat) ===
{stat == "empathy":
    ~ return "Empathy (Compassion)"
- stat == "observation":
    ~ return "Observation (Critical Thinking)"
- stat == "narrative_presence":
    ~ return "Narrative Presence (Authority)"
- stat == "trust":
    ~ return "Trust (Connection)"
- else:
    ~ return "Unknown"
}

// ============================================================================
// COHERENCE DESCRIPTIONS
// ============================================================================

=== describe_coherence_level() ===
{coherence >= 80:
    Your emotional state is highly integrated. You can hold multiple truths simultaneously. The world feels less like contradictions and more like complexity you're capable of navigating.
    
- coherence >= 65:
    You're finding your balance. Different feelings pull at you, but you're learning to weave them together into something coherent.
    
- coherence >= 50:
    Your emotions are mixed. You feel pulled in different directions. Integration is possible, but requires intention.
    
- coherence >= 40:
    You're struggling to hold it together. Conflicting feelings feel unbearable. You need to find harmony soon.
    
- else:
    You are fractured. Everything feels impossible. The world doesn't make sense.
}

// ============================================================================
// EMOTIONAL RESONANCE CHECK
// Determines if player's emotional state resonates with an NPC
// ============================================================================

=== emotional_resonance(npc_primary_tone, npc_secondary_tone) ===
~ temp npc_primary_value = 50
~ temp npc_secondary_value = 50

{
    - npc_primary_tone == "empathy":
        ~ npc_primary_value = tone_empathy
    - npc_primary_tone == "observation":
        ~ npc_primary_value = tone_observation
    - npc_primary_tone == "narrative_presence":
        ~ npc_primary_value = tone_narrative_presence
    - npc_primary_tone == "trust":
        ~ npc_primary_value = tone_trust
}

{
    - npc_secondary_tone == "empathy":
        ~ npc_secondary_value = tone_empathy
    - npc_secondary_tone == "observation":
        ~ npc_secondary_value = tone_observation
    - npc_secondary_tone == "narrative_presence":
        ~ npc_secondary_value = tone_narrative_presence
    - npc_secondary_tone == "trust":
        ~ npc_secondary_value = tone_trust
}

~ temp resonance = (npc_primary_value + npc_secondary_value) / 2
~ return resonance

// ============================================================================
// CHOICE CONSEQUENCES TEMPLATES
// Use these patterns to consistently track choice impacts
// ============================================================================

=== consequence_empathetic ===
~ adjust_tone("empathy", 8)
~ adjust_tone("observation", 3)
~ coherence = calculate_coherence()
You acted with compassion.

=== consequence_observant ===
~ adjust_tone("observation", 8)
~ adjust_tone("observation", 3)
~ coherence = calculate_coherence()
You questioned deeply.

=== consequence_narrative ===
~ adjust_tone("narrative_presence", 10)
~ adjust_tone("empathy", 2)
~ adjust_tone("observation", 2)
~ coherence = calculate_coherence()
You held both truths simultaneously.

=== consequence_reflective ===
~ adjust_tone("trust", 8)
~ adjust_tone("narrative_presence", 3)
~ coherence = calculate_coherence()
You looked inward.

=== consequence_balanced ===
~ adjust_tone("observation", 3)
~ coherence = calculate_coherence()
You remained centered.

// ============================================================================
// FLAVOR TEXT GENERATORS
// ============================================================================

=== generate_coherence_flavor() ===
{coherence >= 80:
    A profound sense of alignment flows through you.
- coherence >= 60:
    You feel more at peace with your contradictions.
- coherence >= 40:
    You're aware of the tension within yourself.
- else:
    Everything feels fractured and impossible.
}

=== generate_tone_shift_flavor(stat, delta) ===
{delta > 0:
    You feel more {get_tone_name(stat)}.
- delta < 0:
    You feel less {get_tone_name(stat)}.
- else:
    Your {get_tone_name(stat)} remains unchanged.
}

// ============================================================================
// STATE EXPORT (For Backend Integration)
// ============================================================================

=== export_game_state() ===
This would be exported as JSON to the Python backend:

{
  "tone": {
    "trust": {tone_trust},
    "observation": {tone_observation},
    "empathy": {tone_empathy},
    "narrative_presence": {tone_narrative_presence}
  },
  "coherence": {coherence},
  "influence": {
    "saori": {influence_saori},
    "ravi": {influence_ravi},
    "nima": {influence_nima}
  },
  "glyphs_revealed": {glyphs_revealed},
  "progress": {
    "met_saori": {has_met_saori},
    "met_ravi": {has_met_ravi},
    "met_nima": {has_met_nima}
  }
}
