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
- value > max_val:
    ~ return max_val
- else:
    ~ return value
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
~ temp mean = average(tone_empathy, tone_skepticism, tone_integration, tone_awareness)
~ temp dev_e = absolute(tone_empathy - mean)
~ temp dev_s = absolute(tone_skepticism - mean)
~ temp dev_i = absolute(tone_integration - mean)
~ temp dev_a = absolute(tone_awareness - mean)
~ temp avg_dev = average(dev_e, dev_s, dev_i, dev_a)
~ coherence = round(100 - avg_dev)
~ return coherence

// ============================================================================
// TONE STAT UTILITIES
// ============================================================================

=== tone_summary() ===
Empathy: {tone_empathy}
Skepticism: {tone_skepticism}
Integration: {tone_integration}
Awareness: {tone_awareness}
Coherence: {coherence}

=== highest_tone() ===
{tone_empathy > tone_skepticism and tone_empathy > tone_integration and tone_empathy > tone_awareness:
    ~ return "empathy"
- tone_skepticism > tone_integration and tone_skepticism > tone_awareness:
    ~ return "skepticism"
- tone_integration > tone_awareness:
    ~ return "integration"
- else:
    ~ return "awareness"
}

=== lowest_tone() ===
{tone_empathy < tone_skepticism and tone_empathy < tone_integration and tone_empathy < tone_awareness:
    ~ return "empathy"
- tone_skepticism < tone_integration and tone_skepticism < tone_awareness:
    ~ return "skepticism"
- tone_integration < tone_awareness:
    ~ return "integration"
- else:
    ~ return "awareness"
}

=== get_tone_name(stat) ===
{stat == "empathy":
    ~ return "Empathy (Compassion)"
- stat == "skepticism":
    ~ return "Skepticism (Critical Thinking)"
- stat == "integration":
    ~ return "Integration (Synthesis)"
- stat == "awareness":
    ~ return "Awareness (Self-Understanding)"
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
{npc_primary_tone == "empathy":
    ~ temp npc_primary_value = tone_empathy
- npc_primary_tone == "skepticism":
    ~ temp npc_primary_value = tone_skepticism
- npc_primary_tone == "integration":
    ~ temp npc_primary_value = tone_integration
- npc_primary_tone == "awareness":
    ~ temp npc_primary_value = tone_awareness
}

{npc_secondary_tone == "empathy":
    ~ temp npc_secondary_value = tone_empathy
- npc_secondary_tone == "skepticism":
    ~ temp npc_secondary_value = tone_skepticism
- npc_secondary_tone == "integration":
    ~ temp npc_secondary_value = tone_integration
- npc_secondary_tone == "awareness":
    ~ temp npc_secondary_value = tone_awareness
}

~ temp resonance = (npc_primary_value + npc_secondary_value) / 2
~ return resonance

// ============================================================================
// CHOICE CONSEQUENCES TEMPLATES
// Use these patterns to consistently track choice impacts
// ============================================================================

=== consequence_empathetic ===
~ adjust_tone("empathy", 8)
~ adjust_tone("awareness", 3)
~ coherence = calculate_coherence()
You acted with compassion.

=== consequence_skeptical ===
~ adjust_tone("skepticism", 8)
~ adjust_tone("awareness", 3)
~ coherence = calculate_coherence()
You questioned deeply.

=== consequence_integrative ===
~ adjust_tone("integration", 10)
~ adjust_tone("empathy", 2)
~ adjust_tone("skepticism", 2)
~ coherence = calculate_coherence()
You held both truths simultaneously.

=== consequence_reflective ===
~ adjust_tone("awareness", 8)
~ adjust_tone("integration", 3)
~ coherence = calculate_coherence()
You looked inward.

=== consequence_balanced ===
~ adjust_tone("awareness", 3)
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
    "empathy": {tone_empathy},
    "skepticism": {tone_skepticism},
    "integration": {tone_integration},
    "awareness": {tone_awareness}
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
