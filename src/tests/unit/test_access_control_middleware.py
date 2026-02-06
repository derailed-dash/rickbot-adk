from unittest.mock import patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

# Import after implementing or mock it
from rickbot_agent.auth_middleware import PersonaAccessMiddleware
from rickbot_agent.auth_models import AuthUser


@pytest.fixture
def app():
    app = FastAPI()

    class MockAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Simulate AuthMiddleware setting request.state.user
            user_id = request.headers.get("X-Test-User")
            if user_id:
                request.state.user = AuthUser(
                    id=user_id,
                    email=user_id,
                    name=user_id,
                    provider="google"
                )
            else:
                request.state.user = None
            return await call_next(request)

    app.add_middleware(PersonaAccessMiddleware)
    app.add_middleware(MockAuthMiddleware)

    @app.post("/chat")
    async def chat(request: Request):
        return {"status": "ok"}

    return app

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_allows_standard_persona(mock_get_required, mock_get_user, app):
    mock_get_user.return_value = "standard"
    mock_get_required.return_value = "standard"

    client = TestClient(app)
    response = client.post(
        "/chat", 
        data={"personality": "Rick", "prompt": "hello"}, 
        headers={"X-Test-User": "user@example.com"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_blocks_supporter_persona_for_standard_user(mock_get_required, mock_get_user, app):
    mock_get_user.return_value = "standard"
    mock_get_required.return_value = "supporter"

    client = TestClient(app)
    # PersonaAccessMiddleware needs to handle both Form and JSON, but /chat uses Form
    response = client.post(
        "/chat", 
        data={"personality": "Yasmin", "prompt": "hello"}, 
        headers={"X-Test-User": "user@example.com"}
    )

    assert response.status_code == 403
    assert "Upgrade Required" in response.json()["detail"]

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_allows_supporter_persona_for_supporter_user(mock_get_required, mock_get_user, app):
    mock_get_user.return_value = "supporter"
    mock_get_required.return_value = "supporter"

    client = TestClient(app)
    response = client.post(
        "/chat", 
        data={"personality": "Yasmin", "prompt": "hello"}, 
        headers={"X-Test-User": "supporter@example.com"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("rickbot_agent.auth_middleware.get_user_role")
@patch("rickbot_agent.auth_middleware.get_required_role")
def test_middleware_blocks_unauthenticated_user_from_supporter_persona(mock_get_required, mock_get_user, app):
    mock_get_user.return_value = "standard" # Default for unauthenticated if we want
    mock_get_required.return_value = "supporter"

    client = TestClient(app)
    # No X-Test-User header means request.state.user is None
    response = client.post(
        "/chat", 
        data={"personality": "Yasmin", "prompt": "hello"}
    )

    assert response.status_code == 403
