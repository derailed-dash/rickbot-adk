from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from rickbot_agent.auth import verify_token
from rickbot_agent.auth_models import AuthUser


@pytest.fixture
def client():
    from src.main import app

    # Mock Auth
    mock_user = AuthUser(id="test_id", email="test@example.com", name="Test User", provider="mock")
    app.dependency_overrides[verify_token] = lambda: mock_user

    with TestClient(app) as c:
        yield c


# Mock data behaving like Personality objects
class MockPersonality:
    def __init__(self, name, menu_name, title, overview, welcome, prompt_question):
        self.name = name
        self.menu_name = menu_name
        self.title = title
        self.overview = overview
        self.welcome = welcome
        self.prompt_question = prompt_question


@patch("src.main.get_personalities")
def test_get_personas(mock_get_personalities, client):
    """Test the /personas endpoint with mocked data."""
    # Setup mock return value
    mock_personalities = {
        "Rick": MockPersonality("Rick", "Rick Sanchez", "I'm Rickbot!", "Smartest man", "Whatever", "What do you want?"),
        "Yoda": MockPersonality("Yoda", "Yoda", "Yoda I am", "Wise teacher", "Do or do not", "Speak your mind"),
    }
    mock_get_personalities.return_value = mock_personalities

    response = client.get("/personas")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check for specific known personalities based on personalities.yaml
    names = [p["name"] for p in data]
    assert "Rick" in names
    assert "Yoda" in names

    # Verify structure of a persona object
    rick = next(p for p in data if p["name"] == "Rick")
    assert rick["description"] == "Rick Sanchez"
    assert rick["avatar"] == "/avatars/rick.png"

    # Assert new fields are present
    assert rick["title"] == "I'm Rickbot!"
    assert rick["overview"] == "Smartest man"
    assert rick["welcome"] == "Whatever"
    assert rick["prompt_question"] == "What do you want?"
