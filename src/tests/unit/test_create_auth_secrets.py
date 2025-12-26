"""
Unit tests for the `create_auth_secrets` module.

This test suite is designed to verify the functionality of the
`create_secrets_toml` function in `src/streamlit_fe/create_auth_secrets.py`.

The tests ensure that the function behaves correctly under various conditions,
without making any actual calls to external services (like Google Secret Manager)
or modifying the local filesystem. This is achieved by using Python's `unittest.mock`
library to patch and mock dependencies.

Key behaviors tested include:
- Verification that the secrets.toml file is created when it does not exist.
- Confirmation that the correct secret content is written to the file.
- Assurance that file/directory creation is skipped if secrets.toml already exists.
- Validation of error handling when fetching the secret from the external service fails.
"""

import os
from unittest.mock import mock_open, patch

import pytest
from streamlit.errors import StreamlitAPIException

from src.streamlit_fe.create_auth_secrets import create_secrets_toml


# Since the function is decorated with @st.cache_resource, we need to clear
# its cache before each test to ensure test isolation.
@pytest.fixture(autouse=True)
def clear_streamlit_cache() -> None:
    """
    A pytest fixture that automatically runs before each test in this module.
    It clears the cache for the `create_secrets_toml` function, ensuring
    that each test runs in a clean, isolated state.
    """
    try:
        create_secrets_toml.clear()
    except StreamlitAPIException:
        # This handles the case where the function might not have been called yet
        # or caching is not active in the test environment.
        pass


@patch("src.rickbot_utils.secret_utils.secretmanager.SecretManagerServiceClient")
@patch("os.path.exists")
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_create_secrets_toml_success(mock_file_open, mock_makedirs, mock_exists, mock_secret_manager_client) -> None:
    """
    Tests the successful creation of secrets.toml when it does not exist.
    """
    # Arrange: File does not exist, and the secret is successfully retrieved.
    mock_exists.return_value = False
    mock_secret_content = """[auth]
redirect_uri = "https://localhost:8501/oauth2callback"
cookie_secret = "some_random_secret"

[auth.google]
client_id = "some_client_id"
client_secret = "some_client_secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
"""
    # Configure the mock SecretManagerServiceClient
    mock_sm_client = mock_secret_manager_client.return_value
    access_response = mock_sm_client.access_secret_version.return_value
    access_response.payload.data.decode.return_value = mock_secret_content

    project_id = "test-project"
    secrets_file_path = os.path.join(".streamlit", "secrets.toml")

    # Act: Call the function to create the secrets file.
    create_secrets_toml(project_id)

    # Assert: Verify that the correct actions were taken.
    mock_exists.assert_any_call(secrets_file_path)
    mock_secret_manager_client.return_value.access_secret_version.assert_called_once_with(
        request={"name": f"projects/{project_id}/secrets/rickbot-streamlit-secrets-toml/versions/latest"}
    )
    mock_makedirs.assert_called_once_with(".streamlit", exist_ok=True)
    mock_file_open.assert_called_once_with(secrets_file_path, "w")
    mock_file_open().write.assert_called_once_with(mock_secret_content)


@patch("src.rickbot_utils.secret_utils.retrieve_secret")
@patch("os.path.exists")
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_create_secrets_toml_already_exists(mock_file_open, mock_makedirs, mock_exists, mock_retrieve_secret) -> None:
    """
    Tests that file creation is skipped if secrets.toml already exists.
    """
    # Arrange: The secrets.toml file already exists.
    mock_exists.return_value = True
    project_id = "test-project"
    secrets_file_path = os.path.join(".streamlit", "secrets.toml")

    # Act: Call the function.
    create_secrets_toml(project_id)

    # Assert: Verify that no file operations or secret retrievals were performed.
    mock_exists.assert_called_once_with(secrets_file_path)
    mock_retrieve_secret.assert_not_called()
    mock_makedirs.assert_not_called()
    mock_file_open.assert_not_called()


@patch("src.rickbot_utils.secret_utils.secretmanager.SecretManagerServiceClient")
@patch("os.path.exists")
def test_create_secrets_toml_retrieval_fails(mock_exists, mock_secret_manager_client) -> None:
    """
    Tests that a ValueError is raised if retrieving the secret fails.
    """
    # Arrange: File does not exist and the secret retrieval will raise an exception.
    mock_exists.return_value = False
    mock_secret_manager_client.return_value.access_secret_version.side_effect = Exception("Test secret retrieval error")
    project_id = "test-project"

    # Act & Assert: Verify that the specific ValueError is raised.
    with pytest.raises(ValueError) as excinfo:
        create_secrets_toml(project_id)

    assert "Error accessing secret" in str(excinfo.value)
    assert "Test secret retrieval error" in str(excinfo.value)
