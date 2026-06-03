# TheVillage Changelog

Last updated: 2026-06-02

## Purpose
This file is the chronological history for TheVillage behavioral, architectural, and interaction changes.

Use this log to track:
- what changed
- why it changed
- what user-facing behavior was affected
- what tests or validations were run

## Entry Template
### YYYY-MM-DD - Short Title
- Summary:
- Scope:
- User impact:
- Technical details:
- Validation:
- Follow-up:

---

## 2026-06-02 - Step 2: Election and Scoring Logic Implemented
- Summary: Implemented governance election flow with functional fitness scoring and ranked-choice runoff.
- Scope: `governance.py`, elections routing.
- User impact: Leader selection now reflects live system needs instead of static max-score selection.
- Technical details:
- Added `governance.compute_leadership_score(villager, context)` with weighted coherence, role strength, needs vector, emotional field, mission alignment, and reward trend.
- Added `governance.run_ranked_choice_election()` with majority detection and elimination rounds.
- Added `governance.needs_vector` update flow to rebalance candidate fitness based on village conditions.
- Validation: Governance and evolution mode tests passing.
- Follow-up: Continue tuning weights for long-horizon stabilization under prolonged crisis.

## 2026-06-02 - Step 3: Crisis and Revalidation Flows Wired
- Summary: Connected crisis leadership transfer and legitimacy revalidation to the new governance model.
- Scope: Mind orchestration, governance triggers, elections mode integration.
- User impact: Crisis transfer now selects interim leadership functionally, while legitimacy failure can trigger revalidation elections automatically.
- Technical details:
- Added crisis override path and non-counting crisis election handling.
- Added `governance.trigger_revalidation_if_needed()` checks for legitimacy drop, dispute, crisis escalation, and recovery shifts.
- Added dispute resolution timing telemetry hook.
- Validation: Crisis -> election -> revalidation paths covered by governance tests.
- Follow-up: Add UI surfacing for active revalidation state.

## 2026-06-02 - Step 4: HouseBrief Governance Override Applied
- Summary: Added governance-aware house brief override layer during leadership transition and crisis.
- Scope: `HouseBrief` model and villager crisis brief generation.
- User impact: House prompts now adapt during transitions with clearer governance-safe framing and transition-sensitive guidance.
- Technical details:
- Implemented `house_brief.apply_governance_override()`.
- Applied crisis transition context and legitimacy-aware downstream impacts.
- Preserved role-specific handoff/authority guidance while applying governance context.
- Validation: Model tests confirm crisis house briefs still include role-specific handoff semantics.
- Follow-up: Add richer per-role override variants for late-stage stabilization.

## 2026-06-02 - Step 5: Governance Telemetry Added
- Summary: Added governance telemetry tracking for leadership cadence, legitimacy, crisis load, and cohesion effects.
- Scope: Governance state synchronization and telemetry updates.
- User impact: Governance behavior is now auditable and measurable over time.
- Technical details:
- Added telemetry under `telemetry.governance.*` including term durations, consecutive terms, cooldowns, legitimacy history, crisis frequency, dispute resolution time, coherence impact, and internality growth indicators.
- Added synchronization between runtime governance metadata and persisted `governance` state fields.
- Validation: Governance regression tests verify telemetry presence and update behavior.
- Follow-up: Add chartable API output slices for telemetry consumers.

## 2026-06-02 - Step 6: Governance Regression Suite Added
- Summary: Added dedicated regression coverage for governance charter behavior.
- Scope: New test module and cross-mode validation.
- User impact: Reduced risk of silent regressions in term policy, crisis transfer, and legitimacy logic.
- Technical details:
- Added `TheVillage/tests/test_governance.py` covering term limits/cooldowns, crisis non-counting elections, revalidation triggers, needs-vector scoring response, non-adversarial crisis language, and crisis->election->stabilization loop.
- Validation: Test module executed in CI-style local run.
- Follow-up: Add parameterized tests for extended term sequences and edge-case cooldown rollover.

## 2026-06-02 - Step 7: Full Validation and Regression Fix
- Summary: Ran full TheVillage test suite, fixed one guidance-override regression, and revalidated.
- Scope: Full test suite plus targeted model patch.
- User impact: Ensures governance override does not erase role-specific handoff/authority guidance during crisis.
- Technical details:
- Initial full run found one failure in `test_model.py` leadership crisis guidance expectations.
- Patched `HouseBrief.apply_governance_override()` to keep existing transition-context guidance (handoff/authority/legitimacy/revalidation) and only apply generic override when missing.
- Final full suite result: all tests passing.
- Validation: `pytest TheVillage/tests -q` -> 39 passed.
- Follow-up: Keep this regression in place as a guard for future governance prompt refactors.

