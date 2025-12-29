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

    # Patch the GLOBAL session_service in src.main which is already initialized
    # We must patch the OBJECT, not the module factory function, because the module is already loaded.
    # However, since we just need it to work during the test, patching the symbol in src.main is enough?
    # No, src.main.session_service is assigned at import time.
    # To mock it, we should patch "src.main.session_service" directly.

    # Mock session service
    mock_session_service = AsyncMock()
    mock_session = MagicMock()
    mock_session_service.get_session.return_value = mock_session
    mock_session_service.create_session.return_value = mock_session

    # Use patch context managers for specific targets in src.main where they are imported
    with (
        patch("src.main.get_agent", return_value=MagicMock()),
        patch("src.main.Runner", return_value=mock_runner),
        patch("src.main.session_service", new=mock_session_service),
        patch("src.main.artifact_service"),
    ):
        # Mock Auth User
        from rickbot_agent.auth_models import AuthUser

        mock_user = AuthUser(id="test_id", email="test@example.com", name="Test User", provider="mock")
        # We can't override dependency_overrides easily inside valid importing context if app is top-level
        # But we can patch the verify_token function to return our user
        # Note: Depends(verify_token) calls verify_token(creds)
        # However, FastAPI dependencies are simpler to override via app.dependency_overrides if verify_token is the dependency

        # But wait, verify_token takes creds.
        # For unit testing the endpoint logic (bypassing auth), dependency_overrides is best.
        # But here we are patched.

        # Use the REAL verify_token function as the key for dependency overrides
        # We need to import it from where it's defined or where src.main imported it from UNPATCHED
        from rickbot_agent.auth import verify_token
        from src.main import app

        # Override the dependency
        app.dependency_overrides[verify_token] = lambda: mock_user

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

    response = c.post("/chat", data={"prompt": "Hello", "personality": "Rick", "user_id": "test_user"})
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello from Rick"
    assert "session_id" in data


def test_chat_stream_endpoint(client):
    c, mock_runner = client

    # Mock runner.run_async to yield events
    async def mock_run_async(*args, **kwargs):
        # We need to mimic the event structure src/main.py expects
        # event.content.parts -> part.text

        # Chunk 1
        event1 = MagicMock()
        event1.actions = None  # Prevent MagicMock serialization error in json.dumps
        event1.get_function_calls.return_value = []
        # The code checks: if event.content and event.content.parts:
        event1.content.parts = [MockPart(text="Chunk 1")]
        yield event1

        # Chunk 2
        event2 = MagicMock()
        event2.actions = None  # Prevent MagicMock serialization error in json.dumps
        event2.get_function_calls.return_value = []
        event2.content.parts = [MockPart(text="Chunk 2")]
        yield event2

    mock_runner.run_async = mock_run_async

    response = c.post("/chat_stream", data={"prompt": "Hello", "personality": "Rick", "user_id": "test_user"})
    assert response.status_code == 200

    # Check streaming content by parsing SSE
    import json

    content = response.content.decode("utf-8")
    lines = content.strip().split("\n\n")

    # We expect:
    # 1. session_id
    # 2. Chunk 1
    # 3. Chunk 2
    # 4. done

    events = []
    for line in lines:
        if line.startswith("data: "):
            payload = line[6:]
            try:
                events.append(json.loads(payload))
            except json.JSONDecodeError:
                pytest.fail(f"Failed to decode JSON from SSE line: {line!r}")

    assert len(events) >= 3
    assert "session_id" in events[0]

    # Look for chunks
    chunks = [e["chunk"] for e in events if "chunk" in e]
    assert "Chunk 1" in chunks
    assert "Chunk 2" in chunks

    # Verify done event
    assert events[-1] == {"done": True}
