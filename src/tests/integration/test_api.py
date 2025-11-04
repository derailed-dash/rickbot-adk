"""Integration Tests for the Rickbot-ADK FastAPI Application.

Summary:
    This module contains integration tests for the FastAPI application defined
    in `src/main.py`. It focuses on verifying the behavior of the API endpoints,
    particularly the `/chat` endpoint.

Purpose:
    The purpose of these tests is to ensure that the API layer correctly handles
    incoming requests, interacts with the underlying services (in a mocked capacity),
    and formats responses as expected. It validates the API contract, including
    request/response models, status codes, and basic data flow.

Module/Functionality Being Tested:
    - The `/chat` POST endpoint in `src/main.py`.
    - FastAPI's request parsing, dependency injection, and response handling.
    - Pydantic model validation for `ChatRequest` and `ChatResponse`.

Preconditions & Mocking:
    - These tests use FastAPI's `TestClient` to send simulated HTTP requests
      to the application without needing a live running server.
    - The ADK `Runner` (`src.main.Runner`) is mocked using `unittest.mock.patch`
      for simple, isolated unit tests. For the multi-turn integration test,
      no mocking is used to ensure the session history is truly maintained.

Expected Outcomes:
    - Successful requests to `/chat` should return a 200 OK status code and a
      JSON payload matching the `ChatResponse` model.
    - Requests with invalid or missing data should return appropriate HTTP
      error codes (e.g., 422 Unprocessable Entity).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import tenacity
from fastapi.testclient import TestClient
from google.genai import errors

from src.main import app

client = TestClient(app)


class MockEvent:
    """A mock for the ADK's Event object."""

    def __init__(self, text: str, is_final: bool = False):
        self.text = text
        self._is_final = is_final
        self.content = MagicMock()
        self.content.parts = [MagicMock()]
        self.content.parts[0].text = self.text
        self.actions = None

    def is_final_response(self) -> bool:
        """Check if this is the final response."""
        return self._is_final

    def get_function_calls(self) -> list:
        """Return a list of function calls."""
        return []


@patch("src.main.Runner")
def test_chat_endpoint_success(MockRunner):
    """Test the /chat endpoint for a successful text-only request."""
    # Configure the mock runner to return a mock event stream
    mock_runner_instance = MockRunner.return_value
    mock_event = MockEvent("Test response from Rick", is_final=True)

    async def mock_event_stream(*args, **kwargs):
        yield mock_event

    mock_runner_instance.run_async = mock_event_stream

    # Mock the session service to simulate a new session
    with patch("src.main.session_service") as mock_session_service:
        mock_session_service.get_session = AsyncMock(return_value=None)
        mock_session_service.create_session = AsyncMock()

        # Make the request to the API
        response = client.post(
            "/chat",
            data={"prompt": "Hello", "personality": "Rick"},
        )

        # Assert the response
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["response"] == "Test response from Rick"
        assert "session_id" in json_response


@pytest.mark.asyncio
@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type(errors.ClientError),
)
async def test_chat_endpoint_multiturn_integration():
    """Tests the API for a real multi-turn conversation, ensuring session history is maintained."""
    # --- Turn 1: Introduce name ---
    response1 = client.post(
        "/chat",
        data={"prompt": "Hi, my name is Dazbo.", "personality": "Rick"},
    )
    assert response1.status_code == 200
    json_response1 = response1.json()
    session_id = json_response1["session_id"]
    assert session_id is not None

    # --- Turn 2: Recall name ---
    response2 = client.post(
        "/chat",
        data={
            "prompt": "What is my name?",
            "personality": "Rick",
            "session_id": session_id,
        },
    )
    assert response2.status_code == 200
    json_response2 = response2.json()
    # Assert that the real agent response contains the name
    assert "dazbo" in json_response2["response"].lower()
