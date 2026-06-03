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
