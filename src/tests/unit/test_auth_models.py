import pytest
from pydantic import ValidationError

# We assume the module will be created later
try:
    from rickbot_agent.auth_models import AuthUser
except ImportError:
    pass

def test_auth_user_creation_valid():
    """Test creating an AuthUser with valid data."""
    user = AuthUser(
        id="12345",
        email="test@example.com",
        name="Test User",
        provider="google"
    )
    assert user.id == "12345"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.provider == "google"

def test_auth_user_validation_missing_email():
    """Test that email is required."""
    with pytest.raises(ValidationError):
        AuthUser(
            id="12345",
            name="Test User",
            provider="google"
        )
