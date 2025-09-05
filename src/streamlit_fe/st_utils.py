"""
This module contains utility functions for the Rickbot Streamlit application.
"""

from google.cloud import secretmanager
from limits import parse, storage
from limits.strategies import MovingWindowRateLimiter


def retrieve_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """
    Access the payload for the given secret version and return it.
    The calling service account must have the 'Secret Manager Secret Accessor' role.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload

class RateLimiter:
    """A simple rate limiter to prevent abuse."""

    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.limits_mem_store = storage.MemoryStorage()
        self.limiter = MovingWindowRateLimiter(self.limits_mem_store)
        self.limit = parse(f"{self.max_requests}/minute")

    def hit(self, key: str) -> bool:
        """Check if current request is within the rate limit.
        If so (i.e. limit not exceeded), increments and returns True.
        Otherwise returns False.
        """
        return self.limiter.hit(self.limit, key)
