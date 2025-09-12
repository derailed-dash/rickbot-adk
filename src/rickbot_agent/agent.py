"""
This module defines the main agent for the Rickbot-ADK application.
It initializes a set of Google Gemini-powered agent, each loaded from a specific personality.
We then cache these agents for fast retrieval.
"""

import functools

from google.adk.agents import Agent
from google.adk.tools import (
    AgentTool,
    # FunctionTool,
    google_search,  # built-in Google Search tool
)
from google.genai.types import GenerateContentConfig

from .config import get_config, logger
from .personality import Personality, get_personalities

config = get_config()

def test() -> str:
    """ Create a simple test message when asked to run a test """
    return "Testing 123"

search_agent = Agent(
    model=config.model,
    name="SearchAgent",
    description="Agent to perform Google Search",
    instruction="You're a specialist in Google Search",
    tools=[google_search],
)

# test_agent = Agent(
#     model = config.model,
#     name = "TestAgent",
#     instruction = "You execute when asked to test",
#     tools = [FunctionTool(func=test)],
# )

def create_agent(personality: Personality) -> Agent:
    """Creates and returns an agent with the given personality."""
    logger.debug(f"Creating agent for personality: {personality.name}")
    # Load configuration
    instruction = f"""{personality.system_instruction}
    If you don't know the answer to something, use the SearchAgent to perform a Google Search"""

    return Agent(
        name=f"{config.agent_name}_{personality.name}",  # Make agent name unique
        description=f"A chatbot with the personality of {personality.menu_name}",
        model=config.model,
        instruction=instruction,
        tools=[AgentTool(agent=search_agent)],
        generate_content_config=GenerateContentConfig(
            temperature=personality.temperature, top_p=1, max_output_tokens=8192
        ),
    )

@functools.cache
def _get_cached_agent_for_personality(personality: Personality) -> Agent:
    """
    Helper function to create and cache an agent for a given Personality object.
    This is where the actual caching happens.
    """
    logger.info(f"Lazily creating and caching agent for personality: {personality.name}")
    return create_agent(personality)

def get_agent(personality_name: str) -> Agent:
    """
    Retrieves a pre-configured agent from the cache, or creates it if not found.
    Agents are loaded lazily to improve startup performance.
    """
    personalities = get_personalities()
    personality = personalities.get(personality_name)

    if not personality:
        logger.error(f"Personality '{personality_name}' not found. Falling back to 'Rick'.")
        personality = personalities.get("Rick")
        if not personality:
            raise ValueError("Default 'Rick' personality not found. Cannot initialize agent.")

    # Call the cached helper function
    return _get_cached_agent_for_personality(personality)

# For backwards compatibility or direct access if needed, though get_agent is preferred.
root_agent = get_agent("Rick")
