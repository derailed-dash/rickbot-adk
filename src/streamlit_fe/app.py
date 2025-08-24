"""
This is the main entry point for the Rickbot Streamlit application.
"""

import asyncio
import uuid
from pathlib import Path

import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from streamlit.errors import StreamlitAPIException
from streamlit.runtime.scriptrunner import get_script_run_ctx

from rickbot_agent.agent import get_agent  # Import the agent getter
from rickbot_agent.personality import Personality, get_avatar, personalities
from streamlit_fe.chat import render_chat
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
    return Runner(
        agent=rickbot_agent,
        app_name=config.app_name,
        session_service=session_service
    )

@st.cache_resource # Ensure this rate limiter is share d across all user sessions and reruns
def initialize_rate_limiter():
    """ Initialize the rate limiter. """
    return RateLimiter(config.rate_limit_qpm)

def main():
    """ Main function to run the Streamlit application. """
    try:
        # --- Page Configuration ---
        st.set_page_config(
            page_title="Rickbot",
            page_icon=RICKBOT_AVATAR,  # Rickbot logo
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # --- Authentication Check ---
        if config.auth_required and not st.user.is_logged_in:
            st.error("Please log in to access this application.")
            st.stop()

        # --- Rate Limiting ---
        rate_limiter = initialize_rate_limiter()

        # --- Session State Initialization ---
        if "user_id" not in st.session_state:
            if config.auth_required and st.user.is_logged_in:
                st.session_state.user_id = st.user.email
            else:
                # No user logged in so get use Streamlit unique session ID as a stand-in for user_id
                ctx = get_script_run_ctx()
                st.session_state.user_id = ctx.session_id if ctx else "anonymous_user"

            logger.debug(f"User ID: {st.session_state.user_id}")

        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            logger.debug(f"Session ID: {st.session_state.session_id}")

        if "current_personality" not in st.session_state:
            st.session_state.current_personality = personalities[DEFAULT_PERSONALITY]

        # Re-initialize ADK runner if personality changes or not yet initialized
        if (
            "adk_runner" not in st.session_state
            or st.session_state.get("last_personality") != st.session_state.current_personality
        ):
            st.session_state.adk_runner = asyncio.run(
                initialize_adk_runner(st.session_state.current_personality)
            )
            st.session_state.last_personality = (st.session_state.current_personality)

        # --- Render Chat Interface ---
        render_chat(
            config,
            rate_limiter,
            st.session_state.adk_runner
        )

    except (StreamlitAPIException, KeyError, ValueError, TypeError, RuntimeError) as e:
        st.error(f"An unexpected error occurred: {e}")
        logger.error(f"Application error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
