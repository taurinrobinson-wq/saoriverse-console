# Phase 1 Architecture Visual

## Data Flow: Player Choice â†’ NPC Response

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PLAYER MAKES DIALOGUE CHOICE                                         â”‚
â”‚ e.g., "Show compassion to the merchant"                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ TRAIT_SYSTEM.py: TraitChoice created                                 â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚ â”‚ choice_id: "intro_01"                                        â”‚   â”‚
â”‚ â”‚ primary_trait: EMPATHY                                       â”‚   â”‚
â”‚ â”‚ trait_weight: 0.3                                            â”‚   â”‚
â”‚ â”‚ npc_name: "Nima"                                             â”‚   â”‚
â”‚ â”‚ scene_name: "First Meeting"                                  â”‚   â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ TRAIT_SYSTEM.py: TraitProfiler.record_choice()                      â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚ â”‚ 1. Update empathy: 50.0 + (0.3 * 10) = 53.0                â”‚   â”‚
â”‚ â”‚ 2. Add to recent_choices deque (max 10 items)              â”‚   â”‚
â”‚ â”‚ 3. Update coherence based on pattern consistency           â”‚   â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ COHERENCE_CALCULATOR.py: get_coherence_report()                    â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚ â”‚ Recent choices: [EMPATHY, EMPATHY, SKEPTICISM]              â”‚   â”‚
â”‚ â”‚ Pattern analysis:                                             â”‚   â”‚
â”‚ â”‚   - Empathy count: 0.6                                       â”‚   â”‚
â”‚ â”‚   - Skepticism count: 0.3                                    â”‚   â”‚
â”‚ â”‚   - Total: 1.0                                               â”‚   â”‚
â”‚ â”‚ Coherence = 0.6 / 1.0 = 60% = 60 points = "MIXED"         â”‚   â”‚
â”‚ â”‚                                                              â”‚   â”‚
â”‚ â”‚ Report:                                                       â”‚   â”‚
â”‚ â”‚   - overall_coherence: 60.0                                  â”‚   â”‚
â”‚ â”‚   - npc_trust_level: "moderate"                              â”‚   â”‚
â”‚ â”‚   - dialogue_depth: "social"                                 â”‚   â”‚
â”‚ â”‚   - primary_pattern: EMPATHY                                 â”‚   â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ NPC_RESPONSE_ENGINE.py: get_npc_response()                          â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚ â”‚ Nima profile: EMPATHETIC personality                         â”‚   â”‚
â”‚ â”‚   - prefers_traits: [EMPATHY, INTEGRATION]                   â”‚   â”‚
â”‚ â”‚   - uncomfortable_traits: []                                  â”‚   â”‚
â”‚ â”‚                                                              â”‚   â”‚
â”‚ â”‚ Player's primary trait: EMPATHY                              â”‚   â”‚
â”‚ â”‚ Trait comfort: 0.9 (Nima loves empathy)                      â”‚   â”‚
â”‚ â”‚ Coherence: 60 = dialogue_depth: "social"                     â”‚   â”‚
â”‚ â”‚ Conflict level: "ally" (shares EMPATHY)                      â”‚   â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ DIALOGUE ENGINE (FirstPerson orchestrator)                           â”‚
â”‚ Uses NPC response parameters to generate dialogue:                   â”‚
â”‚   - Trait comfort: 0.9 (high alignment)                              â”‚
â”‚   - Coherence: 60 (moderate)                                         â”‚
â”‚   - Dialogue depth: "social" (shares moderate context)              â”‚
â”‚   - Conflict: "ally" (supports player)                               â”‚
â”‚                                                                      â”‚
â”‚ Example response: "I hear you, and I appreciate your concern."       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ STREAMLIT UI                                                         â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚ â”‚ TRAIT METERS:                           COHERENCE:           â”‚   â”‚
â”‚ â”‚ Empathy:     â–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘ 60%    MIXED (60/100)                â”‚   â”‚
â”‚ â”‚ Skepticism:  â–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘  10%    NPC TRUST: moderate          â”‚   â”‚
â”‚ â”‚ Integration: â–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘  10%    DIALOGUE: social             â”‚   â”‚
â”‚ â”‚ Awareness:   â–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘  10%                                  â”‚   â”‚
â”‚ â”‚                                                              â”‚   â”‚
â”‚ â”‚ Nima perceives you as: Empathetic Ally                       â”‚   â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Coherence Calculation Formula

