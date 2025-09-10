"""
This module contains utility functions for the Rickbot Streamlit application.
"""

import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from limits import parse, storage
from limits.strategies import MovingWindowRateLimiter

from rickbot_agent.agent import get_agent
from rickbot_agent.personality import Personality
from streamlit_fe.st_config import config


async def initialize_adk_runner(personality: Personality) -> Runner:
    """Initialise the ADK runner with the correct agent personality."""
    rickbot_agent = get_agent(personality.name)

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=config.app_name,
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
    )
    return Runner(agent=rickbot_agent, app_name=config.app_name, session_service=session_service)


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
