import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
from pydantic import BaseModel

# Create a dummy Part class for Pydantic
class MockPart(BaseModel):
    text: str | None = None
    inline_data: dict | None = None

    @classmethod
    def from_text(cls, text):
        return cls(text=text)

# Patch modules
mock_personality_mod = MagicMock()
mock_agent_mod = MagicMock()
sys.modules["rickbot_agent.personality"] = mock_personality_mod
sys.modules["rickbot_agent.agent"] = mock_agent_mod

mock_p = MagicMock()
mock_p.name = "Rick"
mock_p.menu_name = "Rick Sanchez"
mock_personalities = {"Rick": mock_p}
mock_personality_mod.get_personalities.return_value = mock_personalities
mock_agent_mod.get_agent.return_value = MagicMock()

from src.main import app
from fastapi.testclient import TestClient
from rickbot_agent.auth_models import AuthUser

client = TestClient(app)
@pytest.mark.asyncio
async def test_chat_unauthenticated():
    response = client.post(
        "/chat",
        data={"prompt": "Hello", "personality": "Rick"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_chat_authenticated_mock():
    # Mock session service
    from src.main import session_service
    mock_session = MagicMock()
    session_service.get_session = AsyncMock(return_value=mock_session)
    session_service.create_session = AsyncMock(return_value=mock_session)

    # Mock runner
    mock_runner = MagicMock()
    async def mock_run_async(*args, **kwargs):
        event = MagicMock()
        event.is_final_response.return_value = True
        event.content.parts = [MockPart(text="Hello from Rick")]
        yield event
    mock_runner.run_async = mock_run_async

    headers = {"Authorization": "Bearer mock:123:test@example.com:Tester"}
    # Enable mock auth
    with patch("os.getenv", side_effect=lambda k, d=None: "true" if k == "NEXT_PUBLIC_ALLOW_MOCK_AUTH" else d), \
         patch("src.main.Runner", return_value=mock_runner):
        response = client.post(
            "/chat",
            data={"prompt": "Hello", "personality": "Rick"},
            headers=headers
        )
    assert response.status_code == 200
    assert response.json()["response"] == "Hello from Rick"

@pytest.mark.asyncio
async def test_personas_protected():
    headers = {"Authorization": "Bearer mock:123:test@example.com:Tester"}
    with patch("os.getenv", side_effect=lambda k, d=None: "true" if k == "NEXT_PUBLIC_ALLOW_MOCK_AUTH" else d), \
         patch("src.main.get_personalities", return_value=mock_personalities):
        response = client.get("/personas", headers=headers)
    
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Rick"