```
Coherence = (max_trait_weight / total_weight) * 100

Example 1: Consistent player
  Recent 5 choices: [EMPATHY, EMPATHY, EMPATHY, EMPATHY, SKEPTICISM]
  Empathy weight: 0.3 * 4 = 1.2
  Skepticism weight: 0.3 * 1 = 0.3
  Total: 1.5
  Coherence = (1.2 / 1.5) * 100 = 80 = "CLEAR"

Example 2: Mixed player
  Recent 10 choices: [E, S, I, A, E, S, I, A, E, S]
  Each trait weight: 0.3 * 2 = 0.6
  Total: 2.4
  Coherence = (0.6 / 2.4) * 100 = 25 = "CONTRADICTORY"

Example 3: Balanced player (valid coherent pattern)
  Recent 4 choices: [E, E, I, I]
  Empathy weight: 0.6
  Integration weight: 0.6
  Total: 1.2
  Coherence = (0.6 / 1.2) * 100 = 50 = "MIXED" (genuine synthesis)
```

---

## NPC Trait Compatibility Matrix

```
                Empathy  Skepticism  Integration  Awareness
Saori           Neutral    Neutral      â˜…â˜…â˜…â˜…â˜…      â˜…â˜…â˜…â˜…â˜…
(Integrator)

Ravi            âœ— âœ— âœ—     â˜…â˜…â˜…â˜…â˜…       Neutral     â˜…â˜…â˜…â˜…â˜…
(Skeptical)

Nima            â˜…â˜…â˜…â˜…â˜…      âœ— âœ—        â˜…â˜…â˜…â˜…        Neutral
(Empathetic)

Malrik          âœ— âœ— âœ—     â˜…â˜…â˜…â˜…â˜…       Neutral     â˜…â˜…â˜…â˜…
(Skeptic)

Elenya          â˜…â˜…â˜…â˜…â˜…      Neutral     â˜…â˜…â˜…â˜…â˜…       Neutral
(Empathetic)

Cal           Neutral    Neutral     â˜…â˜…â˜…â˜…        â˜…â˜…â˜…â˜…â˜…
(Aware)

Legend:
â˜…â˜…â˜…â˜…â˜… = "ally" (trust increases, dialogue deepens)
â˜…â˜…â˜…â˜… = "neutral" (baseline interaction)
âœ— âœ— âœ— = "opposed" (high coherence needed to overcome suspicion)
```

---

## Coherence Level Thresholds

```
95    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
      â•‘   CRYSTAL_CLEAR                        â•‘
      â•‘   "Perfectly consistent"               â•‘
      â•‘   - NPC trust: high                    â•‘
      â•‘   - Dialogue: intimate                 â•‘
80    â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
      â•‘   CLEAR                                â•‘
      â•‘   "Mostly consistent"                  â•‘
      â•‘   - NPC trust: high                    â•‘
      â•‘   - Dialogue: personal                 â•‘
60    â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
      â•‘   MIXED                                â•‘
      â•‘   "Holds multiple truths"              â•‘
      â•‘   - NPC trust: moderate                â•‘
      â•‘   - Dialogue: social                   â•‘
40    â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
      â•‘   CONFUSED                             â•‘
      â•‘   "Contradictory patterns"             â•‘
      â•‘   - NPC trust: low                     â•‘
      â•‘   - Dialogue: guarded                  â•‘
20    â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
      â•‘   CONTRADICTORY                        â•‘
      â•‘   "Wildly inconsistent"                â•‘
      â•‘   - NPC trust: suspicious              â•‘
      â•‘   - Dialogue: minimal                  â•‘
0     â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## Class Hierarchy

```
TraitSystem (trait_system.py)
â”œâ”€â”€ TraitType (enum)
â”‚   â”œâ”€â”€ EMPATHY
â”‚   â”œâ”€â”€ SKEPTICISM
â”‚   â”œâ”€â”€ INTEGRATION
â”‚   â””â”€â”€ AWARENESS
â”œâ”€â”€ TraitChoice (dataclass)
â”‚   â”œâ”€â”€ choice_id
â”‚   â”œâ”€â”€ primary_trait
â”‚   â”œâ”€â”€ secondary_trait (optional)
â”‚   â””â”€â”€ coherence_bonus
â”œâ”€â”€ TraitProfile (dataclass)
â”‚   â”œâ”€â”€ empathy: 0-100
â”‚   â”œâ”€â”€ skepticism: 0-100
â”‚   â”œâ”€â”€ integration: 0-100
â”‚   â”œâ”€â”€ awareness: 0-100
â”‚   â”œâ”€â”€ coherence: 0-100
â”‚   â””â”€â”€ recent_choices: deque[TraitChoice] (max 10)
â””â”€â”€ TraitProfiler
    â”œâ”€â”€ record_choice(trait_choice)
    â”œâ”€â”€ get_primary_trait()
    â”œâ”€â”€ get_trait_pattern()
    â”œâ”€â”€ is_coherent()
    â””â”€â”€ get_trait_summary()

