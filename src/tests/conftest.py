import os
from unittest.mock import patch

import pytest

# Ensure GOOGLE_CLOUD_PROJECT is set for test collection
if "GOOGLE_CLOUD_PROJECT" not in os.environ:
    os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Sets environment variables for the entire test session."""
    with patch.dict(os.environ, {"RICKBOT_TEST_MODE": "true", "NEXT_PUBLIC_ALLOW_MOCK_AUTH": "true"}):
        yield
