import sys
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel


# Create a dummy Part class for Pydantic
class MockPart(BaseModel):
    text: str | None = None
    inline_data: dict | None = None

    @classmethod
    def from_text(cls, text):
        return cls(text=text)

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Mock config
    mock_config = MagicMock()
    mock_config.agent_name = "test_agent"
    mock_config.model = "test_model"
    mock_logger = MagicMock()

    # Patch modules
    with patch.dict(sys.modules, {
        "google.auth": MagicMock(),
        "google.cloud": MagicMock(),
        "google.cloud.secretmanager": MagicMock(),
        "rickbot_utils.config": MagicMock(config=mock_config, logger=mock_logger),
        "rickbot_agent.agent": MagicMock(),
        "rickbot_agent.services": MagicMock(),
        "google.adk.runners": MagicMock(),
        "google.genai.types": MagicMock(Part=MockPart, Content=MagicMock, Blob=MagicMock),
    }):
        from google.adk.runners import Runner

        from rickbot_agent.services import get_session_service

        # Mock session service
        mock_session_service = AsyncMock()
        mock_session = MagicMock()
        mock_session_service.get_session.return_value = mock_session
        mock_session_service.create_session.return_value = mock_session
        get_session_service.return_value = mock_session_service

        # Mock runner
        mock_runner = MagicMock()
        Runner.return_value = mock_runner  # type: ignore

        # Helper to mock run_async on the runner instance
        async def mock_run_async(*args, **kwargs):
             yield MagicMock() # default yield

        mock_runner.run_async = mock_run_async

        from rickbot_agent.auth import verify_token
        from rickbot_agent.auth_models import AuthUser
        from src.main import app

        # Mock Auth
        mock_user = AuthUser(id="test_id", email="test@example.com", name="Test User", provider="mock")
        app.dependency_overrides[verify_token] = lambda: mock_user

        # We define a custom client fixture that yields the client
        # This ensures app is imported within the patch context
        with TestClient(app) as c:
             yield c, mock_runner

def test_read_root(client):
    c, _ = client
    response = c.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_chat_endpoint(client):
    c, mock_runner = client

    # Mock runner.run_async to yield events
    async def mock_run_async(*args, **kwargs):
        event = MagicMock()
        event.is_final_response.return_value = True
        event.content.parts = [MockPart(text="Hello from Rick")]
        yield event

    mock_runner.run_async = mock_run_async

    response = c.post(
        "/chat",
        data={"prompt": "Hello", "personality": "Rick", "user_id": "test_user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello from Rick"
    assert "session_id" in data

def test_chat_stream_endpoint(client):
    c, mock_runner = client

    # Mock runner.run_async to yield events
    async def mock_run_async(*args, **kwargs):
        event = MagicMock()
        event.is_model_response.return_value = True
        part = MockPart(text="Chunk 1")
        event.content.parts = [part]
        yield event

        event2 = MagicMock()
        event2.is_model_response.return_value = True
        part2 = MockPart(text="Chunk 2")
        event2.content.parts = [part2]
        yield event2

    mock_runner.run_async = mock_run_async

    response = c.post(
        "/chat_stream",
        data={"prompt": "Hello", "personality": "Rick", "user_id": "test_user"}
    )
    assert response.status_code == 200
    # Check streaming content
    content = response.content.decode("utf-8")
    assert "data: " in content
    assert "Chunk 1" in content
    assert "Chunk 2" in content
