"""
This is the main entry point for the Rickbot Streamlit application.
"""

import asyncio
import os
import uuid
from pathlib import Path

import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from streamlit.errors import StreamlitAPIException
from streamlit.runtime.scriptrunner import get_script_run_ctx

from rickbot_agent.agent import get_agent  # Import the agent getter
from rickbot_agent.personality import Personality, get_avatar, get_personalities
from streamlit_fe.chat import render_chat
from streamlit_fe.create_auth_secrets import create_secrets_toml
from streamlit_fe.st_config import config, logger
from streamlit_fe.st_utils import RateLimiter

# Define the root path of the project
ROOT_DIR = Path(__file__).parent.parent
DEFAULT_PERSONALITY = "Rick"
RICKBOT_AVATAR = get_avatar("rickbot-trans")


async def initialize_adk_runner(personality: Personality):
    """Initialise the ADK runner with the correct agent personality."""
    rickbot_agent = get_agent(personality.name)

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=config.app_name,
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
    )
    return Runner(agent=rickbot_agent, app_name=config.app_name, session_service=session_service)


@st.cache_resource  # Ensure this rate limiter is shared across all user sessions and reruns
def initialize_rate_limiter():
    """Initialize the rate limiter."""
    return RateLimiter(config.rate_limit_qpm)


def render_login_screen(mock_user: bool = False, mock_user_email: str | None = None):
    """Renders the login screen for both real and mock users."""
    header_col1, header_col2 = st.columns([0.3, 0.7])
    header_col1.image(RICKBOT_AVATAR, width=140)
    header_col2.title(f"{st.session_state.current_personality.title}")

    st.divider()
    st.markdown(
        "Rickbot is a multi-personality chatbot application. Chat with Rick or other personalities, ask your questions, and feel free to upload content as part of your discussion."
    )
    st.markdown(
        ":eyes: We do not store any user data, prompts or responses. Read our [Privacy Policy](/privacy_policy)."
    )
    st.divider()
    if mock_user:
        st.markdown(":lock: Click to start your mock session.")
        if st.button("Log in as Mock User", use_container_width=True):
            st.session_state.is_logged_in = True
            st.session_state.user_email = mock_user_email
            st.session_state.user_name = "Mock User"
            st.rerun()
    else:
        st.markdown(
            ":lock: Please login to use Rickbot. Any Google account will do. Login helps us prevent abuse and maintain a stable, accessible experience for everyone."
        )
        if st.button("Log in with Google", use_container_width=True):
            st.login("google")


def main():
    """Main function to run the Streamlit application."""
    # --- Page Configuration ---
    st.set_page_config(
        page_title="Rickbot",
        page_icon=RICKBOT_AVATAR,  # Rickbot logo
        layout="wide",
        initial_sidebar_state="expanded",
    )

    personalities = get_personalities()
    if "current_personality" not in st.session_state:
        st.session_state.current_personality = personalities[DEFAULT_PERSONALITY]

    # --- Authentication Check ---
    mock_user_email = os.environ.get("MOCK_AUTH_USER")

    # Initialize login state if it doesn't exist
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False

    # If logged in, show the app
    if st.session_state.is_logged_in:
        authenticated_flow()
        return

    # --- Login Flow ---
    if mock_user_email:
        render_login_screen(mock_user=True, mock_user_email=mock_user_email)
    elif config.auth_required:
        try:
            create_secrets_toml(config.google_project_id)  # Do once and cache
        except ValueError as e:
            logger.error(f"Failed to setup auth: {e}", exc_info=True)
            st.error(f"⚠️ Could not initialize the application. Please check your configuration. Error: {e}")
            st.stop()

        if not st.user.is_logged_in:
            render_login_screen(mock_user=False)
        else:
            # This block is for when st.user.is_logged_in is true, but our session_state flag is not.
            # This happens on the rerun after a successful login.
            st.session_state.is_logged_in = True
            st.session_state.user_email = st.user.email
            st.session_state.user_name = st.user.name
            st.rerun()  # Rerun to enter the authenticated_flow
    else:  # No authentication required - go straight to authenticated page
        st.session_state.is_logged_in = False
        authenticated_flow()


def authenticated_flow():
    try:
        # --- Rate Limiting ---
        rate_limiter = initialize_rate_limiter()

        # --- Session State Initialization ---
        if "user_id" not in st.session_state:
            if st.session_state.get("is_logged_in"):
                st.session_state.user_id = st.session_state.user_email
            else:
                # No user logged in so get use Streamlit unique session ID as a stand-in for user_id
                ctx = get_script_run_ctx()
                st.session_state.user_id = ctx.session_id if ctx else "anonymous_user"

            logger.debug(f"User ID: {st.session_state.user_id}")

        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            logger.debug(f"Session ID: {st.session_state.session_id}")

        # Re-initialize ADK runner if personality changes or not yet initialized
        if (
            "adk_runner" not in st.session_state
            or st.session_state.get("last_personality") != st.session_state.current_personality
        ):
            st.session_state.adk_runner = asyncio.run(initialize_adk_runner(st.session_state.current_personality))
            st.session_state.last_personality = st.session_state.current_personality

        # --- Render Chat Interface ---
        render_chat(rate_limiter, st.session_state.adk_runner)

    except (StreamlitAPIException, KeyError, ValueError, TypeError, RuntimeError) as e:
        st.error(f"An unexpected error occurred: {e}")
        logger.error(f"Application error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
