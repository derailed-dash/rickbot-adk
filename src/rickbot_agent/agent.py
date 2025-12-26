"""
This module defines the main agent for the Rickbot-ADK application.
It initializes a set of Google Gemini-powered agent, each loaded from a specific personality.
We then cache these agents for fast retrieval.
"""

import functools

from google.adk.agents import Agent
from google.adk.tools import (
    AgentTool,
    FunctionTool,  # noqa: F401
    google_search,  # built-in Google Search tool
)
from google.genai.types import GenerateContentConfig

from rickbot_utils.config import config, logger

from .personality import Personality, get_personalities

# ADK Built-in Tool Limitation:
# A single root agent or a standalone agent can only support ONE built-in tool.
# See here: https://google.github.io/adk-docs/tools/built-in-tools/#use-built-in-tools-with-other-tools
# It cannot use other tools (custom or built-in) simultaneously within the same agent.
# To combine multiple built-in tools or use built-in tools with other custom tools,
# we should define an agent to wrap the built-in tool. This is the Agent-as-a-Tool pattern.
# Note: agent-as-tool receives only necessary input, whereas a sub-agent can access the complete session context.
search_agent = Agent(
    model=config.model,
    name="SearchAgent",
    description="Agent to perform Google Search",
    instruction="You're a specialist in Google Search",
    tools=[google_search],
)


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
        generate_content_config=GenerateContentConfig(temperature=personality.temperature, top_p=1, max_output_tokens=8192),
        output_key="last_turn_response",
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
# root_agent = get_agent("Rick") # REMOVED to avoid side-effects at import time
