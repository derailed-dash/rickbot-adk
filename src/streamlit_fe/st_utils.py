"""
This module contains utility functions for the Rickbot Streamlit application.
"""

from limits import parse, storage
from limits.strategies import MovingWindowRateLimiter


class RateLimiter:
    """A simple rate limiter to prevent abuse."""

    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.limits_mem_store = storage.MemoryStorage()
        self.limiter = MovingWindowRateLimiter(self.limits_mem_store)
        self.limit = parse(f"{self.max_requests}/minute")

    def hit(self, key: str) -> bool:
        """ Check if current request is within the rate limit.
        If so (i.e. limit not exceeded), increments and returns True.
        Otherwise returns False.
        """
        return self.limiter.hit(self.limit, key)
