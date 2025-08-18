"""Utility functions for Secret Management"""

from google.cloud import secretmanager


def retrieve_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """
    Access the payload for the given secret version and return it.
    The calling service account must have the 'Secret Manager Secret Accessor' role.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload
