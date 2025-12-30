import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from google.adk.artifacts import GcsArtifactService

from rickbot_agent.auth import verify_token
from rickbot_agent.auth_models import AuthUser
from rickbot_agent.services import get_artifact_service
from rickbot_utils.config import get_config
from src.main import app

# Create a dummy Part class for Pydantic if needed, 
# but here we rely on standard ADK types if possible, or mocks.

@pytest.fixture
def mock_gcs_env():
    """Sets ARTIFACT_BUCKET and clears caches to force GCS service creation."""
    with patch.dict(os.environ, {"ARTIFACT_BUCKET": "test-bucket"}):
        get_config.cache_clear()
        get_artifact_service.cache_clear()

        # Ensure services.py sees the new config
        new_config = get_config()
        with patch("rickbot_agent.services.config", new_config):
            yield

        get_config.cache_clear()
        get_artifact_service.cache_clear()

@pytest.fixture
def mock_gcs_client():
    """Mocks the google.cloud.storage.Client to avoid real network calls."""
    with patch("google.cloud.storage.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_bucket.get_blob.return_value = mock_blob


        # Setup specific behaviors
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b"GCS Content"
        mock_blob.download_as_text.return_value = "GCS Content"
        mock_blob.download_as_string.return_value = b"GCS Content"
        mock_blob.content_type = "text/plain"
        mock_blob.size = 100
        mock_blob.metadata = {}

        # Important: _load_artifact calls _list_versions which calls list_blobs
        # We must ensure list_blobs returns something valid to parse a version
        # Expected format: {app_name}/{user_id}/user/{filename}/{version}
        mock_blob.name = "rickbot_api/test@example.com/user/user:test_upload.txt/0"
        mock_client.list_blobs.return_value = [mock_blob]

        yield mock_client, mock_bucket, mock_blob

def test_gcs_configuration_and_usage(mock_gcs_env, mock_gcs_client):
    """
    Verifies that:
    1. Setting ARTIFACT_BUCKET causes get_artifact_service to return GcsArtifactService.
    2. Uploading a file calls the GCS upload methods.
    3. Retrieving a file calls the GCS download methods.
    """
    _, _, mock_blob = mock_gcs_client

    # 1. Verify Service Creation
    # This call should create a GcsArtifactService because env var is set
    # And it should trigger storage.Client() which is mocked.
    service = get_artifact_service()
    assert isinstance(service, GcsArtifactService)
    # Internal client check removed to avoid implementation details dependency

    # 2. Patch the app's artifact_service
    # main.py might have already initialized a service. We override it.
    with patch("src.main.artifact_service", service), \
         patch("src.main.Runner"): # Mock Runner to skip Agent logic

        # Mock Auth
        mock_user = AuthUser(id="test_id", email="test@example.com", name="Test User", provider="mock")
        app.dependency_overrides[verify_token] = lambda: mock_user

        client = TestClient(app)

        # --- TEST UPLOAD ---
        filename = "test_upload.txt"
        file_content = b"Content for GCS"

        response = client.post(
            "/chat",
            data={"prompt": "Save this", "personality": "Rick"},
            files={"files": (filename, file_content, "text/plain")}
        )
        assert response.status_code == 200

        # Verify GCS interaction
        # The ADK GcsArtifactService calls bucket.blob(blob_name).upload_from_file(...)
        # Check if any upload method was called on the blob
        assert mock_blob.upload_from_file.called or mock_blob.upload_from_string.called

        # --- TEST RETRIEVAL ---
        # The filename in the service is usually scoped: "user:test_upload.txt"
        get_response = client.get(f"/artifacts/{filename}")
        assert get_response.status_code == 200
        assert get_response.content == b"GCS Content" # Matched the mock

        # Verify GCS interaction
        assert mock_blob.download_as_bytes.called

    # Clean up overrides
    app.dependency_overrides = {}
