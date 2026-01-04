"""Unit tests for the updated Personality model with generic file search store support."""

import os
from unittest.mock import patch

import pytest

from rickbot_agent.personality import Personality


@pytest.fixture(autouse=True)
def mock_env_test_mode():
    """Ensure we are in test mode to avoid secret manager calls."""
    with patch.dict(os.environ, {"RICKBOT_TEST_MODE": "true", "GOOGLE_CLOUD_PROJECT": "test-project"}):
        yield


@patch("os.path.exists", return_value=False)
def test_personality_model_has_optional_file_search_store_id(mock_exists):
    """Test that Personality accepts an optional file_search_store_id."""

    # Case 1: Without file_search_store_id (default behavior)
    p1 = Personality(
        name="Rick",
        menu_name="Rick Sanchez",
        title="Rick Sanchez",
        overview="The smartest man in the universe.",
        welcome="Welcome to the Rick Zone!",
        prompt_question="What's up, Morty?",
        temperature=0.7,
    )
    # This should default to None (or empty string if we chose that, but spec says None or empty)
    # The dataclass field default check will be implicit if instantiation succeeds without it.
    assert not hasattr(p1, "file_search_store_id") or p1.file_search_store_id is None

    # Case 2: With file_search_store_id
    p2 = Personality(
        name="Dazbo",
        menu_name="Dazbo",
        title="I'm Dazbot.",
        overview="Geeky architect.",
        welcome="Hello.",
        prompt_question="Query?",
        temperature=0.5,
        file_search_store_id="projects/123/locations/us/stores/abc",
        file_search_instruction="Search your heart.",
    )
    assert p2.file_search_store_id == "projects/123/locations/us/stores/abc"
    assert p2.file_search_instruction == "Search your heart."
