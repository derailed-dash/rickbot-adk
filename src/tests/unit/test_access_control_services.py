from unittest.mock import MagicMock, patch

import pytest

from src.rickbot_agent.services import get_required_role, get_user_role


@pytest.fixture
def mock_db():
    with patch("src.rickbot_agent.services._get_firestore_client") as mock:
        db = MagicMock()
        mock.return_value = db
        yield db

def test_get_user_role_found(mock_db):
    # Setup mock for .where("id", "==", user_id).limit(1).get()
    mock_doc = MagicMock()
    mock_doc.id = "ReadableName:test-user"
    mock_doc.to_dict.return_value = {"role": "supporter"}
    
    mock_query = mock_db.collection.return_value.where.return_value.limit.return_value
    mock_query.get.return_value = [mock_doc]

    role = get_user_role("test-user")
    assert role == "supporter"
    mock_db.collection.assert_called_with("users")

def test_get_user_role_not_found(mock_db):
    # Setup mock for empty result
    mock_query = mock_db.collection.return_value.where.return_value.limit.return_value
    mock_query.get.return_value = []

    # Should default to 'standard'
    role = get_user_role("unknown-user")
    assert role == "standard"

def test_get_required_role_found(mock_db):
    # Setup mock for persona_tiers
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"required_role": "supporter"}
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    role = get_required_role("yasmin")
    assert role == "supporter"
    mock_db.collection.assert_called_with("persona_tiers")

def test_get_required_role_not_found(mock_db):
    # Setup mock for missing persona
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    # Should default to 'standard'
    role = get_required_role("unknown-persona")
    assert role == "standard"