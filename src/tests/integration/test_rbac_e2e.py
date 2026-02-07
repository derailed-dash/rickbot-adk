"""
Integration tests for Role-Based Access Control (RBAC) in Rickbot-ADK.
This verifies the full flow from Middleware -> Firestore -> Response.
"""

import os
import subprocess
import threading
import time
from collections.abc import Iterator
from typing import Any

import pytest
import requests
from requests.exceptions import RequestException

from rickbot_utils.logging_utils import setup_logger

# Configure logging
logger = setup_logger(__name__)

PORT = 8005 # Use a different port to avoid conflicts
BASE_URL = f"http://127.0.0.1:{PORT}"
STREAM_URL = f"{BASE_URL}/chat_stream"

def log_output(pipe: Any, log_func: Any) -> None:
    for line in iter(pipe.readline, ""):
        log_func(line.strip())

def start_server() -> subprocess.Popen[str]:
    command = [
        "uv",
        "run",
        "fastapi",
        "run",
        "src/main.py",
        "--port",
        str(PORT),
    ]
    env = os.environ.copy()
    env["RICKBOT_TEST_MODE"] = "true"
    env["BACKEND_ALLOW_MOCK_AUTH"] = "true"
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
        cwd=os.getcwd(),
    )

    threading.Thread(target=log_output, args=(process.stdout, logger.info), daemon=True).start()
    threading.Thread(target=log_output, args=(process.stderr, logger.error), daemon=True).start()

    return process

def wait_for_server(timeout: int = 60, interval: int = 1) -> bool:
    start_time = time.time()
    health_check_url = BASE_URL + "/"
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_check_url, timeout=5)
            if response.status_code == 200:
                return True
        except RequestException:
            pass
        time.sleep(interval)
    return False

@pytest.fixture(scope="module")
def rbac_server():
    process = start_server()
    if not wait_for_server():
        process.terminate()
        pytest.fail("Server failed to start")
    yield process
    process.terminate()
    process.wait()

def test_standard_user_cannot_access_supporter_persona(rbac_server):
    """
    Verify that a 'standard' user (id: test-standard-user) 
    cannot access a 'supporter' persona (id: yasmin).
    """
    from google.cloud import firestore
    db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    # Seed required data for the test
    db.collection("persona_tiers").document("yasmin").set({"required_role": "supporter"})
    db.collection("users").document("StandardUser:mock:test-standard-user").set({
        "id": "test-standard-user",
        "provider": "mock",
        "name": "StandardUser",
        "role": "standard",
        "email": "standard@example.com"
    })

    # Note: verify_credentials in mock mode parses id from token: mock:<id>:<email>:<name>
    headers = {"Authorization": "Bearer mock:test-standard-user:standard@example.com:StandardUser"}
    data = {"prompt": "Hello", "personality": "Yasmin"}

    response = requests.post(STREAM_URL, data=data, headers=headers)
    
    assert response.status_code == 403
    json_resp = response.json()
    assert json_resp["error_code"] == "UPGRADE_REQUIRED"
    assert "Yasmin" in json_resp["detail"]

def test_supporter_user_can_access_supporter_persona(rbac_server):
    """
    Verify that a 'supporter' user (id: derailed-dash)
    can access a 'supporter' persona (id: yasmin).
    """
    from google.cloud import firestore
    db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    db.collection("users").document("Dazbo:mock:derailed-dash").set({
        "id": "derailed-dash",
        "provider": "mock",
        "name": "Dazbo",
        "role": "supporter",
        "email": "dazbo@example.com"
    })

    headers = {"Authorization": "Bearer mock:derailed-dash:dazbo@example.com:Dazbo"}
    data = {"prompt": "Hello", "personality": "Yasmin"}

    response = requests.post(STREAM_URL, data=data, headers=headers)
    
    # Yasmin is a supporter persona, should return 200
    assert response.status_code == 200

def test_standard_user_can_access_standard_persona(rbac_server):
    """
    Verify that a 'standard' user can access a 'standard' persona.
    """
    headers = {"Authorization": "Bearer mock:test-standard-user:standard@example.com:StandardUser"}
    data = {"prompt": "Hello", "personality": "Rick"}

    response = requests.post(STREAM_URL, data=data, headers=headers)
    
    assert response.status_code == 200

def test_dynamic_tier_update(rbac_server):
    """
    Verify that changing a persona's required role in Firestore 
    is reflected immediately without server restart.
    """
    from google.cloud import firestore
    db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    doc_ref = db.collection("persona_tiers").document("rick")
    
    try:
        # 1. Initially Rick is standard (verified in previous test)
        
        # 2. Change Rick to supporter
        doc_ref.update({"required_role": "supporter"})
        time.sleep(1) # Small delay for Firestore consistency
        
        headers = {"Authorization": "Bearer mock:test-standard-user:standard@example.com:StandardUser"}
        data = {"prompt": "Hello", "personality": "Rick"}
        
        response = requests.post(STREAM_URL, data=data, headers=headers)
        assert response.status_code == 403
        assert response.json()["error_code"] == "UPGRADE_REQUIRED"
        
    finally:
        # 3. Restore Rick to standard
        doc_ref.update({"required_role": "standard"})
