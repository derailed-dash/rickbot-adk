"""This module contains service initialisation functions for the Rickbot agent."""

from functools import cache

from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.sessions import BaseSessionService, InMemorySessionService
from google.cloud import firestore  # type: ignore[attr-defined]

from rickbot_utils.config import config
from rickbot_utils.logging_utils import setup_logger

logger = setup_logger(config.agent_name)


@cache
def get_artifact_service():
    """Initialise and return the artifact service. Use GcsArtifactService if artifact_bucket is set."""

    if config.artifact_bucket:
        logger.info(f"Using GcsArtifactService with artifact bucket: {config.artifact_bucket}")
        return GcsArtifactService(config.artifact_bucket)

    logger.info("Using InMemoryArtifactService")
    return InMemoryArtifactService()


@cache
def get_session_service() -> BaseSessionService:
    """Initialise and return the session service. The session services creates sessions."""
    # For now, we'll use the in-memory service.
    # This can be expanded later to support persistent services.
    return InMemorySessionService()


@cache
def _get_firestore_client() -> firestore.Client:
    """Initialise and return the Firestore client."""
    return firestore.Client(project=config.project_id)


def get_user_role(user_id: str) -> str:
    """
    Retrieve the role for a given user from Firestore.
    Defaults to 'standard' if the user is not found.
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            role = doc.to_dict().get("role", "standard")
            logger.debug(f"Retrieved role '{role}' for user '{user_id}'")
            return role
    except Exception as e:
        logger.error(f"Error retrieving role for user '{user_id}': {e}")

    return "standard"


def get_required_role(persona_id: str) -> str:
    """
    Retrieve the required role for a given persona from Firestore.
    Defaults to 'standard' if the persona is not found.
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection("persona_tiers").document(persona_id.lower())
        doc = doc_ref.get()
        if doc.exists:
            required_role = doc.to_dict().get("required_role", "standard")
            logger.debug(f"Retrieved required role '{required_role}' for persona '{persona_id}'")
            return required_role
    except Exception as e:
        logger.error(f"Error retrieving required role for persona '{persona_id}': {e}")

    return "standard"
