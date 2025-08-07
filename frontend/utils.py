"""
This module contains utility functions for the Rickbot Streamlit application.
"""

import time
from collections import deque


class RateLimiter:
    """A simple rate limiter to prevent abuse."""

    def __init__(self, max_requests: int, period_seconds: int):
        self.requests = deque()
        self.max_requests = max_requests
        self.period_seconds = period_seconds

    def hit(self, rate_limit: str | None, key: str) -> bool:
        """
        Records a hit and checks if the rate limit has been exceeded.
        """
        if not rate_limit:
            return True

        # Parse the rate limit string (e.g., "5/60" -> 5 requests per 60 seconds)
        try:
            max_requests, period_seconds = map(int, rate_limit.split("/"))
            self.max_requests = max_requests
            self.period_seconds = period_seconds
        except ValueError:
            # Invalid format, so no rate limiting is applied
            return True

        # Record the current timestamp
        self.requests.append(time.time())

        # Remove timestamps older than the period
        while self.requests and self.requests[0] < time.time() - self.period_seconds:
            self.requests.popleft()

        # Check if the number of requests exceeds the limit
        return len(self.requests) <= self.max_requests