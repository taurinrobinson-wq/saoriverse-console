# Phase 1 Architecture Visual

## Data Flow: Player Choice → NPC Response

```
┌─────────────────────────────────────────────────────────────────────┐
│ PLAYER MAKES DIALOGUE CHOICE                                         │
│ e.g., "Show compassion to the merchant"                              │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TRAIT_SYSTEM.py: TraitChoice created                                 │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ choice_id: "intro_01"                                        │   │
│ │ primary_trait: EMPATHY                                       │   │
│ │ trait_weight: 0.3                                            │   │
│ │ npc_name: "Nima"                                             │   │
│ │ scene_name: "First Meeting"                                  │   │
│ └──────────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TRAIT_SYSTEM.py: TraitProfiler.record_choice()                      │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ 1. Update empathy: 50.0 + (0.3 * 10) = 53.0                │   │
│ │ 2. Add to recent_choices deque (max 10 items)              │   │
│ │ 3. Update coherence based on pattern consistency           │   │
│ └──────────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ COHERENCE_CALCULATOR.py: get_coherence_report()                    │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Recent choices: [EMPATHY, EMPATHY, SKEPTICISM]              │   │
│ │ Pattern analysis:                                             │   │
│ │   - Empathy count: 0.6                                       │   │
│ │   - Skepticism count: 0.3                                    │   │
│ │   - Total: 1.0                                               │   │
│ │ Coherence = 0.6 / 1.0 = 60% = 60 points = "MIXED"         │   │
│ │                                                              │   │
│ │ Report:                                                       │   │
│ │   - overall_coherence: 60.0                                  │   │
│ │   - npc_trust_level: "moderate"                              │   │
│ │   - dialogue_depth: "social"                                 │   │
│ │   - primary_pattern: EMPATHY                                 │   │
│ └──────────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ NPC_RESPONSE_ENGINE.py: get_npc_response()                          │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Nima profile: EMPATHETIC personality                         │   │
│ │   - prefers_traits: [EMPATHY, INTEGRATION]                   │   │
│ │   - uncomfortable_traits: []                                  │   │
│ │                                                              │   │
│ │ Player's primary trait: EMPATHY                              │   │
│ │ Trait comfort: 0.9 (Nima loves empathy)                      │   │
│ │ Coherence: 60 = dialogue_depth: "social"                     │   │
│ │ Conflict level: "ally" (shares EMPATHY)                      │   │
│ └──────────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ DIALOGUE ENGINE (FirstPerson orchestrator)                           │
│ Uses NPC response parameters to generate dialogue:                   │
│   - Trait comfort: 0.9 (high alignment)                              │
│   - Coherence: 60 (moderate)                                         │
│   - Dialogue depth: "social" (shares moderate context)              │
│   - Conflict: "ally" (supports player)                               │
│                                                                      │
│ Example response: "I hear you, and I appreciate your concern."       │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STREAMLIT UI                                                         │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ TRAIT METERS:                           COHERENCE:           │   │
│ │ Empathy:     ███░░░░░░ 60%    MIXED (60/100)                │   │
│ │ Skepticism:  █░░░░░░░░  10%    NPC TRUST: moderate          │   │
│ │ Integration: █░░░░░░░░  10%    DIALOGUE: social             │   │
│ │ Awareness:   █░░░░░░░░  10%                                  │   │
│ │                                                              │   │
│ │ Nima perceives you as: Empathetic Ally                       │   │
│ └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
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
Saori           Neutral    Neutral      ★★★★★      ★★★★★
(Integrator)

Ravi            ✗ ✗ ✗     ★★★★★       Neutral     ★★★★★
(Skeptical)

Nima            ★★★★★      ✗ ✗        ★★★★        Neutral
(Empathetic)

Malrik          ✗ ✗ ✗     ★★★★★       Neutral     ★★★★
(Skeptic)

Elenya          ★★★★★      Neutral     ★★★★★       Neutral
(Empathetic)

Coren           Neutral    Neutral     ★★★★        ★★★★★
(Aware)

Legend:
★★★★★ = "ally" (trust increases, dialogue deepens)
★★★★ = "neutral" (baseline interaction)
✗ ✗ ✗ = "opposed" (high coherence needed to overcome suspicion)
```

---

## Coherence Level Thresholds

