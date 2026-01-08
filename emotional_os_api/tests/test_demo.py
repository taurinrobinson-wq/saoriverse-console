from fastapi.testclient import TestClient
from emotional_os_api import app
import os


def test_demo_auth_required():
    client = TestClient(app)
    r = client.post("/v1/demo", json={"text": "hi", "user_id": "u1"})
    assert r.status_code == 401


def test_demo_flow_with_key(monkeypatch, tmp_path):
    # Use a real key and temp storage to allow engine initialization
    monkeypatch.setenv("EMOTIONAL_OS_API_KEY", "test-key")
    monkeypatch.setenv("EMOTIONAL_OS_STORAGE_PATH", str(tmp_path / "fs_state.json"))
    client = TestClient(app)
    headers = {"x-api-key": "test-key"}
    payload = {"text": "I feel lost", "user_id": "demo-user", "signals": {"warmth": 0.7}}
    r = client.post("/v1/demo", json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert "state" in data
    assert data["meta"]["user_id"] == "demo-user"