CoherenceSystem (coherence_calculator.py)
â”œâ”€â”€ CoherenceLevel (enum)
â”‚   â”œâ”€â”€ CRYSTAL_CLEAR (95)
â”‚   â”œâ”€â”€ CLEAR (80)
â”‚   â”œâ”€â”€ MIXED (60)
â”‚   â”œâ”€â”€ CONFUSED (40)
â”‚   â””â”€â”€ CONTRADICTORY (20)
â”œâ”€â”€ CoherenceReport (dataclass)
â”‚   â”œâ”€â”€ overall_coherence
â”‚   â”œâ”€â”€ level
â”‚   â”œâ”€â”€ primary_pattern
â”‚   â”œâ”€â”€ npc_trust_level
â”‚   â””â”€â”€ dialogue_depth
â””â”€â”€ CoherenceCalculator
    â”œâ”€â”€ calculate_coherence()
    â”œâ”€â”€ get_pattern_analysis()
    â”œâ”€â”€ get_coherence_report()
    â””â”€â”€ would_be_coherent(next_choice)

NPCSystem (npc_response_engine.py)
â”œâ”€â”€ NPCPersonalityType (enum)
â”‚   â”œâ”€â”€ EMPATHETIC
â”‚   â”œâ”€â”€ SKEPTICAL
â”‚   â”œâ”€â”€ INTEGRATOR
â”‚   â””â”€â”€ AWARE
â”œâ”€â”€ NPCDialogueProfile (dataclass)
â”‚   â”œâ”€â”€ personality_type
â”‚   â”œâ”€â”€ preferred_traits
â”‚   â””â”€â”€ uncomfortable_traits
â””â”€â”€ NPCResponseEngine
    â”œâ”€â”€ get_npc_response(npc_name, prompt)
    â”œâ”€â”€ get_npc_reaction_to_choice(npc_name, trait)
    â”œâ”€â”€ should_npc_trust_player(npc_name)
    â”œâ”€â”€ get_npc_conflict_level(npc_name)
    â””â”€â”€ get_npc_dialogue_depth(npc_name)
```

---

## Next: Phase 2 Integration Points

Phase 2 will connect these systems into the game loop:

```
orchestrator.py (main game loop)
  â”œâ”€ Create TraitProfiler on game start
  â”œâ”€ On each dialogue choice:
  â”‚  â”œâ”€ Create TraitChoice
  â”‚  â”œâ”€ Call profiler.record_choice()
  â”‚  â”œâ”€ Call coherence_calculator.get_coherence_report()
  â”‚  â””â”€ Call npc_response_engine.get_npc_response()
  â”œâ”€ Pass parameters to FirstPerson dialogue generator
  â””â”€ Update Streamlit UI display

streamlit UI (velinor_scenes_test.py)
  â”œâ”€ Show trait meters (4 bars, 0-100 each)
  â”œâ”€ Show coherence status (level + percentage)
  â”œâ”€ Show primary pattern with narrative description
  â”œâ”€ Show NPC perception for each NPC in scene
  â””â”€ Show dialogue history with trait mapping

Scene implementation (marketplace_scene.py - Phase 2)
  â”œâ”€ Define dialogue choices as TraitChoice objects
  â”œâ”€ Modify branching based on coherence/pattern
  â”œâ”€ Lock certain paths for low-coherence players
  â””â”€ Adjust NPC behavior based on perceived trait
```

