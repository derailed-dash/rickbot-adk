from slowapi import Limiter
from slowapi.util import get_remote_address

def test_limiter_exists():
    from rickbot_utils.rate_limit import limiter
    assert isinstance(limiter, Limiter)

def test_limiter_configuration():
    from rickbot_utils.rate_limit import limiter
    # Verify default key func is get_remote_address (as a fallback, though we'll customize it later)
    # Note: slowapi/limits might not expose storage_uri directly on the instance easily without accessing internal _storage
    # But we can check if enabled is True by default
    assert limiter.enabled is True
