"""
If Rickbot is configured to perform user authentication,
then we delegate user authentication to one or more OAuth providers.

E.g. for we can use the Google Authentication Platform as an OAuth provider:
- We retrieve Google OAuth credentials (client_id and client_secret)
from Google Secret Manager and save them to secrets.toml at run time.
- OAuth credentials are required for Rickbot to identify itself to the Google Auth Platform.

The .streamlit/secrets.toml is Streamlit's standard mechanism for handling sensitive information.
- See Streamlit docs here: https://docs.streamlit.io/develop/concepts/connections/authentication.
- The file is built once when the service is first launched.

Now our users can authenticate using Google's Auth UI.
We can run this from our app code or standalone.
"""

import os

import streamlit as st

from rickbot_utils.logging_utils import setup_logger
from src.rickbot_utils.secret_utils import retrieve_secret

# Basic logger setup
logger = setup_logger(__name__)


@st.cache_resource  # This should only be done once
def create_secrets_toml(google_project_id: str) -> None:
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
