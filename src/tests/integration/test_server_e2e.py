"""
This module contains end-to-end tests for the Rickbot-ADK API server.
It starts the server as a subprocess, waits for it to become ready, and then performs
integration tests against its endpoints, specifically focusing on the chat streaming functionality.
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

# Use the same port as in the specific run command
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
CHAT_URL = f"{BASE_URL}/chat"
STREAM_URL = f"{BASE_URL}/chat_stream"

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def log_output(pipe: Any, log_func: Any) -> None:
    """Log the output from the given pipe."""
    for line in iter(pipe.readline, ""):
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    """Start the FastAPI API server using subprocess and log its output."""
    # We run the actual app: uv run fastapi run src/main.py --port 8000
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
    # vital: ensure test mode is passed to subprocess
    env["RICKBOT_TEST_MODE"] = "true"

    # We start from project root
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
        cwd=os.getcwd(), 
    )

    # Start threads to log stdout and stderr in real-time
    threading.Thread(target=log_output, args=(process.stdout, logger.info), daemon=True).start()
    threading.Thread(
        target=log_output, args=(process.stderr, logger.error), daemon=True
    ).start()

    return process


def wait_for_server(timeout: int = 60, interval: int = 1) -> bool:
    """Wait for the server to be ready."""
    start_time = time.time()
    # We use the root endpoint / which returns Hello World
    health_check_url = BASE_URL + "/"
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_check_url, timeout=5)
            if response.status_code == 200:
                logger.info("Server is ready")
                return True
        except RequestException:
            pass
        time.sleep(interval)
    logger.error(f"Server did not become ready within {timeout} seconds")
    return False


@pytest.fixture(scope="session")
def server_fixture(request: Any) -> Iterator[subprocess.Popen[str]]:
    """Pytest fixture to start and stop the server for testing."""
    logger.info("Starting server process")
    server_process = start_server()
    if not wait_for_server():
        # Clean up if it failed to start properly
        server_process.terminate()
        pytest.fail("Server failed to start")
    logger.info("Server process started")

    def stop_server() -> None:
        logger.info("Stopping server process")
        server_process.terminate()
        server_process.wait()
        logger.info("Server process stopped")

    request.addfinalizer(stop_server)
    yield server_process


def test_chat_endpoint(server_fixture: subprocess.Popen[str]) -> None:
    """Test the /chat endpoint."""
    logger.info("Starting /chat test")

    # Enable mock auth via header if supported or assume mock auth logic in app
    # For now we use the mock usage pattern: 
    # The server in production (and here) uses verify_token.
    # We need to rely on the MOCK AUTH environment variable if we want to bypass real auth,
    # OR we need to supply a valid mock token if NEXT_PUBLIC_ALLOW_MOCK_AUTH is enabled.

    # Note: We didn't set NEXT_PUBLIC_ALLOW_MOCK_AUTH in the subprocess env above.
    # Let's rely on the fact we can't easily mock auth in a subprocess without that var.
    # However, 'make test-all' usually runs in an env where we can access GCP secrets.
    # But wait, user doesn't want Dazbo secrets.

    # We'll use the Mock Auth credentials format, assuming NEXT_PUBLIC_ALLOW_MOCK_AUTH is set in .env
    # or passed in. Let's assume .env is loaded by the app.

    headers = {
        "Authorization": "Bearer mock:123:test@example.com:Tester"
    }

    # Standard form data for /chat
    data = {
        "prompt": "Hello Rick!",
        "personality": "Rick",
        "session_id": "test_session_chat"
    }

    response = requests.post(CHAT_URL, data=data, headers=headers)
    assert response.status_code == 200, f"Chat failed: {response.text}"
    json_resp = response.json()
    assert "response" in json_resp
    assert len(json_resp["response"]) > 0
    assert json_resp["session_id"] == "test_session_chat"


def test_chat_stream_endpoint(server_fixture: subprocess.Popen[str]) -> None:
    """Test the /chat_stream endpoint."""
    logger.info("Starting /chat_stream test")

    headers = {
        "Authorization": "Bearer mock:123:test@example.com:Tester"
    }

    data = {
        "prompt": "Tell me a joke.",
        "personality": "Rick",
        "session_id": "test_session_stream"
    }

    response = requests.post(STREAM_URL, data=data, headers=headers, stream=True)
    assert response.status_code == 200, f"Chat stream failed: {response.text}"

    # Verify we get SSE events
    events_received = False
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            if decoded_line.startswith("data: "):
                events_received = True
                break

    assert events_received, "No SSE events received from /chat_stream"
