"""This module defines the main agent for the Rickbot-ADK application.

It initializes a Google Gemini-powered agent with a specific personality (Rick)
and equips it with tools for interaction. The agent's behavior is determined
by a system instruction retrieved from the personality configuration.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search  # built-in Google Search tool
from google.genai.types import GenerateContentConfig

from .config import get_config, logger
from .personality import Personality, personalities

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
            temperature=personality.temperature, top_p=1, max_output_tokens=16384
        ),
    )

# Pre-load and cache all agents at startup
_agent_cache: dict[str, Agent] = {
    name: create_agent(p) for name, p in personalities.items()
}
logger.info(f"Pre-loaded and cached {len(_agent_cache)} agents.")

def get_agent(personality_name: str) -> Agent:
    """Retrieves a pre-configured agent from the cache."""
    agent = _agent_cache.get(personality_name)
    if not agent:
        logger.error(f"Agent for personality '{personality_name}' not found in cache.")
        # Fallback to Rick or raise an error
        rick_agent = _agent_cache.get("Rick")
        if not rick_agent:
            raise ValueError("Default 'Rick' personality agent not found.")
        return rick_agent
    return agent

# For backwards compatibility or direct access if needed, though get_agent is preferred.
root_agent = get_agent("Rick")