## 2026-06-02 - Humane Governance Charter Model (Terms, Ranked-Choice, Revalidation, Telemetry)
- Summary: Implemented a stable, development-oriented governance charter that rotates leadership functionally, enforces anti-stagnation limits, and handles crisis/dispute/revalidation without adversarial framing.
- Scope: Governance module, elections mode, core state model, mind orchestration, house-brief behavior, telemetry wiring, and regression coverage.
- User impact: Leadership now behaves as a temporary cognitive mode with explicit term cadence, eligibility gates, mission-fit revalidation, and calmer transition language during crisis.
- Technical details:
- Added governance term structure: 14-day terms, max 2 consecutive terms, and 2-term cooldown tracking.
- Added eligibility checks that reject cooldown, impairment, and over-limit candidates.
- Added scheduled elections at dawn cadence, with crisis interim transfer that does not increment term count and does not cancel scheduled elections.
- Added functional leadership scoring using coherence contribution, role strengths, needs weighting, emotional field state, reward trend, and mission alignment.
- Added dynamic `governance.needs_vector` to rebalance candidate fitness by current system pressures.
- Added ranked-choice election with instant runoff and Aura-aware modifier.
- Added dynamic legitimacy scoring and revalidation triggers tied to legitimacy drop, dispute cues, crisis escalation/recovery shifts.
- Added post-election stabilization to reduce contradiction pressure and smooth emotional volatility.
- Added house-level governance override integration and non-adversarial tone enforcement in crisis briefs.
- Added explicit governance telemetry under `telemetry.governance.*` (term durations, cooldowns, consecutive terms, legitimacy, crisis frequency, dispute resolution time, coherence impact, internality indicators).
- Validation:
- Governance regression suite added and passing.
- Crisis -> election -> stabilization loop validated.
- Term limits and cooldown behavior validated.
- Revalidation trigger behavior validated.
- Non-adversarial crisis brief language validated.
- Follow-up:
- Expose governance/telemetry slices as first-class API response sections for easier frontend inspection.
- Add dashboard views for legitimacy trajectory and dispute-resolution latency.

## 2026-06-01 - Canonical Role Baseline Established
- Summary: Documented the six canonical houses and their subsystem correlations.
- Scope: Documentation only.
- User impact: Provides a stable reference for narrative and product direction.
- Technical details: Added canonical baseline doc and cross-reference structure under TheVillage docs.
- Validation: Manual review.
- Follow-up: Keep role identity stable unless explicitly versioned.

## 2026-06-01 - HouseBrief Model Attached to Villagers
- Summary: Added HouseBrief state to each villager and persistence model.
- Scope: Core state model, villager initialization, API payload exposure.
- User impact: Houses now carry explicit goal/problem/guidance fields.
- Technical details: Added HouseBrief dataclass, attached to villager state, serialization/deserialization, and API inclusion.
- Validation: TheVillage test suite passing.
- Follow-up: Continue expanding per-house decision loop.

## 2026-06-01 - Global Clock, Day/Night, and Dream Mode
- Summary: Added hour-based progression with dream-hour behavior and waking-hour drift.
- Scope: Engine tick flow, scheduler hourly processing, villager dream behavior, model fields.
- User impact: Village now changes behavior by hour and supports night-time dream processing.
- Technical details: Added current_hour, tick_hour logic, dream-time guard, and once-per-night dream generation.
- Validation: Clock/dream tests added and passing.
- Follow-up: Expand symbolic recombination and dream interpretation quality.

## 2026-06-01 - Time-of-Day Color Schemes
- Summary: Added dynamic UI theming based on village hour.
- Scope: API color scheme provider and frontend variable application.
- User impact: Visual atmosphere now shifts across dawn/day/sunset/night.
- Technical details: Added color scheme payload and client-side CSS variable mapping.
- Validation: Manual UI behavior check and regression tests passing.
- Follow-up: Tune palettes after user playtesting.

## 2026-06-01 - House Choice Controls and Selection Persistence
- Summary: Added clickable four-choice controls per house and persisted selection to house_brief.selected_choice.
- Scope: Frontend detail panel controls and new API endpoint for choice submissions.
- User impact: Users can now guide each house through structured option selection.
- Technical details: Added /api/villager-choice endpoint and selected-state UI rendering.
- Validation: TheVillage test suite passing after integration.
- Follow-up: Add downstream impact preview and explicit choice-effect telemetry.

