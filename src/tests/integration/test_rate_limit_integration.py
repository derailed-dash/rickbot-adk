from fastapi.testclient import TestClient
from main import app
from slowapi.errors import RateLimitExceeded

client = TestClient(app)

def test_limiter_integration():
    # Verify limiter state is attached
    assert hasattr(app.state, "limiter")
    
    # Verify exception handler is registered
    # This is a bit internal to FastAPI, but we can check if the exception is in exception_handlers
    # Note: exception_handlers key might be the class or the status code.
    # SlowAPI registers handler for RateLimitExceeded
    assert RateLimitExceeded in app.exception_handlers or 429 in app.exception_handlers
