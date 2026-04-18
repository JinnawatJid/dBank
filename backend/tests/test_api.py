import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

from unittest.mock import patch

def test_ask_endpoint_skeleton():
    # Since we implemented the generative AI orchestration loop, we must mock the genai model
    # to avoid needing a real API key and making network calls during the unit test.
    test_payload = {"query": "What caused the spike in tickets?"}

    with patch("backend.api.routes.genai.GenerativeModel") as MockModel:
        # Mock the chat session and response
        mock_chat = MockModel.return_value.start_chat.return_value

        class MockPart:
            def __init__(self, text):
                self.text = text

        mock_chat.send_message.return_value.parts = [MockPart(f"You asked: '{test_payload['query']}'. I am a skeleton API, so I don't know the answer yet!")]

        with patch("backend.api.routes.settings.GOOGLE_API_KEY", "dummy_key"):
            response = client.post("/api/v1/ask", json=test_payload)

            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "tools_used" in data
            assert "I am a skeleton API" in data["answer"] or test_payload["query"] in data["answer"]
