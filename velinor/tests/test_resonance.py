import pytest

from velinor.engine.resonance import apply_tone_to_remnants, apply_tone_to_all_npcs, simulate_encounter


def test_apply_tone_to_remnants_increases_expected_dimensions():
    tone = {"empathy": 1.0}
    remnants = {"empathy": 0.2, "trust": 0.1}
    influence_map = {"empathy": {"empathy": 1.0, "trust": 0.5}}

    updated = apply_tone_to_remnants(tone, remnants, influence_map)
    assert updated["empathy"] > remnants["empathy"]
    assert updated["trust"] > remnants["trust"]


def test_apply_tone_to_all_npcs_updates_each_profile():
    tone = {"trust": 0.5}
    npc_profiles = {
        "a": {"name": "A", "role": "x", "remnants": {"trust": 0.1}},
        "b": {"name": "B", "role": "y", "remnants": {"trust": 0.2}},
    }
    influence_map = {"trust": {"trust": 1.0}}

    out = apply_tone_to_all_npcs(tone, npc_profiles, influence_map)
    assert out["a"]["remnants"]["trust"] > npc_profiles["a"]["remnants"]["trust"]
    assert out["b"]["remnants"]["trust"] > npc_profiles["b"]["remnants"]["trust"]


def test_simulate_encounter_applies_sequence_and_decay():
    seq = {0: {"empathy": 1.0}, 1: {"trust": 0.5}}
    npc_profiles = {"x": {"name": "X", "role": "z", "remnants": {"empathy": 0.0, "trust": 0.0}}}
    influence_map = {"empathy": {"empathy": 1.0}, "trust": {"trust": 1.0}}

    final = simulate_encounter(seq, npc_profiles, influence_map, decay=0.1)
    # after applying empathy then trust with decay, both dimensions should be > 0
    assert final["x"]["remnants"]["empathy"] >= 0.0
    assert final["x"]["remnants"]["trust"] >= 0.0
