from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_agents_endpoint_returns_agents_key():
    response = client.get("/agents")

    assert response.status_code == 200

    data = response.json()
    assert "agents" in data
    assert isinstance(data["agents"], list)