## 2026-06-02 - Crisis-to-Governance Adaptation Loop (Leadership, Dispute, Revalidation)
- Summary: Upgraded leadership crisis handling from passive logging into an adaptive governance loop that changes goals, authority, contradiction pressure, and house-level decisions in real time.
- Scope: Core orchestration engine, crisis arc progression, villager brief generation, mode routing behavior, and regression tests.
- User impact: Crisis language now causes immediate functional state shifts instead of narrative-only output. Users can now see live changes in executive leadership, crisis goals, dispute state, and role-specific decision options.
- Technical details:
- Crisis detection now triggers direct systemic effects when health-risk and leadership-transfer cues are present.
- Crisis protocol enters elections mode, raises tension/contradiction load, and activates high-priority goals including stabilize_leadership_transition and maintain_service_continuity.
- Crisis metadata is persisted in evolution_meta, including active_crisis, affected_villager, interim_leader, recovery_status, crisis_turn_started, and dispute flags.
- A turn-based crisis arc now advances automatically from acute disruption to improving recovery, then to potential dispute and eventual mediated settlement.
- Additional phrase-level parsing was added for interpersonal refusal dynamics, allowing live reports to escalate dispute conditions without waiting for timer-only transitions.
- When leadership dispute is active, negotiate_leadership_settlement is injected into the active goal set and contradiction pressure remains elevated until resolution.
- House briefs now apply a crisis-aware override layer that rewrites goal/problem/guidance/choices by role.
- Affected leader house (for example Tomas) receives recovery-and-handoff actions.
- Interim authority house (for example Edda) receives legitimacy-and-transition actions.
- If dispute is active, final action options switch to mediation-oriented pathways.
- Briefs are explicitly refreshed after interaction and cycle updates so UI state reflects governance shifts immediately.
- Validation:
- Live browser interaction confirmed real-time transformation of house goals and options after leadership crisis and dispute phrases.
- Regression tests expanded and passing, including crisis impact assertions and dispute escalation behavior.
- Follow-up:
- Add richer mediator-state modeling (trust repair score, legitimacy confidence, settlement durability).
- Add explicit telemetry for which house options are chosen during crisis and how those choices affect resolution speed.

## 2026-06-02 - Election Legitimacy Doubt and Candidate Revalidation Path
- Summary: Added a second-order adaptation path for election legitimacy doubts, enabling candidate re-evaluation against mission-level criteria during active crisis.
- Scope: Leadership dispute parser, goal prioritization, evolution metadata, and crisis brief decision layer.
- User impact: Inputs such as election doubt or candidate challenge now open a structured revalidation workflow instead of remaining implicit narrative tension.
- Technical details:
- New election-doubt markers trigger leadership_revalidation mode in evolution metadata.
- Candidate mentions (Edda, Sable, Lio, Jun, Mira, Tomas) are extracted into candidate_review_list for downstream guidance framing.
- Two mission-critical goals are added at high priority: revalidate_leadership_mandate and compare_leadership_candidates.
- Disputing actor attribution was improved to use refusal-phrase proximity, correctly identifying statements such as "Edda does not want to give up leadership" as Edda-driven dispute.
- Crisis brief language now explicitly frames leadership fitness against coherence and self-understanding outcomes.
- Dispute-plus-revalidation state now offers a combined action: mediated settlement plus time-bounded revalidation election.
- Validation:
- New regression test added for the exact phrasing pattern involving Tomas recovery, Edda refusal, and election-doubt dynamics.
- Model tests passing (29 total) after integration.
- Live state payload verified: leadership_dispute=true, leadership_revalidation=true, disputing_actor=Edda, candidate list populated, and revalidation goals active.
- Follow-up:
- Tune ElectionsMode scoring weights for crisis-specific leader fitness dimensions (continuity, dynamic adaptation, care throughput, and narrative coherence).

## 2026-06-02 - Mission Statement Alignment to Emergent Internality
- Summary: Updated the default mission statement to explicitly encode coherence preservation plus self-understanding growth.
- Scope: Core mission model default text.
- User impact: The system's top-line purpose now matches actual behavioral incentives and visible leadership review framing.
- Technical details: Main mission default now reads as maintaining coherence while increasing capacity for self-understanding, explicitly naming emergent internality intent.
- Validation: Regression suite passing after update.
- Follow-up: Add mission decomposition metrics so each active goal can be scored against coherence and internality contribution separately.
