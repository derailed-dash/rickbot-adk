"""Unit tests for the utils.logging_utils module."""

import logging
import os
from unittest.mock import patch

import pytest

from rickbot_utils.logging_utils import setup_logger


@pytest.fixture(autouse=True)
def clear_logger_handlers():
    """Fixture to clear logger handlers before each test to prevent duplicate logs."""
    for handler in logging.getLogger("test_app").handlers[:]:
        logging.getLogger("test_app").removeHandler(handler)
    yield


def test_setup_logger_default_level() -> None:
    """Test that setup_logger sets the default log level to INFO."""
    setup_logger.cache_clear()
    with patch.dict(os.environ, {}, clear=True):  # Ensure no LOG_LEVEL is set
        logger = setup_logger("test_app")
        assert logger.level == logging.INFO
        assert logger.name == "test_app"
        assert len(logger.handlers) > 0


def test_setup_logger_debug_level() -> None:
    """Test that setup_logger sets the log level to DEBUG when specified."""
    setup_logger.cache_clear()
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=True):
        logger = setup_logger("test_app")
        assert logger.level == logging.DEBUG


def test_setup_logger_warning_level() -> None:
    """Test that setup_logger sets the log level to WARNING when specified."""
    setup_logger.cache_clear()
    with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}, clear=True):
        logger = setup_logger("test_app")
        assert logger.level == logging.WARNING
