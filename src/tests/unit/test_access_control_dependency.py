import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from rickbot_agent.auth_models import AuthUser, PersonaAccessDeniedException
from main import check_persona_access

@pytest.mark.asyncio
async def test_check_persona_access_granted_standard():
    # Rick is a standard persona
    mock_user = AuthUser(id="user123", email="user@example.com", name="Test User", provider="mock")
    
    with patch("main.get_required_role", return_value="standard"), \
         patch("main.get_user_role", return_value="standard"), \
         patch("rickbot_agent.services.sync_user_metadata") as mock_sync:
        
        # Should not raise any exception
        await check_persona_access(personality="Rick", user=mock_user)
        mock_sync.assert_called_once_with(mock_user.id, mock_user.email, mock_user.name)

@pytest.mark.asyncio
async def test_check_persona_access_denied_supporter_required():
    # Yasmin is a supporter persona, user is standard
    mock_user = AuthUser(id="user123", email="user@example.com", name="Test User", provider="mock")
    
    with patch("main.get_required_role", return_value="supporter"), \
         patch("main.get_user_role", return_value="standard"), \
         patch("rickbot_agent.services.sync_user_metadata"):
        
        with pytest.raises(PersonaAccessDeniedException) as excinfo:
            await check_persona_access(personality="Yasmin", user=mock_user)
        
        assert excinfo.value.personality == "Yasmin"
        assert excinfo.value.required_role == "supporter"

@pytest.mark.asyncio
async def test_check_persona_access_granted_supporter():
    # Yasmin is a supporter persona, user is supporter
    mock_user = AuthUser(id="user123", email="user@example.com", name="Test User", provider="mock")
    
    with patch("main.get_required_role", return_value="supporter"), \
         patch("main.get_user_role", return_value="supporter"), \
         patch("rickbot_agent.services.sync_user_metadata"):
        
        # Should not raise any exception
        await check_persona_access(personality="Yasmin", user=mock_user)

@pytest.mark.asyncio
async def test_check_persona_access_syncs_metadata():
    mock_user = AuthUser(id="google-123", email="google@example.com", name="Google User", provider="google")
    
    with patch("main.get_required_role", return_value="standard"), \
         patch("main.get_user_role", return_value="standard"), \
         patch("rickbot_agent.services.sync_user_metadata") as mock_sync:
        
        await check_persona_access(personality="Rick", user=mock_user)
        mock_sync.assert_called_once_with("google-123", "google@example.com", "Google User")
