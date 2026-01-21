import os
import json
from fastapi.testclient import TestClient

import velinor.velinor_api as api


client = TestClient(api.app)


def write_seed_file(tmp_path, final_plaintext=True):
    seed = {
        "seeds": [
            {
                "id": "demo-cat-001",
                "phrase": "I am so happy to see this",
                "layer": 2,
                "npc": "Demo",
                "tags": ["joy"],
                "required_gates": ["Quiet Bloom"],
            }
        ]
    }
    p = tmp_path / "cipher_seeds.json"
    p.write_text(json.dumps(seed, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_decode_fragment_allowed_by_default(tmp_path, monkeypatch):
    # ensure CIPHER_KEY exists
    monkeypatch.setenv("CIPHER_KEY", "testkey")
    # write a temp seeds file and point loader to it by replacing file contents
    seeds_path = write_seed_file(tmp_path)
    # patch load_seeds to read from our temp file
    monkeypatch.setattr(api, "SEEDS_PATH", os.path.abspath(seeds_path))
    monkeypatch.setattr(api, "_seeds_cache", None)

    resp = client.post("/decode-seed", json={
        "seed_id": "demo-cat-001",
        "player_state": {"message": "that's wonderful, i'm so happy"},
        "consent": {"allow_plaintext": True}
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["allowed"] is True
    assert "text" in data


def test_final_layer_requires_consent(tmp_path, monkeypatch):
    monkeypatch.setenv("CIPHER_KEY", "testkey")
    seeds_path = write_seed_file(tmp_path)
    monkeypatch.setattr(api, "SEEDS_PATH", os.path.abspath(seeds_path))
    monkeypatch.setattr(api, "_seeds_cache", None)

    # Without consent -> denied
    resp = client.post("/decode-seed", json={
        "seed_id": "demo-cat-001",
        "player_state": {"message": "fine"},
        "consent": {"allow_plaintext": False}
    })
    assert resp.status_code == 200
    assert resp.json().get("status") == "denied"

    # With consent -> allowed and returns plaintext
    resp2 = client.post("/decode-seed", json={
        "seed_id": "demo-cat-001",
        "player_state": {"message": "fine"},
        "consent": {"allow_plaintext": True}
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "ok"
    assert data2["allowed"] is True
