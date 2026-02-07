from unittest.mock import patch

import pytest

from main import check_persona_access
from rickbot_agent.auth_models import AuthUser, PersonaAccessDeniedException


@pytest.mark.asyncio
async def test_check_persona_access_granted_standard():
    # Rick is a standard persona
    mock_user = AuthUser(id="user123", email="user@example.com", name="Test User", provider="mock")

    with patch("main.get_required_role", return_value="standard"), \
         patch("main.get_user_role", return_value="standard"):

        # Should not raise any exception
        await check_persona_access(personality="Rick", user=mock_user)

@pytest.mark.asyncio
async def test_check_persona_access_denied_supporter_required():
    # Yasmin is a supporter persona, user is standard
    mock_user = AuthUser(id="user123", email="user@example.com", name="Test User", provider="mock")

    with patch("main.get_required_role", return_value="supporter"), \
         patch("main.get_user_role", return_value="standard"):

        with pytest.raises(PersonaAccessDeniedException) as excinfo:
            await check_persona_access(personality="Yasmin", user=mock_user)

        assert excinfo.value.personality == "Yasmin"
        assert excinfo.value.required_role == "supporter"

@pytest.mark.asyncio
async def test_check_persona_access_granted_supporter():
    # Yasmin is a supporter persona, user is supporter
    mock_user = AuthUser(id="user123", email="user@example.com", name="Test User", provider="mock")

    with patch("main.get_required_role", return_value="supporter"), \
         patch("main.get_user_role", return_value="supporter"):

        # Should not raise any exception
        await check_persona_access(personality="Yasmin", user=mock_user)

@pytest.mark.asyncio
async def test_check_persona_access_does_not_sync_metadata():
    # Verify that metadata sync is NOT called during chat interaction (moved to login)
    mock_user = AuthUser(id="google-123", email="google@example.com", name="Google User", provider="google")

    with patch("main.get_required_role", return_value="standard"), \
         patch("main.get_user_role", return_value="standard"), \
         patch("rickbot_agent.services.sync_user_metadata") as mock_sync:

        await check_persona_access(personality="Rick", user=mock_user)
        mock_sync.assert_not_called()
