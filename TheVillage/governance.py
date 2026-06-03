"""Governance helpers for executive leadership transitions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from TheVillage.core.models import InternalState, clamp_01


ADVERSARIAL_TERMS = {
    "sabotage": "destabilize",
    "manipulate": "over-influence",
    "attack": "pressure",
    "undermine": "weaken",
    "hostility": "strain",
    "resentment": "concern",
}


def _telemetry_bucket(state: InternalState) -> dict[str, Any]:
    telemetry = cast(dict[str, Any], state.evolution_meta.get("telemetry"))
    if not isinstance(telemetry, dict):
        telemetry = {}
        state.evolution_meta["telemetry"] = telemetry
    governance_bucket = cast(dict[str, Any], telemetry.get("governance"))
    if not isinstance(governance_bucket, dict):
        governance_bucket = {}
        telemetry["governance"] = governance_bucket
    governance_bucket.setdefault("term_durations", [])
    governance_bucket.setdefault("consecutive_terms", {})
    governance_bucket.setdefault("cooldowns", {})
    governance_bucket.setdefault("legitimacy_score", 0.74)
    governance_bucket.setdefault("legitimacy_score_history", [])
    governance_bucket.setdefault("crisis_frequency", 0)
    governance_bucket.setdefault("dispute_resolution_time", [])
    governance_bucket.setdefault("coherence_impact", [])
    governance_bucket.setdefault("internality_growth_indicators", [])
    governance_bucket.setdefault("election_count", 0)
    governance_bucket.setdefault("revalidation_count", 0)
    return governance_bucket


def _sync_governance_dataclass(state: InternalState, governance: dict[str, Any]) -> None:
    state.governance.term_length_days = int(governance.get("term_length_days", state.governance.term_length_days))
    state.governance.max_consecutive_terms = int(
        governance.get("consecutive_term_limit", state.governance.max_consecutive_terms)
    )
    state.governance.cooldown_terms_after_limit = int(
        governance.get("cooldown_terms", state.governance.cooldown_terms_after_limit)
    )
    state.governance.current_term_started_day = int(
        governance.get("term_started_day", state.governance.current_term_started_day)
    )
    state.governance.next_scheduled_election_day = int(
        governance.get("next_scheduled_election_day", state.governance.next_scheduled_election_day)
    )
    state.governance.consecutive_terms_served = {
        str(key): int(value)
        for key, value in cast(dict[str, Any], governance.get("consecutive_terms_served", {})).items()
    }
    state.governance.cooldown_remaining = {
        str(key): int(value)
        for key, value in cast(dict[str, Any], governance.get("cooldown_remaining", {})).items()
    }
    state.governance.crisis_override_active = bool(governance.get("crisis_override_active", False))
    state.governance.crisis_election_does_not_increment_term_count = bool(
        governance.get("crisis_election_does_not_increment_term_count", True)
    )
    state.governance.needs_vector = {
        str(key): float(value)
        for key, value in cast(dict[str, Any], governance.get("needs_vector", {})).items()
    }
    state.governance.legitimacy_score = float(governance.get("legitimacy_score", state.governance.legitimacy_score))
    state.governance.mission_alignment_score = float(
        governance.get("mission_alignment_score", state.governance.mission_alignment_score)
    )
    state.governance.legitimacy_threshold = float(
        governance.get("revalidation_threshold", state.governance.legitimacy_threshold)
    )
    state.governance.pending_revalidation = bool(governance.get("revalidation_pending", False))
    state.governance.last_election_day = int(governance.get("last_election_day", state.governance.last_election_day))
    state.governance.last_election_kind = str(
        governance.get("last_election_type", state.governance.last_election_kind)
    )

    state.telemetry["governance"] = dict(_telemetry_bucket(state))


def get_governance(state: InternalState) -> dict[str, Any]:
    governance = cast(dict[str, Any], state.evolution_meta.get("governance"))
    if not isinstance(governance, dict):
        governance = {}
        state.evolution_meta["governance"] = governance
    governance.setdefault("term_length_days", state.governance.term_length_days or 14)
    governance.setdefault("consecutive_term_limit", state.governance.max_consecutive_terms or 2)
    governance.setdefault("cooldown_terms", state.governance.cooldown_terms_after_limit or 2)
    governance.setdefault("consecutive_terms_served", {})
    governance.setdefault("cooldown_remaining", {})
    governance.setdefault("term_started_day", state.governance.current_term_started_day or state.current_day)
    governance.setdefault(
        "next_scheduled_election_day",
        state.governance.next_scheduled_election_day or (state.current_day + int(governance["term_length_days"])),
    )
    governance.setdefault("last_scheduled_election_day", 0)
    governance.setdefault("last_counted_election_day", 0)
    governance.setdefault("crisis_override_active", state.governance.crisis_override_active)
    governance.setdefault(
        "crisis_election_does_not_increment_term_count",
        state.governance.crisis_election_does_not_increment_term_count,
    )
    governance.setdefault(
        "needs_vector",
        {
            "Tomas": 1.0,
            "Mira": 1.0,
            "Edda": 1.0,
            "Lio": 1.0,
            "Sable": 1.0,
            "Jun": 1.0,
        },
    )
    governance.setdefault("legitimacy_score", state.governance.legitimacy_score)
    governance.setdefault("mission_alignment_score", state.governance.mission_alignment_score)
    governance.setdefault("revalidation_threshold", state.governance.legitimacy_threshold)
    governance.setdefault("revalidation_pending", state.governance.pending_revalidation)
    governance.setdefault("scheduled_election_pending", False)
    governance.setdefault("crisis_brief", {
        "language_rules": [
            "Use concern, uncertainty, preference, and functional reasoning.",
            "Avoid blame, hostility, manipulation, and adversarial framing.",
            "Frame disputes as mission-fit and mode-fit checks.",
        ]
    })
    _sync_governance_dataclass(state, governance)
    return governance


def get_leader(state: InternalState) -> str:
    return (state.executive_function or "Tomas").strip() or "Tomas"


def set_leader(state: InternalState, leader: str, reason: str | None = None) -> None:
    selected = (leader or "Tomas").strip() or "Tomas"
    previous = get_leader(state)
    state.executive_function = selected
    if previous != selected:
        note = f"Leadership shifted from {previous} to {selected}."
        if reason:
            note = f"{note} Reason: {reason}"
        state.recent_events.append(note)
        state.recent_events = state.recent_events[-20:]


def choose_leader(candidate_scores: Mapping[str, float]) -> str:
    if not candidate_scores:
        return "Tomas"
    return max(candidate_scores.items(), key=lambda item: item[1])[0]


def enforce_tone_constraints(text: str) -> str:
    normalized = text
    lowered = normalized.lower()
    for blocked, replacement in ADVERSARIAL_TERMS.items():
        if blocked in lowered:
            normalized = normalized.replace(blocked, replacement)
            normalized = normalized.replace(blocked.capitalize(), replacement.capitalize())
    return normalized


def _is_impaired(state: InternalState, villager: str) -> bool:
    villager_state = state.villager_states.get(villager)
    if villager_state is not None and str(villager_state.mood).lower() in {"ill", "impaired", "critical"}:
        return True
    if str(state.evolution_meta.get("active_crisis") or "") == "leadership":
        affected = str(state.evolution_meta.get("affected_villager") or "")
        recovery = str(state.evolution_meta.get("recovery_status") or "acute")
        if villager == affected and recovery != "recovered":
            return True
    return False


def is_eligible(state: InternalState, villager: str) -> bool:
    governance = get_governance(state)
    cooldowns = governance["cooldown_remaining"] if isinstance(governance["cooldown_remaining"], dict) else {}
    consecutive = governance["consecutive_terms_served"] if isinstance(governance["consecutive_terms_served"], dict) else {}
    term_limit = int(governance.get("consecutive_term_limit", 2))
    cooldown_remaining = int(cooldowns.get(villager, 0))
    consecutive_terms = int(consecutive.get(villager, 0))
    if cooldown_remaining > 0:
        return False
    if _is_impaired(state, villager):
        return False
    if consecutive_terms >= term_limit:
        return False
    return True


def _role_need_boost(role: str, villager: str, state: InternalState) -> float:
    role_name = role.lower()
    coherence = float(state.environment.coherence)
    rumination = float(state.background_processes.get("rumination", 0.0))
    strain = float(state.bodily_state.get("tension", 0.0)) + float(state.emotional_state.get("social_threat", 0.0))
    structural = float(state.health_metrics.stalled_goals) * 0.15 + float(state.health_metrics.contradiction_count) * 0.08
    boost = 0.0
    if coherence < 0.55 and villager in {"Tomas", "Edda"}:
        boost += (0.55 - coherence) * 0.65
    if rumination > 0.35 and villager == "Mira":
        boost += (rumination - 0.35) * 0.5
    if float(state.health_metrics.contradiction_count) > 1 and villager == "Lio":
        boost += 0.08
    if strain > 0.6 and villager == "Jun":
        boost += min(0.18, (strain - 0.6) * 0.45)
    if structural > 0.25 and villager == "Sable":
        boost += min(0.17, structural * 0.3)
    if "planner" in role_name and coherence < 0.6:
        boost += 0.03
    if "stability" in role_name and float(state.health_metrics.contradiction_count) > 0:
        boost += 0.03
    return boost


def refresh_needs_vector(state: InternalState) -> dict[str, float]:
    governance = get_governance(state)
    vector = {
        "Tomas": 1.0,
        "Mira": 1.0,
        "Edda": 1.0,
        "Lio": 1.0,
        "Sable": 1.0,
        "Jun": 1.0,
    }
    coherence = float(state.environment.coherence)
    if coherence < 0.58:
        vector["Tomas"] += (0.58 - coherence) * 0.9
        vector["Edda"] += (0.58 - coherence) * 0.9
    drift = float(state.background_processes.get("rumination", 0.0)) + max(0.0, 0.5 - float(state.self_model.get("coherence", 0.5)))
    if drift > 0.45:
        vector["Mira"] += min(0.7, (drift - 0.45) * 1.2)
    confusion = float(state.health_metrics.contradiction_count) * 0.15 + max(0.0, 0.45 - coherence)
    if confusion > 0.2:
        vector["Lio"] += min(0.55, confusion)
    strain = float(state.bodily_state.get("tension", 0.0)) + float(state.emotional_state.get("social_threat", 0.0))
    if strain > 0.62:
        vector["Jun"] += min(0.7, (strain - 0.62) * 0.9)
    structural = float(state.health_metrics.stalled_goals) * 0.22 + float(state.health_metrics.contradiction_count) * 0.1
    if structural > 0.28:
        vector["Sable"] += min(0.6, structural)

    governance["needs_vector"] = {name: round(value, 3) for name, value in vector.items()}
    _sync_governance_dataclass(state, governance)
    return governance["needs_vector"]


def compute_leadership_score(villager: str, context: Mapping[str, object]) -> float:
    state = context.get("state")
    if not isinstance(state, InternalState):
        return 0.0
    governance = get_governance(state)
    raw_needs_vector = governance.get("needs_vector")
    needs_vector = cast(dict[str, Any], raw_needs_vector) if isinstance(raw_needs_vector, dict) else {}
    villager_state = state.villager_states.get(villager)
    role = villager_state.role if villager_state is not None else ""
    reward_trend = float(villager_state.reward_trend) if villager_state is not None else 0.0
    coherence_contribution = clamp_01(float(state.self_model.get("coherence", 0.5)) * 0.7 + float(state.environment.coherence) * 0.3)
    role_strength = 0.5 + _role_need_boost(role, villager, state)
    current_need = float(needs_vector.get(villager, 1.0))
    emotional_field = 1.0 - clamp_01(float(state.bodily_state.get("tension", 0.0)) * 0.5 + float(state.emotional_state.get("social_threat", 0.0)) * 0.5)
    mission_alignment = compute_mission_alignment_score(state, villager)
    score = (
        coherence_contribution * 0.25
        + role_strength * 0.2
        + current_need * 0.2
        + emotional_field * 0.12
        + mission_alignment * 0.15
        + (0.5 + reward_trend * 0.5) * 0.08
    )
    return round(score, 4)


def compute_mission_alignment_score(state: InternalState, villager: str) -> float:
    villager_state = state.villager_states.get(villager)
    role = (villager_state.role if villager_state is not None else "").lower()
    coherence = clamp_01(float(state.environment.coherence) * 0.55 + float(state.self_model.get("coherence", 0.5)) * 0.45)
    internality = clamp_01(float(state.self_model.get("continuity", 0.0)) * 0.4 + float(state.self_model.get("curiosity", 0.3)) * 0.6)
    role_fit = 0.5
    if "planner" in role:
        role_fit = 0.62
    elif "curiosity" in role:
        role_fit = 0.58
    elif "stability" in role:
        role_fit = 0.64
    elif "narrator" in role:
        role_fit = 0.57
    elif "architect" in role:
        role_fit = 0.61
    elif "caretaker" in role:
        role_fit = 0.59
    mission_alignment = clamp_01(coherence * 0.55 + internality * 0.3 + role_fit * 0.15)
    governance = get_governance(state)
    governance["mission_alignment_score"] = round(mission_alignment, 3)
    return mission_alignment


def _aura_modifier(state: InternalState, candidate: str) -> float:
    arc_theme = str(state.aura_arc_theme or "").lower()
    tension = float(state.aura_tension or 0.0)
    modifier = 0.0
    if arc_theme == "warning" and candidate in {"Edda", "Tomas"}:
        modifier += 0.04
    if arc_theme in {"search", "growth"} and candidate in {"Mira", "Sable"}:
        modifier += 0.04
    if arc_theme == "alignment" and candidate in {"Lio", "Jun"}:
        modifier += 0.04
    modifier += min(0.03, tension * 0.02 if candidate == "Jun" else 0.0)
    return modifier


def run_ranked_choice_election(
    state: InternalState,
    context: Mapping[str, object],
) -> tuple[str, dict[str, object]]:
    candidate_scores = context.get("candidate_scores")
    if not isinstance(candidate_scores, dict) or not candidate_scores:
        return "Tomas", {"rounds": []}
    voters = list(state.villager_states.keys())
    active_candidates = list(candidate_scores.keys())
    rounds: list[dict[str, object]] = []

    while len(active_candidates) > 1:
        ballots: dict[str, int] = {candidate: 0 for candidate in active_candidates}
        for voter in voters:
            voter_state = state.villager_states.get(voter)
            voter_role = (voter_state.role if voter_state is not None else "").lower()
            ranked = sorted(
                active_candidates,
                key=lambda candidate: (
                    float(candidate_scores.get(candidate, 0.0))
                    + _aura_modifier(state, candidate)
                    + (0.02 if voter == candidate else 0.0)
                    + (0.015 if voter_role and voter_role.split()[0] in candidate.lower() else 0.0)
                ),
                reverse=True,
            )
            ballots[ranked[0]] += 1

        total_votes = max(1, len(voters))
        winner = max(ballots.items(), key=lambda item: item[1])[0]
        if ballots[winner] > total_votes / 2:
            rounds.append({"active": list(active_candidates), "ballots": dict(ballots), "winner": winner})
            return winner, {"rounds": rounds}

        loser = min(ballots.items(), key=lambda item: item[1])[0]
        rounds.append({"active": list(active_candidates), "ballots": dict(ballots), "eliminated": loser})
        active_candidates = [candidate for candidate in active_candidates if candidate != loser]

    return active_candidates[0], {"rounds": rounds}


def _step_cooldowns(governance: dict[str, object], candidates: list[str]) -> None:
    cooldowns = governance["cooldown_remaining"] if isinstance(governance["cooldown_remaining"], dict) else {}
    for candidate in candidates:
        remaining = int(cooldowns.get(candidate, 0))
        if remaining > 0:
            cooldowns[candidate] = remaining - 1


def _update_term_state(state: InternalState, winner: str, previous: str) -> None:
    governance = get_governance(state)
    term_length = int(governance.get("term_length_days", 14))
    limit = int(governance.get("consecutive_term_limit", 2))
    cooldown_terms = int(governance.get("cooldown_terms", 2))
    consecutive = governance["consecutive_terms_served"] if isinstance(governance["consecutive_terms_served"], dict) else {}
    cooldowns = governance["cooldown_remaining"] if isinstance(governance["cooldown_remaining"], dict) else {}

    _step_cooldowns(governance, list(state.villager_states.keys()))

    previous_streak = int(consecutive.get(previous, 0))
    if previous != winner:
        if previous_streak >= limit:
            cooldowns[previous] = cooldown_terms
        consecutive[previous] = 0

    next_streak = 1 if winner != previous else int(consecutive.get(winner, 0)) + 1
    consecutive[winner] = next_streak
    governance["term_started_day"] = state.current_day
    governance["next_scheduled_election_day"] = state.current_day + term_length
    governance["last_counted_election_day"] = state.current_day

    telemetry = _telemetry_bucket(state)
    telemetry["consecutive_terms"] = dict(consecutive)
    telemetry["cooldowns"] = dict(cooldowns)


def _record_governance_telemetry(state: InternalState, winner: str, changed: bool, election_type: str) -> None:
    governance = get_governance(state)
    telemetry = _telemetry_bucket(state)
    telemetry["election_count"] = int(telemetry.get("election_count", 0)) + 1
    if election_type == "revalidation":
        telemetry["revalidation_count"] = int(telemetry.get("revalidation_count", 0)) + 1
    if election_type == "crisis":
        telemetry["crisis_frequency"] = int(telemetry.get("crisis_frequency", 0)) + 1

    legitimacy_history = telemetry.get("legitimacy_score_history")
    if not isinstance(legitimacy_history, list):
        legitimacy_history = []
        telemetry["legitimacy_score_history"] = legitimacy_history
    legitimacy_history.append(round(float(governance.get("legitimacy_score", 0.74)), 3))
    telemetry["legitimacy_score"] = round(float(governance.get("legitimacy_score", 0.74)), 3)
    legitimacy_history[:] = legitimacy_history[-80:]

    coherence_impact = telemetry.get("coherence_impact")
    if not isinstance(coherence_impact, list):
        coherence_impact = []
        telemetry["coherence_impact"] = coherence_impact
    coherence_impact.append({"day": state.current_day, "leader": winner, "coherence": round(float(state.environment.coherence), 3)})
    coherence_impact[:] = coherence_impact[-80:]

    internality = telemetry.get("internality_growth_indicators")
    if not isinstance(internality, list):
        internality = []
        telemetry["internality_growth_indicators"] = internality
    internality.append({
        "day": state.current_day,
        "continuity": round(float(state.self_model.get("continuity", 0.0)), 3),
        "curiosity": round(float(state.self_model.get("curiosity", 0.0)), 3),
    })
    internality[:] = internality[-80:]

    if changed:
        state.recent_events.append(f"Governance telemetry: leadership rotated via {election_type} election.")
        state.recent_events = state.recent_events[-20:]


def schedule_election(state: InternalState) -> bool:
    governance = get_governance(state)
    due_day = int(governance.get("next_scheduled_election_day", state.current_day + 14))
    last_day = int(governance.get("last_scheduled_election_day", 0))
    is_dawn = state.current_hour == 8
    should_schedule = is_dawn and state.current_day >= due_day and state.current_day != last_day
    governance["scheduled_election_pending"] = bool(should_schedule)
    return bool(should_schedule)


def trigger_revalidation_if_needed(state: InternalState) -> bool:
    governance = get_governance(state)
    threshold = float(governance.get("revalidation_threshold", 0.46))
    legitimacy = float(governance.get("legitimacy_score", 0.74))
    active_crisis = str(state.evolution_meta.get("active_crisis") or "") == "leadership"
    dispute = bool(state.evolution_meta.get("leadership_dispute"))
    explicit_revalidation = bool(state.evolution_meta.get("leadership_revalidation"))
    recovery_shift = str(state.evolution_meta.get("recovery_status") or "") == "recovered"
    should_revalidate = legitimacy < threshold or dispute or explicit_revalidation or (active_crisis and recovery_shift)
    governance["revalidation_pending"] = bool(should_revalidate)
    _sync_governance_dataclass(state, governance)
    return bool(should_revalidate)


def apply_post_election_stabilization(state: InternalState) -> None:
    state.health_metrics.contradiction_count = max(0, int(state.health_metrics.contradiction_count) - 1)
    state.bodily_state["tension"] = clamp_01(float(state.bodily_state.get("tension", 0.2)) - 0.08)
    state.emotional_state["arousal"] = clamp_01(float(state.emotional_state.get("arousal", 0.2)) - 0.06)
    state.environment.coherence = clamp_01(float(state.environment.coherence) + 0.05)
    state.recent_events.append("Post-election stabilization reduced contradiction pressure and smoothed emotional field.")
    state.recent_events = state.recent_events[-20:]


def update_legitimacy_score(state: InternalState) -> float:
    governance = get_governance(state)
    coherence = float(state.environment.coherence)
    contradictions = max(0.0, float(state.health_metrics.contradiction_count))
    strain = float(state.bodily_state.get("tension", 0.0))
    caretaker_signal = float(state.subsystem_scores.get("caretaker", 0.5))
    crisis_penalty = 0.1 if str(state.evolution_meta.get("active_crisis") or "") == "leadership" else 0.0
    legitimacy = clamp_01(coherence * 0.45 + (1.0 - min(1.0, contradictions * 0.2)) * 0.2 + (1.0 - strain) * 0.2 + caretaker_signal * 0.15 - crisis_penalty)
    governance["legitimacy_score"] = round(legitimacy, 3)
    _sync_governance_dataclass(state, governance)
    return legitimacy


def run_election(
    state: InternalState,
    villager_names: list[str],
    *,
    election_type: str,
    reason: str,
) -> dict[str, object]:
    governance = get_governance(state)
    refresh_needs_vector(state)
    update_legitimacy_score(state)

    eligible_candidates = [name for name in villager_names if is_eligible(state, name)]
    if not eligible_candidates:
        eligible_candidates = [name for name in villager_names if not _is_impaired(state, name)]
    if not eligible_candidates:
        eligible_candidates = list(villager_names)

    candidate_scores = {
        name: compute_leadership_score(name, {"state": state, "election_type": election_type})
        for name in eligible_candidates
    }
    winner, election_meta = run_ranked_choice_election(state, {"candidate_scores": candidate_scores})
    previous = get_leader(state)

    counted = not (
        election_type == "crisis"
        and bool(governance.get("crisis_election_does_not_increment_term_count", True))
    )

    set_leader(
        state,
        winner,
        reason=(
            f"{reason} Ranked-choice winner={winner}; "
            f"needs_vector={governance.get('needs_vector')}; candidate_scores={candidate_scores}"
        ),
    )

    if counted:
        duration = state.current_day - int(governance.get("term_started_day", state.current_day))
        telemetry = _telemetry_bucket(state)
        durations = telemetry.get("term_durations")
        if isinstance(durations, list):
            durations.append(max(0, int(duration)))
            durations[:] = durations[-80:]
        _update_term_state(state, winner, previous)
        governance["crisis_override_active"] = False
    else:
        governance["crisis_override_active"] = True
        governance["interim_leader"] = winner

    governance["scheduled_election_pending"] = False
    governance["revalidation_pending"] = False
    governance["last_election_type"] = election_type
    governance["last_election_day"] = state.current_day
    if election_type == "scheduled":
        governance["last_scheduled_election_day"] = state.current_day

    apply_post_election_stabilization(state)
    _record_governance_telemetry(state, winner, changed=winner != previous, election_type=election_type)
    _sync_governance_dataclass(state, governance)
    return {
        "leader": winner,
        "changed": int(winner != previous),
        "candidate_scores": candidate_scores,
        "eligible_candidates": eligible_candidates,
        "counted": int(counted),
        "election_type": election_type,
        "election_meta": election_meta,
    }


def maybe_run_scheduled_election(state: InternalState, villager_names: list[str]) -> dict[str, object] | None:
    if not schedule_election(state):
        return None
    return run_election(
        state,
        villager_names,
        election_type="scheduled",
        reason="Scheduled governance election fired at dawn.",
    )


def maybe_run_revalidation_election(state: InternalState, villager_names: list[str]) -> dict[str, object] | None:
    if not trigger_revalidation_if_needed(state):
        return None
    return run_election(
        state,
        villager_names,
        election_type="revalidation",
        reason="Leadership legitimacy revalidation was triggered.",
    )


def maybe_run_crisis_election(state: InternalState, villager_names: list[str]) -> dict[str, object] | None:
    if str(state.evolution_meta.get("active_crisis") or "") != "leadership":
        return None
    governance = get_governance(state)
    if bool(governance.get("crisis_override_active")):
        return None
    return run_election(
        state,
        villager_names,
        election_type="crisis",
        reason="Crisis override requested interim leadership transfer.",
    )


def record_dispute_resolution_time(state: InternalState, turns_elapsed: int) -> None:
    telemetry = _telemetry_bucket(state)
    values = telemetry.get("dispute_resolution_time")
    if not isinstance(values, list):
        values = []
        telemetry["dispute_resolution_time"] = values
    values.append(max(0, int(turns_elapsed)))
    values[:] = values[-80:]
