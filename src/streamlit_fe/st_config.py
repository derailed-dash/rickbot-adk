"""
This module contains the configuration for the Rickbot Streamlit application.
"""

import os
from dataclasses import dataclass

import streamlit as st

from rickbot_utils.logging_utils import setup_logger

app_name = os.environ.setdefault("APP_NAME", "rickbot_st_ui")

logger = setup_logger(app_name)

@dataclass
class Config:
    """Configuration for the application, loaded from environment variables."""

    app_name: str
    google_project_id: str  # used for Google Auth
    auth_required: bool
    rate_limit_qpm: int  # queries per minute

@st.cache_resource
def get_config() -> Config:
    """Returns the application configuration."""
    google_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not google_project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")
    auth_required = os.environ.get("AUTH_REQUIRED", "false").lower() == "true"
    rate_limit = int(os.environ.get("RATE_LIMIT", "20"))  # Set a low rate limit by default

    logger.debug(f"Auth required: {auth_required}")
    logger.debug(f"Rate limit: {rate_limit} qpm")

    return Config(
        google_project_id=google_project_id,
        app_name=app_name,
        auth_required=auth_required,
        rate_limit_qpm=rate_limit,
    )

config = get_config()
