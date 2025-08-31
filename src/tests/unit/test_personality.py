"""Unit tests for the rickbot_agent.personality module.

This test suite covers the functionality of the Personality class and its related
functions. It ensures that personalities are correctly loaded and initialized
from different sources, including local files and Google Secret Manager.

The tests cover the following scenarios:
- Correctly constructing avatar paths.
- Initializing a Personality by fetching the system instruction from Google
  Secret Manager when a local file is not present.
- Initializing a Personality by loading the system instruction from a local
  file when it exists.
- Handling errors when the required GOOGLE_CLOUD_PROJECT environment variable
  is not set for Secret Manager access.
- Handling exceptions that occur during the retrieval of secrets from
  Secret Manager.
- Loading and parsing personality data from a YAML configuration file.
- Caching the loaded personalities to avoid redundant file I/O and API calls.

Fixtures are used to create a temporary test directory and mock the
`personalities.yaml` file, ensuring that the tests run in an isolated
environment. The `unittest.mock` library is used extensively to patch
dependencies and simulate different conditions, such as the existence of
files or the behavior of external services like Secret Manager.
"""

import os
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from rickbot_agent.personality import Personality, _load_personalities, get_avatar, get_personalities

# Define a dummy path for testing purposes
TEST_SCRIPT_DIR = Path("/tmp/test_rickbot_agent")

@pytest.fixture(autouse=True)
def mock_script_dir():
    """Mocks SCRIPT_DIR to a temporary directory for testing."""
    with patch('rickbot_agent.personality.SCRIPT_DIR', TEST_SCRIPT_DIR):
        yield

@pytest.fixture
def mock_personalities_yaml():
    """Creates a mock personalities.yaml file for testing."""
    yaml_content = """
    - name: Rick
      menu_name: Rick Sanchez
      title: Rick Sanchez
      overview: The smartest man in the universe.
      welcome: Welcome to the Rick Zone!
      prompt_question: What's up, Morty?
      temperature: 0.7
    - name: Yoda
      menu_name: Master Yoda
      title: Grand Master Yoda
      overview: A wise and powerful Jedi Master.
      welcome: Welcome, young Padawan.
      prompt_question: Seek wisdom, you do?
      temperature: 0.5
    """
    (TEST_SCRIPT_DIR / "data").mkdir(parents=True, exist_ok=True)
    with open(TEST_SCRIPT_DIR / "data/personalities.yaml", "w") as f:
        f.write(yaml_content)
    yield
    # Clean up
    import shutil
    if TEST_SCRIPT_DIR.exists():
        shutil.rmtree(TEST_SCRIPT_DIR)

def test_get_avatar():
    """Tests that get_avatar returns the correct path."""
    expected_path = str(TEST_SCRIPT_DIR / "media/rick.png")
    assert get_avatar("rick") == expected_path

@patch('rickbot_agent.personality.retrieve_secret')
@patch('os.path.exists', return_value=False) # Simulate no local file
@patch('builtins.open', new_callable=mock_open) # Mock open to prevent file access
def test_personality_from_secret_manager(mock_open_file, mock_exists, mock_retrieve_secret):
    """Tests Personality initialization when system_instruction comes from Secret Manager."""
    mock_retrieve_secret.return_value = "System instruction from Secret Manager."
    with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
        personality = Personality(
            name="Rick",
            menu_name="Rick Sanchez",
            title="Rick Sanchez",
            overview="The smartest man in the universe.",
            welcome="Welcome to the Rick Zone!",
            prompt_question="What's up, Morty?",
            temperature=0.7
        )
        assert personality.system_instruction == "System instruction from Secret Manager."
        mock_retrieve_secret.assert_called_once_with("test-project", "rick-system-prompt")
        assert personality.avatar == str(TEST_SCRIPT_DIR / "media/rick.png")

