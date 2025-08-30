"""
This module contains end-to-end tests for the Rickbot-ADK API server.
It starts the server as a subprocess, waits for it to become ready, and then performs
integration tests against its endpoints, specifically focusing on the chat streaming functionality.
"""
import json
import logging
import os
import subprocess
import threading
import time
from collections.abc import Iterator
from typing import Any

import pytest
import requests
from requests.exceptions import RequestException

# This module contains end-to-end tests for the Rickbot-ADK API server.
# It starts the server as a subprocess, waits for it to become ready, and then performs
# integration tests against its endpoints, specifically focusing on the chat streaming functionality.

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_NAME = "rickbot_agent"  # Use the correct agent name
BASE_URL = "http://127.0.0.1:8000/"
STREAM_URL = BASE_URL + "run_sse"

HEADERS = {"Content-Type": "application/json"}


def log_output(pipe: Any, log_func: Any) -> None:
    """Log the output from the given pipe."""
    for line in iter(pipe.readline, ""):
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    """Start the ADK API server using subprocess and log its output."""
    # Use the ADK CLI to start the server for the rickbot_agent
    command = [
        "uv",
        "run",
        "adk",
        "api_server",
        "src/rickbot_agent",
        "--port",
        "8000",
    ]
    env = os.environ.copy()
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    # Start threads to log stdout and stderr in real-time
    threading.Thread(
        target=log_output, args=(process.stdout, logger.info), daemon=True
    ).start()
    threading.Thread(
        target=log_output, args=(process.stderr, logger.error), daemon=True
    ).start()

    return process


def wait_for_server(timeout: int = 60, interval: int = 1) -> bool:
    """Wait for the server to be ready."""
    start_time = time.time()
    # The /list-apps endpoint is a reliable way to check if the ADK server is up
    health_check_url = BASE_URL + "list-apps"
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_check_url, timeout=10)
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
        pytest.fail("Server failed to start")
    logger.info("Server process started")

    def stop_server() -> None:
        logger.info("Stopping server process")
        server_process.terminate()
        server_process.wait()
        logger.info("Server process stopped")

    request.addfinalizer(stop_server)
    yield server_process


def test_chat_stream(server_fixture: subprocess.Popen[str]) -> None:
    """Test the chat stream functionality for the rickbot_agent."""
    logger.info("Starting chat stream test")

    # Create session first
    user_id = "test_user_123"
    session_data = {"state": {}}  # No specific state needed for this test

    session_url = f"{BASE_URL}/apps/{APP_NAME}/users/{user_id}/sessions"
    session_response = requests.post(
        session_url,
        headers=HEADERS,
        json=session_data,
        timeout=60,
    )
    assert session_response.status_code == 200
    logger.info(f"Session creation response: {session_response.json()}")
    session_id = session_response.json()["id"]

    # Then send chat message
    data = {
        "app_name": APP_NAME,
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": "Why is the sky blue?"}],
        },
        "run_config": {  # ADK server expects a run_config for streaming
            "streaming_mode": "STREAMING_MODE_SSE"
        },
    }

    response = requests.post(
        STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=60
    )
    assert response.status_code == 200

    # Parse SSE events from response
    events = []
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                event_json = line_str[6:]
                try:
                    event = json.loads(event_json)
                    events.append(event)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON: {event_json}")

    assert events, "No events received from stream"

    # Check for valid content in the response
    has_text_content = False
    for event in events:
        content = event.get("content")
        if (
            content is not None
            and content.get("parts")
            and any(part.get("text") for part in content["parts"])
        ):
            has_text_content = True
            break

    assert has_text_content, "Expected at least one message with text content"
