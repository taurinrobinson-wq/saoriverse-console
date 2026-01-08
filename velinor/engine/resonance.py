"""Simple resonance engine for Velinor.

This module provides minimal functions to map player `tone` vectors
into NPC `remnants` changes according to a provided `influence_map`.
The implementation is intentionally small and deterministic to make
unit testing and iterative improvement straightforward.
"""
from typing import Dict, Mapping


def apply_tone_to_remnants(tone: Mapping[str, float], remnants: Dict[str, float], influence_map: Mapping[str, Mapping[str, float]], scale: float = 1.0) -> Dict[str, float]:
    """Apply a tone vector to a single NPC's remnants.

    Args:
        tone: mapping from tone-dimension -> magnitude (e.g., {'empathy': 1.0}).
        remnants: mapping of the NPC's current remnants to be updated in-place (but a copy is returned).
        influence_map: mapping from tone-dimension -> {remnant-dimension: weight}.
        scale: global multiplier for the effect size.

    Returns:
        A new dict with updated remnants.
    """
    updated = dict(remnants)
    for t_key, t_val in tone.items():
        if t_val == 0:
            continue
        mapping = influence_map.get(t_key, {})
        for r_key, weight in mapping.items():
            delta = t_val * weight * scale
            updated[r_key] = float(updated.get(r_key, 0.0)) + delta
    return updated


def apply_tone_to_all_npcs(tone: Mapping[str, float], npc_profiles: Mapping[str, Mapping], influence_map: Mapping[str, Mapping[str, float]], scale: float = 1.0) -> Dict[str, Mapping]:
    """Apply a tone to all NPCs and return updated profiles.

    NPC profiles are expected to be a mapping of npc_id -> {name, role, remnants}.
    The returned structure mirrors `npc_profiles` but with updated `remnants` dicts.
    """
    out = {}
    for npc_id, profile in npc_profiles.items():
        remnants = profile.get("remnants", {})
        out_profile = dict(profile)
        out_profile["remnants"] = apply_tone_to_remnants(tone, remnants, influence_map, scale=scale)
        out[npc_id] = out_profile
    return out


def simulate_encounter(sequence_of_tones: Mapping[int, Mapping[str, float]], npc_profiles: Mapping[str, Mapping], influence_map: Mapping[str, Mapping[str, float]], decay: float = 0.0) -> Dict[str, Mapping]:
    """Simulate a sequence of tones over time.

    Args:
        sequence_of_tones: mapping from step index -> tone mapping.
        npc_profiles: initial npc profiles as described above.
        influence_map: influence map.
        decay: optional per-step decay factor applied to remnants (0.0 means no decay).

    Returns:
        Final npc profiles with updated remnants.
    """
    current = {k: dict(v) for k, v in npc_profiles.items()}
    # ensure remnants are mutable copies
    for k in current:
        current[k]["remnants"] = dict(current[k].get("remnants", {}))

    for step in sorted(sequence_of_tones.keys()):
        tone = sequence_of_tones[step]
        updated = apply_tone_to_all_npcs(tone, current, influence_map, scale=1.0)
        # optionally apply decay
        for npc_id, profile in updated.items():
            remnants = profile.get("remnants", {})
            if decay:
                for rk in list(remnants.keys()):
                    remnants[rk] = float(remnants[rk]) * (1.0 - decay)
            current[npc_id]["remnants"] = remnants

    return current
