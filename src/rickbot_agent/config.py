"""Configure the Agent and Logging"""

import logging
import os
from dataclasses import dataclass

import google.auth

agent_name = os.environ.setdefault("AGENT_NAME", "rickbot_agent")


# Suppress verbose logging from ADK and GenAI libraries - INFO logging is quite verbose
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)

def setup_logger() -> logging.Logger:
    """Sets up and configures a logger for the application."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    app_logger = logging.getLogger(agent_name)
    log_level_num = getattr(logging, log_level, logging.INFO)
    app_logger.setLevel(log_level_num)
    app_logger.propagate = False  # Prevent messages from propagating to the root logger

    # Add a handler only if one doesn't exist to prevent duplicate logs
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d:%(name)s - %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        app_logger.addHandler(handler)

    app_logger.propagate = False # Prevent propagation to the root logger
    app_logger.info("Logger initialised.")
    app_logger.debug("DEBUG level logging enabled.")

    return app_logger

logger = setup_logger()

@dataclass
class Config:
    """Holds application configuration."""

    agent_name: str
    project_id: str
    location: str
    model: str
    genai_use_vertexai: bool

def get_config() -> Config:
    """Return a dictionary of the current config."""

    _, project_id = google.auth.default()
    location = os.environ.setdefault(
        "GOOGLE_CLOUD_LOCATION", "global"
    )  # assume set as env var, but fail back to global
    model = os.environ.setdefault("MODEL", "gemini-2.5-flash")
    genai_use_vertexai = (
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
    )

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
