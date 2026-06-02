# TheVillage Canonical Baseline

Last updated: 2026-06-01

## Purpose
This document tracks the canonical identity and function of each village house so future narrative and system changes stay consistent.

This file is the starting index for a larger Village Charter: the durable reference set for role definitions, interaction rules, and narrative continuity.

## Village Charter Cross-References
- Interaction model and user-facing behavior: TheVillage/docs/THEVILLAGE_INTERACTION_MODEL.md
- Canonical role and subsystem baseline (this file): TheVillage/docs/THEVILLAGE_CANONICAL_BASELINE.md
- Chronological history of system evolution: TheVillage/docs/THEVILLAGE_CHANGELOG.md

## Canonical Six Houses

1. Tomas - planner
2. Mira - curiosity keeper
3. Edda - stability steward
4. Lio - narrator
5. Sable - architect
6. Jun - caretaker

Source of truth for names and roles:
- TheVillage/core/villagers.py

## System Correlation by House

### Tomas (planner)
- Domain: Mission decomposition and execution sequencing
- Function: Turns high-level mission pressure into concrete daily steps and ordering decisions
- Typical effect: Increases clarity of next actions and improves goal progress momentum

### Mira (curiosity keeper)
- Domain: Vocabulary expansion and conceptual discovery
- Function: Surfaces unknown terms, seeks definitions, and expands shared understanding
- Typical effect: Improves interpretive richness and reduces semantic blind spots

### Edda (stability steward)
- Domain: Contradiction repair and coherence control
- Function: Detects and resolves tensions across subsystem signals and world-model consistency
- Typical effect: Lowers contradiction load and protects global coherence

### Lio (narrator)
- Domain: Continuity and legibility
- Function: Weaves events, tasks, and outcomes into coherent story-level memory
- Typical effect: Preserves continuity across turns, days, and state transitions

### Sable (architect)
- Domain: Structural tuning and long-horizon design
- Function: Rebalances internal structure and reward emphasis to avoid short-term overfitting
- Typical effect: Improves long-term alignment and systemic durability

### Jun (caretaker)
- Domain: Recovery, resilience, and health maintenance
- Function: Monitors stress and error pressure, triggers repair/recovery behavior
- Typical effect: Stabilizes tension and protects village health under load

## Shared-State Principle
These six are not isolated agents. They are interdependent governance lenses over one shared organism-state.

Implications:
- House actions influence other houses through shared health, goals, tensions, and environment state
- User guidance should be subtle and bounded, not direct command/control
- Cohesion is an emergent village-level outcome

## Canonical Implementation Anchors
- Role definitions and per-role logic: TheVillage/core/villagers.py
- Daily scheduling and task execution: TheVillage/core/scheduler.py
- Orchestration, goals, reward, and narrative updates: TheVillage/core/mind.py
- Core state model and persisted fields: TheVillage/core/models.py
- UI and API surface: TheVillage/interface/api.py

## Current Narrative-Alignment Notes
- HouseBrief model is attached to each villager state and exposed via API payload
- Briefs are refreshed from live state during scheduling so role goals/problems stay context-aware
- Global clock, dream window, and hourly behavior now coexist with house briefing

## Change Log
- 2026-06-01: Created canonical baseline and role-to-system mapping
