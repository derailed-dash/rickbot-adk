import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from rickbot_agent.auth_models import AuthUser


@pytest.mark.asyncio
async def test_verify_mock_token_valid():
    try:
        from rickbot_agent.auth import verify_token
    except ImportError:
        pytest.fail("Could not import verify_token from rickbot_agent.auth")

    # Mock token format: "mock:user_id:email:name"
    token = "mock:123:test@example.com:Test User"

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await verify_token(creds)

    assert isinstance(user, AuthUser)
    assert user.id == "123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.provider == "mock"

@pytest.mark.asyncio
async def test_verify_mock_token_invalid_prefix():
    try:
        from rickbot_agent.auth import verify_token
    except ImportError:
        pytest.fail("Could not import verify_token")

    token = "invalid:123:test@example.com:Test User"
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as excinfo:
        await verify_token(creds)
    assert excinfo.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_mock_token_malformed():
    try:
        from rickbot_agent.auth import verify_token
    except ImportError:
        pytest.fail("Could not import verify_token")

    token = "mock:broken"
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as excinfo:
        await verify_token(creds)
    assert excinfo.value.status_code == 401
