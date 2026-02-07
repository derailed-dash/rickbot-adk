import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, verify_token
from rickbot_agent.auth_models import AuthUser

client = TestClient(app)

def test_get_personas_syncs_metadata():
    mock_user = AuthUser(id="sync-user", email="sync@example.com", name="Sync User", provider="mock")
    
    # Use dependency_overrides for FastAPI dependencies
    app.dependency_overrides[verify_token] = lambda: mock_user
    
    try:
        with patch("rickbot_agent.services.sync_user_metadata") as mock_sync, \
             patch("main.get_personalities", return_value={}):
            
            # The token value doesn't matter now as it's overridden
            response = client.get("/personas", headers={"Authorization": "Bearer any-token"})
            
            assert response.status_code == 200
            mock_sync.assert_called_once_with("sync-user", "mock", "sync@example.com", "Sync User")
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()