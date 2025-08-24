"""
This module contains the configuration for the Rickbot Streamlit application.
"""

import logging
import os
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app_name = os.environ.setdefault("APP_NAME", "rickbot_st_ui")


def setup_logger() -> logging.Logger:
    """Sets up and configures a logger for the application."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    app_logger = logging.getLogger(app_name)
    log_level_num = getattr(logging, log_level, logging.INFO)
    app_logger.setLevel(log_level_num)

    # Add a handler only if one doesn't exist to prevent duplicate logs
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d:%(name)s - %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        app_logger.addHandler(handler)

    app_logger.info("Logger initialised.")
    app_logger.debug("DEBUG level logging enabled.")

    return app_logger


logger = setup_logger()

@dataclass
class Config:
    """Configuration for the application, loaded from environment variables."""

    app_name: str
    auth_required: bool
    rate_limit_qpm: int # queries per minute

@st.cache_resource
def get_config() -> Config:
    """Returns the application configuration."""
    auth_required = os.environ.get("AUTH_REQUIRED", "false").lower() == "true"
    rate_limit = int(os.environ.get("RATE_LIMIT", "20")) # Set a low rate limit by default

    logger.debug(f"Auth required: {auth_required}")
    logger.debug(f"Rate limit: {rate_limit} qpm")

    return Config(
        app_name=app_name,
        auth_required=auth_required,
        rate_limit_qpm=rate_limit,
    )

config = get_config()
