import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ask_endpoint_skeleton():
    # We must mock the db dependency in the future if we don't want to connect to a real DB during tests,
    # but for now, the skeleton endpoint doesn't actually execute SQL, so it's safe to test if the DB is running.
    test_payload = {"query": "What caused the spike in tickets?"}
    response = client.post("/ask", json=test_payload)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "tools_used" in data
    assert test_payload["query"] in data["answer"]
