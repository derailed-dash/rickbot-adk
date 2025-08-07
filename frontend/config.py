"""
This module contains the configuration for the Rickbot Streamlit application.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the script's directory
SCRIPT_DIR = Path(__file__).parent.resolve()


@dataclass
class Config:
    """Configuration for the application, loaded from environment variables."""

    project_id: str | None = os.environ.get("GOOGLE_CLOUD_PROJECT")
    region: str | None = os.environ.get("GOOGLE_CLOUD_REGION")
    auth_required: bool = os.environ.get("AUTH_REQUIRED", "false").lower() == "true"
    rate_limit: str | None = os.environ.get("RATE_LIMIT")


@st.cache_resource
def get_config() -> Config:
    """Returns the application configuration."""
    return Config()
