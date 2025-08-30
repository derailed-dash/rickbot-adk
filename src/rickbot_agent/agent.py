"""
This module defines the main agent for the Rickbot-ADK application.
It initializes a set of Google Gemini-powered agent, each loaded from a specific personality.
We then cache these agents for fast retrieval.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search  # built-in Google Search tool
from google.genai.types import GenerateContentConfig

from .config import get_config, logger
from .personality import Personality, get_personalities

config = get_config()

def create_agent(personality: Personality) -> Agent:
    """Creates and returns an agent with the given personality."""
    logger.debug(f"Creating agent for personality: {personality.name}")
    # Load configuration

    return Agent(
        name=f"{config.agent_name}_{personality.name}",  # Make agent name unique
        description=f"A chatbot with the personality of {personality.menu_name}",
        model=config.model,
        instruction=personality.system_instruction,
        tools=[google_search],
        generate_content_config=GenerateContentConfig(
            temperature=personality.temperature, top_p=1, max_output_tokens=8192
        ),
    )

# Agent cache (initially empty, agents are loaded lazily)
_agent_cache: dict[str, Agent] = {}

def get_agent(personality_name: str) -> Agent:
    """
    Retrieves a pre-configured agent from the cache, or creates it if not found.
    Agents are loaded lazily to improve startup performance.
    """
    agent = _agent_cache.get(personality_name)
    if agent:
        return agent

    # If agent not in cache, create it
    personalities = get_personalities()
    personality = personalities.get(personality_name)

    if not personality:
        logger.error(f"Personality '{personality_name}' not found. Falling back to 'Rick'.")
        personality = personalities.get("Rick")
        if not personality:
            raise ValueError("Default 'Rick' personality not found. Cannot initialize agent.")
        personality_name = "Rick" # Update name to reflect fallback

    logger.info(f"Lazily creating and caching agent for personality: {personality_name}")
    agent = create_agent(personality)
    _agent_cache[personality_name] = agent
    return agent

# For backwards compatibility or direct access if needed, though get_agent is preferred.
root_agent = get_agent("Rick")
