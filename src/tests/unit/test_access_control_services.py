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
    # Setup mock for .where("id", "==", user_id).where("provider", "==", provider).limit(1).get()
    mock_doc = MagicMock()
    mock_doc.id = "ReadableName:mock:test-user"
    mock_doc.to_dict.return_value = {"role": "supporter"}

    # Mock chain: collection().where().where().limit().get()
    mock_coll = mock_db.collection.return_value
    mock_where1 = mock_coll.where.return_value
    mock_where2 = mock_where1.where.return_value
    mock_limit = mock_where2.limit.return_value
    mock_limit.get.return_value = [mock_doc]

    role = get_user_role("test-user", "mock")
    assert role == "supporter"
    mock_db.collection.assert_called_with("users")

def test_get_user_role_not_found(mock_db):
    # Setup mock for empty result
    mock_coll = mock_db.collection.return_value
    mock_where1 = mock_coll.where.return_value
    mock_where2 = mock_where1.where.return_value
    mock_limit = mock_where2.limit.return_value
    mock_limit.get.return_value = []

    # Should default to 'standard'
    role = get_user_role("unknown-user", "google")
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
