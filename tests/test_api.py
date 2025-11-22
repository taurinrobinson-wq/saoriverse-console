from fastapi.testclient import TestClient
from emotional_os.main import app

client = TestClient(app)


def test_ingest_feedback():
    response = client.post(
        "/feedback/ingest_feedback",
        json={"rating": 1, "text": "Corrected response",
              "features": [0.5, 0.2, -0.1]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "updated_weights" in data
