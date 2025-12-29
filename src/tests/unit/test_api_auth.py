from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel


# Create a dummy Part class for Pydantic
class MockPart(BaseModel):
    text: str | None = None
    inline_data: dict | None = None

    @classmethod
    def from_text(cls, text):
        return cls(text=text)


@pytest.fixture
def client():
    # Helper to mock Runner
    mock_runner = MagicMock()

    # Configure mocks
    mock_p = MagicMock()
    mock_p.name = "Rick"
    mock_p.menu_name = "Rick Sanchez"
    mock_p.title = "Rickbot"
    mock_p.overview = "Smartest man"
    mock_p.welcome = "Wubba Lubba"
    mock_p.prompt_question = "What?"
    mock_personalities = {"Rick": mock_p}

    # Patch global session_service
    mock_session_service = AsyncMock()
    mock_session = MagicMock()
    mock_session_service.get_session.return_value = mock_session
    mock_session_service.create_session.return_value = mock_session

    # Use patch context managers for specific targets in src.main where they are imported
    with (
        patch("src.main.get_personalities", return_value=mock_personalities),
        patch("src.main.get_agent", return_value=MagicMock()),
        patch("src.main.Runner", return_value=mock_runner),
        patch("src.main.session_service", new=mock_session_service),
        patch("src.main.get_artifact_service"),
    ):
        from src.main import app

        with TestClient(app) as c:
            yield c, mock_runner


@pytest.mark.asyncio
async def test_chat_unauthenticated(client):
    c, _ = client
    response = c.post("/chat", data={"prompt": "Hello", "personality": "Rick"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_chat_authenticated_mock(client):
    c, mock_runner = client

    # Mock runner behavior for this test
    async def mock_run_async(*args, **kwargs):
        event = MagicMock()
        event.is_final_response.return_value = True
        event.content.parts = [MockPart(text="Hello from Rick")]
        yield event

    mock_runner.run_async = mock_run_async

    headers = {"Authorization": "Bearer mock:123:test@example.com:Tester"}

    # Enable mock auth - verify_token reads from environment, so we patch os.getenv specifically for that check
    # But note: verify_token is imported in src.main. If we patch it there, we need to locate it.
    # Actually, verify_token uses os.getenv internally.
    # Conftest sets NEXT_PUBLIC_ALLOW_MOCK_AUTH="true" in env, so we might not need to patch it here
    # if we trust set_test_env. But ensuring it explicit is fine.

    response = c.post("/chat", data={"prompt": "Hello", "personality": "Rick"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["response"] == "Hello from Rick"


@pytest.mark.asyncio
async def test_personas_protected(client):
    c, _ = client
    headers = {"Authorization": "Bearer mock:123:test@example.com:Tester"}

    response = c.get("/personas", headers=headers)

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Rick"
