import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from unittest.mock import MagicMock, patch

# Import after implementing or mock it
from rickbot_agent.auth_middleware import PersonaAccessMiddleware
from rickbot_agent.auth_models import AuthUser, PersonaAccessDeniedException

@pytest.fixture
def mock_app():
    app = FastAPI()

    # Add the handler to the mock app to test it
    from src.main import persona_access_denied_handler
    app.add_exception_handler(PersonaAccessDeniedException, persona_access_denied_handler)

    class MockAuthMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await self.app(scope, receive, send)
                return

            request = Request(scope)
            user_id = request.headers.get("X-Test-User")
            if user_id:
                scope["user"] = AuthUser(
                    id=user_id,
                    email=user_id,
                    name=user_id,
                    provider="google"
                )
            else:
                scope["user"] = None
            
            await self.app(scope, receive, send)

    app.add_middleware(PersonaAccessMiddleware)
    app.add_middleware(MockAuthMiddleware)

    @app.post("/chat")
    async def chat(request: Request):
        return {"status": "ok"}

    return app

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_allows_standard_persona(mock_get_required, mock_get_user, mock_app):
    mock_get_user.return_value = "standard"
    mock_get_required.return_value = "standard"

    client = TestClient(mock_app)
    response = client.post(
        "/chat", 
        data={"personality": "Rick", "prompt": "hello"}, 
        headers={"X-Test-User": "user@example.com"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_blocks_supporter_persona_for_standard_user(mock_get_required, mock_get_user, mock_app):
    mock_get_user.return_value = "standard"
    mock_get_required.return_value = "supporter"

    client = TestClient(mock_app)
    response = client.post(
        "/chat", 
        data={"personality": "Yasmin", "prompt": "hello"}, 
        headers={"X-Test-User": "user@example.com"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["error_code"] == "UPGRADE_REQUIRED"
    assert "Yasmin" in data["detail"]
    assert data["required_role"] == "supporter"

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_allows_supporter_persona_for_supporter_user(mock_get_required, mock_get_user, mock_app):
    mock_get_user.return_value = "supporter"
    mock_get_required.return_value = "supporter"

    client = TestClient(mock_app)
    response = client.post(
        "/chat", 
        data={"personality": "Yasmin", "prompt": "hello"}, 
        headers={"X-Test-User": "supporter@example.com"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_blocks_unauthenticated_user_from_supporter_persona(mock_get_required, mock_get_user, mock_app):
    mock_get_user.return_value = "standard"
    mock_get_required.return_value = "supporter"

    client = TestClient(mock_app)
    response = client.post(
        "/chat", 
        data={"personality": "Yasmin", "prompt": "hello"}
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "UPGRADE_REQUIRED"