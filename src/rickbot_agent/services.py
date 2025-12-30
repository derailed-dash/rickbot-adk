"""This module contains service initialisation functions for the Rickbot agent."""

from functools import cache

from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.sessions import BaseSessionService, InMemorySessionService

from rickbot_utils.config import config
from rickbot_utils.logging_utils import setup_logger

logger = setup_logger(config.agent_name)


@cache
def get_artifact_service():
    """Initialise and return the artifact service. 
    Use GcsArtifactService only if artifact_bucket is set."""
    # use persistent artifact service if artifact_bucket is set
    if config.artifact_bucket:
        logger.info(f"Using GcsArtifactService with artifact bucket: {config.artifact_bucket}")
        return GcsArtifactService(config.artifact_bucket)

    logger.info("Using InMemoryArtifactService")
    return InMemoryArtifactService()


@cache
def get_session_service() -> BaseSessionService:
    """Initialise and return the session service.
    The session services creates sessions."""
    # For now, we'll use the in-memory service.
    # This can be expanded later to support persistent services.
    return InMemorySessionService()
