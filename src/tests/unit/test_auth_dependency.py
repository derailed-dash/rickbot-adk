from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request

from rickbot_agent.auth import verify_credentials, verify_token
from rickbot_agent.auth_models import AuthUser


def test_verify_credentials_valid_mock():
    # Mock token format: "mock:user_id:email:name"
    token = "mock:123:test@example.com:Test User"

    user = verify_credentials(token)

    assert isinstance(user, AuthUser)
    assert user.id == "123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.provider == "mock"


def test_verify_credentials_invalid_prefix():
    token = "invalid:123:test@example.com:Test User"
    user = verify_credentials(token)
    assert user is None


def test_verify_credentials_malformed():
    token = "mock:broken"
    user = verify_credentials(token)
    assert user is None


@pytest.mark.asyncio
async def test_verify_token_dependency_success():
    # Create mock request with user in state
    request = MagicMock(spec=Request)
    request.state = MagicMock()
    user = AuthUser(id="123", email="test@example.com", name="Test", provider="mock")
    request.state.user = user

    # Mock the request state to include an authenticated user
    # This simulates the state after AuthMiddleware has run

    result = await verify_token(request)
    assert result == user


@pytest.mark.asyncio
async def test_verify_token_dependency_failure():
    # Create mock request WITHOUT user in state
    request = MagicMock(spec=Request)
    # Ensure the request state does not have a user attribute
    # This simulates a request where AuthMiddleware failed or wasn't run
    class State:
        pass
    request.state = State()
    with pytest.raises(HTTPException) as excinfo:
        await verify_token(request)
    assert excinfo.value.status_code == 401

