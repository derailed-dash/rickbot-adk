from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Mock data behaving like Personality objects
class MockPersonality:
    def __init__(self, name, menu_name):
        self.name = name
        self.menu_name = menu_name

@patch("src.main.get_personalities")
def test_get_personas(mock_get_personalities):
    """Test the /personas endpoint with mocked data."""
    # Setup mock return value
    mock_personalities = {
        "Rick": MockPersonality("Rick", "Rick Sanchez"),
        "Yoda": MockPersonality("Yoda", "Yoda"),
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
