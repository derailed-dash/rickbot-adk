"""This module defines the main agent for the Rickbot-ADK application.

It initializes a Google Gemini-powered agent with a specific personality (Rick)
and equips it with tools for interaction. The agent's behavior is determined
by a system instruction retrieved from the personality configuration.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.genai.types import GenerateContentConfig

from .config import get_config, logger
from .personality import personalities

# Load configuration
config = get_config()

# Get the Rick personality
rick_personality = personalities.get("Rick")

if rick_personality is None:
    raise ValueError("Rick personality not found.")

root_agent = Agent(
    name=config.agent_name,
    model=config.model,
    instruction=rick_personality.system_instruction,
    tools=[google_search],
    # generate_content_config=GenerateContentConfig(),
)
logger.debug("root_agent initialised.")
