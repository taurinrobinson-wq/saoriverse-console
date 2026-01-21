"""Tests for Velinor cipher API /decode-seed endpoint."""
import os
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import velinor.velinor_api as api


client = TestClient(api.app)


@pytest.fixture
def temp_seeds(tmp_path, monkeypatch):
    """Create temporary cipher_seeds.json for testing."""
    seeds_data = {
        "seeds": [
            {
                "id": "velinor-0-001",
                "phrase": "Wind carries the names we no longer speak.",
                "layer": 0,
                "npc": "Echo",
                "tags": ["memory", "loss"],
                "required_gates": [],
            },
            {
                "id": "velinor-1-002",
                "phrase": "The heart keeps its own archive, even when the mind refuses.",
                "layer": 1,
                "npc": "Saori",
                "tags": ["hidden", "truth"],
                "required_gates": [],
            },
            {
                "id": "velinor-2-003",
                "phrase": "Your presence softened the places I had armored for years.",
                "layer": 2,
                "npc": "Saori",
                "tags": ["tenderness", "vulnerability"],
                "required_gates": ["Quiet Bloom", "Echoed Breath"],
            },
            {
                "id": "velinor-2-004",
                "phrase": "I could not name the fear, so I carried it in silence.",
                "layer": 2,
                "npc": "Whisper",
                "tags": ["fear", "silence"],
                "required_gates": ["Primal Oblivion"],
            },
        ]
    }

    seeds_file = tmp_path / "cipher_seeds.json"
    seeds_file.write_text(json.dumps(seeds_data, indent=2), encoding="utf-8")

    # Patch the API's SEEDS_PATH and reset the cache
    monkeypatch.setattr(api, "SEEDS_PATH", str(seeds_file))
    monkeypatch.setattr(api, "_seeds_cache", None)

    return seeds_file


def test_fragment_layer_0_always_allowed(temp_seeds):
    """Fragment layers (0) should always be allowed without consent."""
    resp = client.post(
        "/decode-seed",
        json={"seed_id": "velinor-0-001", "player_state": {}, "consent": None},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["allowed"] is True
    assert data["layer"] == 0
    assert "Wind carries" in data["text"]


def test_fragment_layer_1_always_allowed(temp_seeds):
    """Deeper fragments (layer 1) should always be allowed without consent."""
    resp = client.post(
        "/decode-seed",
        json={"seed_id": "velinor-1-002", "player_state": {}, "consent": None},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["allowed"] is True
    assert data["layer"] == 1
    assert "archive" in data["text"]


def test_plaintext_denied_without_consent_or_gates(temp_seeds):
    """Layer 2 (plaintext) should be denied without consent or matching gates."""
    resp = client.post(
        "/decode-seed",
        json={
            "seed_id": "velinor-2-003",
            "player_state": {"message": "I don't know what to say."},
            "consent": None,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "denied"
    assert data["allowed"] is False
    assert data["layer"] == 2
    assert data["text"] is None


def test_plaintext_allowed_with_consent_flag(temp_seeds):
    """Layer 2 should be allowed if consent.allow_plaintext is True."""
    resp = client.post(
        "/decode-seed",
        json={
            "seed_id": "velinor-2-003",
            "player_state": {"message": "I don't know what to say."},
            "consent": {"allow_plaintext": True},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["allowed"] is True
    assert data["layer"] == 2
    assert "softened" in data["text"]


def test_plaintext_allowed_with_matching_gates(temp_seeds, monkeypatch):
    """Layer 2 should be allowed if player_state has matching emotional gates."""
    # Mock the emotional OS parser to return matching gates
    def mock_evaluate_gates(signals):
        # Return a gate that matches the required gates for this seed
        return ["Quiet Bloom"]

    monkeypatch.setattr(api, "evaluate_gates", mock_evaluate_gates)

    resp = client.post(
        "/decode-seed",
        json={
            "seed_id": "velinor-2-003",
            "player_state": {"message": "I feel gentle and open."},
            "consent": None,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["allowed"] is True
    assert data["layer"] == 2
    assert "softened" in data["text"]


def test_locked_when_gates_do_not_match(temp_seeds, monkeypatch):
    """Layer 2 should remain locked if gates don't match."""

    def mock_evaluate_gates(signals):
        # Return a gate that does NOT match the required gates
        return ["Iron Boundary"]

    monkeypatch.setattr(api, "evaluate_gates", mock_evaluate_gates)

    resp = client.post(
        "/decode-seed",
        json={
            "seed_id": "velinor-2-003",
            "player_state": {"message": "I need to protect myself."},
            "consent": None,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "denied"
    assert data["allowed"] is False
    assert data["text"] is None


def test_seed_not_found(temp_seeds):
    """Should return 404 if seed_id doesn't exist."""
    resp = client.post(
        "/decode-seed",
        json={"seed_id": "nonexistent-seed", "player_state": {}, "consent": None},
    )
    assert resp.status_code == 404


def test_multiple_gates_any_match_allows_access(temp_seeds, monkeypatch):
    """Layer 2 should be allowed if ANY of the player's gates match required gates."""

    def mock_evaluate_gates(signals):
        # Return multiple gates, one of which matches
        return ["Iron Boundary", "Primal Oblivion", "Some Other Gate"]

    monkeypatch.setattr(api, "evaluate_gates", mock_evaluate_gates)

    resp = client.post(
        "/decode-seed",
        json={
            "seed_id": "velinor-2-004",  # requires Primal Oblivion
            "player_state": {"message": "I feel overwhelmed and exposed."},
            "consent": None,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["allowed"] is True
    assert "fear" in data["text"]


def test_no_gates_required_always_allowed(temp_seeds):
    """Seeds with empty required_gates should always allow layer 2."""
    # Layer 0 and 1 have no required gates, so they're always allowed
    resp = client.post(
        "/decode-seed",
        json={
            "seed_id": "velinor-0-001",
            "player_state": {},
            "consent": None,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["allowed"] is True
