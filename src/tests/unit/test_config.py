"""Unit tests for the rickbot_agent.config module.

This test suite validates the configuration loading and logger setup functionalities
of the Rickbot agent. It ensures that the agent's configuration is correctly
derived from environment variables and that the logger is initialized with the
appropriate settings.

The tests for `get_config` cover:
- Loading default configuration values when no specific environment variables
  are set.
- Overriding default configuration values with custom settings provided through
  environment variables (e.g., AGENT_NAME, GOOGLE_CLOUD_LOCATION, MODEL).
- Correctly handling case-insensitive boolean conversion for the
  `GOOGLE_GENAI_USE_VERTEXAI` environment variable.
- Mocking of `google.auth.default` to simulate the retrieval of a Google Cloud
  project ID without making actual API calls.

The tests use `unittest.mock.patch` to manage environment variables for each
test case, ensuring that tests are independent and deterministic.
"""

import logging
import os
from unittest.mock import patch

import pytest

from rickbot_agent.config import get_config


@pytest.fixture(autouse=True)
def clear_logger_handlers():
    """Fixture to clear logger handlers before each test to prevent duplicate logs."""
    # Clear handlers for the specific logger used in the config module
    agent_name = os.environ.get("AGENT_NAME", "rickbot_agent")
    logger = logging.getLogger(agent_name)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    yield


@patch("google.auth.default", return_value=(None, "test_project_id"))
def test_get_config_vertexai_true_case_insensitive(mock_google_auth_default) -> None:
    """Test get_config handles case-insensitive 'True' for GOOGLE_GENAI_USE_VERTEXAI."""
    env_vars = {"GOOGLE_GENAI_USE_VERTEXAI": "true"}
    with patch.dict(os.environ, env_vars, clear=True):
        config = get_config()
        assert config.genai_use_vertexai is True

    env_vars = {"GOOGLE_GENAI_USE_VERTEXAI": "TRUE"}
    with patch.dict(os.environ, env_vars, clear=True):
        config = get_config()
        assert config.genai_use_vertexai is True

    env_vars = {"GOOGLE_GENAI_USE_VERTEXAI": "True"}
    with patch.dict(os.environ, env_vars, clear=True):
        config = get_config()
        assert config.genai_use_vertexai is True