@patch('os.path.exists', return_value=True) # Simulate local file exists
@patch('builtins.open', new_callable=mock_open, read_data="System instruction from local file.")
def test_personality_from_local_file(mock_open_file, mock_exists):
    """Tests Personality initialization when system_instruction comes from a local file."""
    personality = Personality(
        name="Yoda",
        menu_name="Master Yoda",
        title="Grand Master Yoda",
        overview="A wise and powerful Jedi Master.",
        welcome="Welcome, young Padawan.",
        prompt_question="Seek wisdom, you do?",
        temperature=0.5
    )
    assert personality.system_instruction == "System instruction from local file."
    mock_open_file.assert_called_once_with(TEST_SCRIPT_DIR / "data/system_prompts/yoda.txt", encoding="utf-8")
    assert personality.avatar == str(TEST_SCRIPT_DIR / "media/yoda.png")

@patch('os.path.exists', return_value=False)
@patch('builtins.open', new_callable=mock_open)
def test_personality_no_google_project_env_var(mock_open_file, mock_exists):
    """Tests ValueError when GOOGLE_CLOUD_PROJECT is not set and local file is not found."""
    with patch.dict(os.environ, {}, clear=True): # Ensure GOOGLE_CLOUD_PROJECT is not set
        with pytest.raises(ValueError, match="GOOGLE_CLOUD_PROJECT environment variable not set"):
            Personality(
                name="Rick",
                menu_name="Rick Sanchez",
                title="Rick Sanchez",
                overview="The smartest man in the universe.",
                welcome="Welcome to the Rick Zone!",
                prompt_question="What's up, Morty?",
                temperature=0.7
            )

@patch('rickbot_agent.personality.retrieve_secret', side_effect=Exception("Secret Manager error"))
@patch('os.path.exists', return_value=False)
@patch('builtins.open', new_callable=mock_open)
def test_personality_secret_retrieval_exception(mock_open_file, mock_exists, mock_retrieve_secret):
    """Tests ValueError when an exception occurs during Secret Manager retrieval."""
    with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
        with pytest.raises(ValueError, match="could not access 'rick-system-prompt' from Secret Manager"):
            Personality(
                name="Rick",
                menu_name="Rick Sanchez",
                title="Rick Sanchez",
                overview="The smartest man in the universe.",
                welcome="Welcome to the Rick Zone!",
                prompt_question="What's up, Morty?",
                temperature=0.7
            )

@patch('rickbot_agent.personality.retrieve_secret', return_value="Mocked secret content")
@patch('os.path.exists', return_value=False) # Ensure it tries to get from secret manager
def test_load_personalities(mock_personalities_yaml, mock_exists):
    """Tests _load_personalities function."""
    # Mock builtins.open to provide the YAML content directly
    mock_yaml_content = """
- name: Rick
  menu_name: Rick Sanchez
  title: Rick Sanchez
  overview: The smartest man in the universe.
  welcome: Welcome to the Rick Zone!
  prompt_question: What's up, Morty?
  temperature: 0.7
- name: Yoda
  menu_name: Master Yoda
  title: Grand Master Yoda
  overview: A wise and powerful Jedi Master.
  welcome: Welcome, young Padawan.
  prompt_question: Seek wisdom, you do?
  temperature: 0.5
"""
    with patch('builtins.open', mock_open(read_data=mock_yaml_content)) as mocked_file_open:
        personalities = _load_personalities(str(TEST_SCRIPT_DIR / "data/personalities.yaml")) # Path doesn't matter much now
        assert "Rick" in personalities
        assert "Yoda" in personalities
        assert personalities["Rick"].name == "Rick"
        assert personalities["Yoda"].menu_name == "Master Yoda"
        assert personalities["Rick"].temperature == 0.7
        assert personalities["Yoda"].temperature == 0.5
        mocked_file_open.assert_called_once_with(str(TEST_SCRIPT_DIR / "data/personalities.yaml"), encoding="utf-8")

@patch('rickbot_agent.personality._load_personalities')
def test_get_personalities_caching(mock_load_personalities):
    """Tests that get_personalities loads and caches personalities."""
    # Clear the cache before running the test
    get_personalities.cache_clear()

    mock_load_personalities.return_value = {"Test": "PersonalityObject"}

    # First call should load
    personalities1 = get_personalities()
    mock_load_personalities.assert_called_once()

    # Second call should use cache
    personalities2 = get_personalities()
    mock_load_personalities.assert_called_once() # Still only called once

    assert personalities1 == personalities2
    assert personalities1["Test"] == "PersonalityObject"

