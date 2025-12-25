import os
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Sets environment variables for the entire test session."""
    with patch.dict(os.environ, {"RICKBOT_TEST_MODE": "true"}):
        yield
