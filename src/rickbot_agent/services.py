"""This module contains service initialisation functions for the Rickbot agent."""

from functools import cache

from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.sessions import BaseSessionService, InMemorySessionService


@cache
def get_artifact_service():
    """Initialise and return the artifact service."""
    return InMemoryArtifactService()

@cache
def get_session_service() -> BaseSessionService:
    """Initialise and return the session service.
    The session services creates sessions. """
    # For now, we'll use the in-memory service.
    # This can be expanded later to support persistent services.
    return InMemorySessionService()
