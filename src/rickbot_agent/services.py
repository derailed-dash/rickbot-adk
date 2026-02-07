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
    Queries the 'users' collection for a document where the 'id' field matches.
    Defaults to 'standard' if the user is not found.
    """
    try:
        db = _get_firestore_client()
        # Query by the stable 'id' field
        logger.debug(f"Firestore Query: collection='users', where id == '{user_id}'")
        from google.cloud.firestore_v1.base_query import FieldFilter
        docs = db.collection("users").where(filter=FieldFilter("id", "==", user_id)).limit(1).get()
        
        if docs:
            role = docs[0].to_dict().get("role", "standard")
            logger.debug(f"Retrieved role '{role}' for user_id '{user_id}' from doc '{docs[0].id}'")
            return role
        else:
            logger.debug(f"No Firestore document found for user_id '{user_id}'")
    except Exception as e:
        logger.error(f"Error retrieving role for user_id '{user_id}': {e}")

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


def sync_user_metadata(user_id: str, email: str, name: str) -> None:
    """
    Ensures user metadata is up to date in Firestore.
    If the user doesn't exist (queried by 'id' field), creates a new document 
    with ID format: {id}_{name} for readability.
    """
    try:
        db = _get_firestore_client()
        from google.cloud.firestore_v1.base_query import FieldFilter
        docs = db.collection("users").where(filter=FieldFilter("id", "==", user_id)).limit(1).get()

        data = {
            "id": user_id,
            "email": email,
            "name": name,
            "last_logged_in": firestore.SERVER_TIMESTAMP
        }

        if docs:
            # Update existing document
            doc_ref = docs[0].reference
            doc_ref.update(data)
            logger.debug(f"Updated metadata for user {user_id}")
        else:
            # Create new document with readable ID
            # Clean name for ID use (alphanumeric only)
            safe_name = "".join(c for c in name if c.isalnum())
            doc_id = f"{user_id}_{safe_name}"
            data["role"] = "standard"
            db.collection("users").document(doc_id).set(data)
            logger.info(f"Created new user record: {doc_id}")
    except Exception as e:
        logger.error(f"Error syncing metadata for user {user_id}: {e}")
