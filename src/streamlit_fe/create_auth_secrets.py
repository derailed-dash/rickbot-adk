"""Creates local .streamlit/secrets.toml from secret in Google Secret Manager
We can run this from our app code or standalone."""

import logging
import os

import streamlit as st
from google.cloud import secretmanager

# Basic logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@st.cache_resource
def create_secrets_toml(google_project_id: str):
    streamlit_dir = ".streamlit"
    secrets_file_path = os.path.join(streamlit_dir, "secrets.toml")

    if os.path.exists(secrets_file_path):
        logger.info(".streamlit/secrets.toml already exists, skipping creation.")
        return  # Nothing to do

    logger.info("Retrieving OAuth credentials.")
    try:
        secret_name = "rickbot-streamlit-secrets-toml"
        secret = retrieve_secret(google_project_id, secret_name)

        os.makedirs(streamlit_dir, exist_ok=True)
        logger.info(".streamlit/ created.")
        with open(secrets_file_path, "w") as f:
            f.write(secret)
        logger.info(f"Successfully created {secrets_file_path}")

    except Exception as e:
        raise ValueError(
            f"Error accessing secret '{secret_name}' from Secret Manager: {e}"
        ) from e

if __name__ == "__main__":
    prj_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if prj_id:
        create_secrets_toml(prj_id)
    else:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set.")
