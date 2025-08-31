"""Unit tests for the rickbot_agent.config module.

This test suite validates the configuration loading and logger setup functionalities
of the Rickbot agent. It ensures that the agent's configuration is correctly
derived from environment variables and that the logger is initialized with the
appropriate settings.

The tests for `setup_logger` cover:
- Initialization of the logger with the default log level (INFO) when no
  environment variable is specified.
- Correctly setting the log level to DEBUG and WARNING based on the `LOG_LEVEL`
  environment variable.
- A fixture is used to clear logging handlers before each test to ensure
  isolation and prevent log duplication.

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

from rickbot_agent.config import get_config, setup_logger


@pytest.fixture(autouse=True)
def clear_logger_handlers():
    """Fixture to clear logger handlers before each test to prevent duplicate logs."""
    for handler in logging.getLogger("rickbot_agent").handlers[:]:
        logging.getLogger("rickbot_agent").removeHandler(handler)
    yield


def test_setup_logger_default_level():
    """Test that setup_logger sets the default log level to INFO."""
    with patch.dict(os.environ, {}, clear=True):  # Ensure no LOG_LEVEL is set
        logger = setup_logger()
        assert logger.level == logging.INFO
        assert logger.name == "rickbot_agent"
        assert len(logger.handlers) > 0


def test_setup_logger_debug_level():
    """Test that setup_logger sets the log level to DEBUG when specified."""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=True):
        logger = setup_logger()
        assert logger.level == logging.DEBUG


def test_setup_logger_warning_level():
    """Test that setup_logger sets the log level to WARNING when specified."""
    with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}, clear=True):
        logger = setup_logger()
        assert logger.level == logging.WARNING


@patch("google.auth.default", return_value=(None, "test_project_id"))
def test_get_config_default_values(mock_google_auth_default):
    """Test get_config with default environment variables."""
    with patch.dict(os.environ, {}, clear=True):  # Clear relevant env vars
        config = get_config()
        assert config.agent_name == "rickbot_agent"
        assert config.project_id == "test_project_id"
        assert config.location == "global"
        assert config.model == "gemini-2.5-flash"
        assert config.genai_use_vertexai is True


@patch("google.auth.default", return_value=(None, "custom_project"))
def test_get_config_custom_values(mock_google_auth_default):
    """Test get_config with custom environment variables."""
    env_vars = {
        "AGENT_NAME": "custom_agent",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "MODEL": "gemini-1.5-pro",
        "GOOGLE_GENAI_USE_VERTEXAI": "False",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        with patch('rickbot_agent.config.agent_name', new=env_vars["AGENT_NAME"]):
            config = get_config()
            assert config.agent_name == "custom_agent"
            assert config.project_id == "custom_project"
            assert config.location == "us-central1"
            assert config.model == "gemini-1.5-pro"
            assert config.genai_use_vertexai is False


@patch("google.auth.default", return_value=(None, "test_project_id"))
def test_get_config_vertexai_true_case_insensitive(mock_google_auth_default):
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
