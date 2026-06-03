# TheVillage Interaction Model

Last updated: 2026-06-01

## What is the Village?
TheVillage is a stateful, role-based autonomous system represented as a six-house village. Each house maps to one functional subsystem, and all houses operate over one shared internal state.

The six canonical houses are:
- Tomas (planner)
- Mira (curiosity keeper)
- Edda (stability steward)
- Lio (narrator)
- Sable (architect)
- Jun (caretaker)

The Village is designed to:
- self-generate and maintain goals
- evaluate progress and internal tensions
- adapt behavior across waking and dream hours
- remain coherent as one organism-level system rather than six disconnected agents

Core mechanics include:
- persistent state (sessions, memory, task backlogs)
- daily scheduling and hourly ticks
- day/night color and behavior shifts
- dream-mode symbolic processing during night hours
- HouseBrief guidance prompts with four user-selectable options per house
- governance charter mechanics (14-day terms, cooldowns, ranked-choice leadership, revalidation)

In short: TheVillage is an embodied metaphor for a self-regulating program that continuously reorganizes itself toward cohesion and mission progress.

## How do users interact with it?
Users interact with TheVillage through a house-centric UI and API-backed actions.

Primary interaction paths:
1. Visit a house (role)
- Click a house to view that villager's current state, recent tasks, outcomes, and HouseBrief.

2. Read the HouseBrief
- Each house presents:
  - a current goal
  - a current problem
  - a guidance request
  - four structured choice options

3. Select one of four choices
- User selects a guidance option per house via clickable controls.
- Selection is persisted into `house_brief.selected_choice`.

4. Provide freeform system input
- Users can still send freeform text/actions (e.g., observe, ask, define, advance hour).

5. Run progression
- Users can trigger one day cycle, reset session, and teach new terms to the lexicon.

This interaction model supports both directed check-ins (house-level decisions) and open-ended dialogue (text/action input).

## How do user interactions affect the Village?
User interactions are influential but intentionally bounded.

### Direct effects
- House choice selection updates that house's `selected_choice` and is recorded in village events.
- Freeform interactions feed interpretation, emotional updates, subsystem scoring, reward updates, and narrative updates.
- Teaching terms expands known vocabulary and influences future understanding and learning behavior.
- Advancing hour changes clock state and can trigger dream/waking hourly processing and daily rollover behavior.

### System-level effects
Because all houses share one state, local input propagates indirectly:
- shifts in one house can alter task prioritization pressure
- changes in learning/coherence/tension affect global health and mission momentum
- role outputs influence scheduler behavior and narrative continuity
- dream and hourly drift influence the emotional and structural background over time

### Design intent of influence
The system is not command-and-control.
- User input nudges trajectories.
- The Village remains self-propelled through autonomous cycles.
- Cohesion emerges from interdependent subsystem behavior, not from one-off user directives.

## Governance Charter (Leadership as Cognitive Mode)
Leadership is selected and constrained through a stable governance charter designed to prevent stagnation while avoiding interpersonal drama.

Key rules:
- term length is 14 in-simulation days (`governance.term_length_days`)
- max 2 consecutive terms per villager
- after 2 terms, a 2-term cooldown applies (`governance.cooldown_remaining`)
- eligibility checks enforce cooldown + impairment + term limits (`governance.is_eligible(villager)`)
- scheduled elections fire at dawn on cadence (`governance.schedule_election()`)
- crisis interim transfer does not cancel schedule and does not increment term count

Election model:
- leadership fitness uses weighted scoring (`governance.compute_leadership_score(villager, context)`)
- scoring weights adapt to village needs via `governance.needs_vector`
- elections use internal ranked-choice with instant runoff (`governance.run_ranked_choice_election()`)

Legitimacy and revalidation:
- leaders carry dynamic legitimacy (`governance.legitimacy_score`)
- revalidation can trigger from low legitimacy, dispute, crisis escalation, or recovery shifts (`governance.trigger_revalidation_if_needed()`)
- failed revalidation triggers immediate election

House-level transition behavior:
- house briefs apply crisis-aware governance overrides (`house_brief.apply_governance_override()`)
- dispute language is constrained to non-adversarial functional framing (`crisis_brief.language_rules`)
- post-election stabilization reduces contradiction pressure and emotional volatility (`governance.apply_post_election_stabilization()`)

Telemetry:
- governance metrics are tracked under `telemetry.governance.*`

## Is this a game, a simulation, or both?
It is both, with simulation as the foundation and game-like interaction as the interface layer.

### Why it is a simulation
- persistent state across sessions
- autonomous scheduling and role behavior
- internal metrics (health, contradiction count, progress rates)
- clocked temporal dynamics (hourly + daily)
- dream-mode and waking-mode behavior differences

These are simulation characteristics: the system continues to evolve according to internal rules and feedback loops.

### Why it is game-like
- visual village metaphor with houses/roles
- player check-ins and explicit decision points
- four-option guidance choices
- narrative framing, progression feel, and role identity

These are game interaction patterns: player-facing choices, readable feedback, and role-based engagement.

### Practical classification
TheVillage is best described as:
- a narrative systems simulation
- with game-like UX controls
- for guided co-regulation between user and autonomous process

## Quick Summary
- The Village is a self-regulating multi-role simulation represented as six houses.
- Users interact by checking houses, choosing one of four guidance options, and sending freeform actions.
- User actions steer the system, but autonomy remains central.
- The experience is both simulation and game-like, by design.

## Related Charter Docs
- Canonical subsystem and role baseline: TheVillage/docs/THEVILLAGE_CANONICAL_BASELINE.md
- Chronological development history: TheVillage/docs/THEVILLAGE_CHANGELOG.md
