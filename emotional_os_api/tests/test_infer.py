from fastapi.testclient import TestClient
from emotional_os_api import app


def test_infer_stub_response():
    client = TestClient(app)
    payload = {"user_id": "test-user", "text": "hello world"}
    r = client.post("/infer", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert isinstance(data["response"], str)