```
95    ╔════════════════════════════════════════╗
      ║   CRYSTAL_CLEAR                        ║
      ║   "Perfectly consistent"               ║
      ║   - NPC trust: high                    ║
      ║   - Dialogue: intimate                 ║
80    ╠════════════════════════════════════════╣
      ║   CLEAR                                ║
      ║   "Mostly consistent"                  ║
      ║   - NPC trust: high                    ║
      ║   - Dialogue: personal                 ║
60    ╠════════════════════════════════════════╣
      ║   MIXED                                ║
      ║   "Holds multiple truths"              ║
      ║   - NPC trust: moderate                ║
      ║   - Dialogue: social                   ║
40    ╠════════════════════════════════════════╣
      ║   CONFUSED                             ║
      ║   "Contradictory patterns"             ║
      ║   - NPC trust: low                     ║
      ║   - Dialogue: guarded                  ║
20    ╠════════════════════════════════════════╣
      ║   CONTRADICTORY                        ║
      ║   "Wildly inconsistent"                ║
      ║   - NPC trust: suspicious              ║
      ║   - Dialogue: minimal                  ║
0     ╚════════════════════════════════════════╝
```

---

## Class Hierarchy

```
TraitSystem (trait_system.py)
├── TraitType (enum)
│   ├── EMPATHY
│   ├── SKEPTICISM
│   ├── INTEGRATION
│   └── AWARENESS
├── TraitChoice (dataclass)
│   ├── choice_id
│   ├── primary_trait
│   ├── secondary_trait (optional)
│   └── coherence_bonus
├── TraitProfile (dataclass)
│   ├── empathy: 0-100
│   ├── skepticism: 0-100
│   ├── integration: 0-100
│   ├── awareness: 0-100
│   ├── coherence: 0-100
│   └── recent_choices: deque[TraitChoice] (max 10)
└── TraitProfiler
    ├── record_choice(trait_choice)
    ├── get_primary_trait()
    ├── get_trait_pattern()
    ├── is_coherent()
    └── get_trait_summary()

CoherenceSystem (coherence_calculator.py)
├── CoherenceLevel (enum)
│   ├── CRYSTAL_CLEAR (95)
│   ├── CLEAR (80)
│   ├── MIXED (60)
│   ├── CONFUSED (40)
│   └── CONTRADICTORY (20)
├── CoherenceReport (dataclass)
│   ├── overall_coherence
│   ├── level
│   ├── primary_pattern
│   ├── npc_trust_level
│   └── dialogue_depth
└── CoherenceCalculator
    ├── calculate_coherence()
    ├── get_pattern_analysis()
    ├── get_coherence_report()
    └── would_be_coherent(next_choice)

NPCSystem (npc_response_engine.py)
├── NPCPersonalityType (enum)
│   ├── EMPATHETIC
│   ├── SKEPTICAL
│   ├── INTEGRATOR
│   └── AWARE
├── NPCDialogueProfile (dataclass)
│   ├── personality_type
│   ├── preferred_traits
│   └── uncomfortable_traits
└── NPCResponseEngine
    ├── get_npc_response(npc_name, prompt)
    ├── get_npc_reaction_to_choice(npc_name, trait)
    ├── should_npc_trust_player(npc_name)
    ├── get_npc_conflict_level(npc_name)
    └── get_npc_dialogue_depth(npc_name)
```

---

## Next: Phase 2 Integration Points

Phase 2 will connect these systems into the game loop:

```
orchestrator.py (main game loop)
  ├─ Create TraitProfiler on game start
  ├─ On each dialogue choice:
  │  ├─ Create TraitChoice
  │  ├─ Call profiler.record_choice()
  │  ├─ Call coherence_calculator.get_coherence_report()
  │  └─ Call npc_response_engine.get_npc_response()
  ├─ Pass parameters to FirstPerson dialogue generator
  └─ Update Streamlit UI display

streamlit UI (velinor_scenes_test.py)
  ├─ Show trait meters (4 bars, 0-100 each)
  ├─ Show coherence status (level + percentage)
  ├─ Show primary pattern with narrative description
  ├─ Show NPC perception for each NPC in scene
  └─ Show dialogue history with trait mapping

Scene implementation (marketplace_scene.py - Phase 2)
  ├─ Define dialogue choices as TraitChoice objects
  ├─ Modify branching based on coherence/pattern
  ├─ Lock certain paths for low-coherence players
  └─ Adjust NPC behavior based on perceived trait
```
