# TheVillage Changelog

Last updated: 2026-06-01

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
