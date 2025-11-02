"""Configure the Agent and Logging"""

import logging
import os
from dataclasses import dataclass
from functools import cache

import google.auth

from rickbot_utils.logging_utils import setup_logger

# Suppress verbose logging from ADK and GenAI libraries - INFO logging is quite verbose
logging.getLogger("google_adk").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)

agent_name = "rickbot_agent"
logger = setup_logger(agent_name)

@dataclass
class Config:
    """Holds application configuration."""

    agent_name: str
    project_id: str
    location: str
    model: str
    genai_use_vertexai: bool

@cache
def get_config() -> Config:
    """Return a dictionary of the current config."""

    _, project_id = google.auth.default()
    if not project_id:
        raise ValueError("GCP Project ID not set. Have you run scripts/setup-env.sh?")
    location = os.environ.setdefault(
        "GOOGLE_CLOUD_LOCATION", "global"
    )  # assume set as env var, but fail back to global
    model = os.environ.setdefault("MODEL", "gemini-2.5-flash")
    genai_use_vertexai = os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"

    logger.debug("agent_name set to %s", agent_name)
    logger.debug("project_id set to %s", project_id)
    logger.debug("location set to %s", location)
    logger.debug("model set to %s", model)
    logger.debug("genai_use_vertexai set to %s", genai_use_vertexai)

    return Config(
        agent_name=agent_name,
        project_id=project_id,
        location=location,
        model=model,
        genai_use_vertexai=genai_use_vertexai,
    )

config = get_config()
