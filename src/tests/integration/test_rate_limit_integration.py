from fastapi.testclient import TestClient
from main import app
from slowapi.errors import RateLimitExceeded
import pytest
import os
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Ensure mock auth is enabled for testing
os.environ["NEXT_PUBLIC_ALLOW_MOCK_AUTH"] = "true"

def test_limiter_integration():
    # Verify limiter state is attached
    assert hasattr(app.state, "limiter")
    assert RateLimitExceeded in app.exception_handlers or 429 in app.exception_handlers

def test_global_rate_limit_applied():
    limiter = app.state.limiter
    assert len(limiter._default_limits) > 0

def test_root_endpoint_rate_limited():
    # Attempt to exhaust the 60/min limit on the root endpoint
    for _ in range(65):
        response = client.get("/")
        if response.status_code == 429:
            # Check for Retry-After header
            print(f"DEBUG: 429 response headers: {response.headers}")
            print(f"DEBUG: 429 response body: {response.json()}")
            assert "Retry-After" in response.headers
            return # Success, it's limited
    
    pytest.fail("Root endpoint was not rate limited after 65 requests")

@patch("main.Runner")
@patch("main.get_agent")
def test_chat_endpoint_stricter_limit(mock_get_agent, mock_runner_class):
    # Setup mock runner to return a dummy final response
    mock_runner = MagicMock()
    mock_runner_class.return_value = mock_runner
    
    async def mock_run_async(*args, **kwargs):
        event = MagicMock()
        event.get_function_calls.return_value = []
        event.actions = None
        event.is_final_response.return_value = True
        
        part = MagicMock()
        part.text = "Mocked response"
        event.content.parts = [part]
        
        yield event

    mock_runner.run_async = mock_run_async
    
    # The limit for /chat should be 5/minute
    headers = {"Authorization": "Bearer mock:user1:user1@example.com:User1"}
    data = {"prompt": "Hello", "personality": "Rick"}
    
    for i in range(10):
        response = client.post("/chat", data=data, headers=headers)
        if response.status_code == 429:
            assert i < 6 # Should fail at 6th request
            assert "Retry-After" in response.headers
            assert "detail" in response.json()
            return
            
    pytest.fail("Chat endpoint was not rate limited after 10 requests")
