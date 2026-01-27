from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_rate_limit_key(request: Request) -> str:
    """
    Returns the key for rate limiting.
    - If user is authenticated (request.state.user exists), returns user ID.
    - Otherwise, returns the IP address.
    """
    try:
        if hasattr(request.state, "user") and request.state.user:
             return str(request.state.user.id)
    except AttributeError:
        pass

    # Fallback to IP
    return get_remote_address(request)

# Initialize the Limiter with our custom key function and global default limits
# We keep headers_enabled=False (default) to avoid crashes with Pydantic model returns.
# We will handle custom headers (like Retry-After) in the exception handler.
try:
    limiter = Limiter(
        key_func=get_rate_limit_key,
        default_limits=["60 per minute"]
    )
except UnicodeDecodeError:
    # This can happen in CI/CD where .env is encrypted (git-crypt) and thus invalid utf-8.
    # In this case, we initialize without reading the config file.
    limiter = Limiter(
        key_func=get_rate_limit_key,
        default_limits=["60 per minute"],
        config_filename=""
    )
