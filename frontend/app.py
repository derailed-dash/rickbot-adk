"""
This is the main entry point for the Rickbot Streamlit application.
"""

import asyncio
from pathlib import Path

import streamlit as st
from chat import render_chat
from config import get_config, logger
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import RateLimiter

from rickbot_agent.agent import (
    root_agent as initial_root_agent,  # Import the base agent
)
from rickbot_agent.personality import personalities

# Define the root path of the project
ROOT_DIR = Path(__file__).parent.parent


async def initialize_adk_runner(personality_name: str):
    current_personality = personalities[personality_name]

    # Create a new agent instance with the selected personality's instruction
    # We need to create a new Agent instance because the instruction is set at initialization
    adk_agent = initial_root_agent  # Start with the base agent
    adk_agent.instruction = current_personality.system_instruction  # Update instruction

    session_service = InMemorySessionService()
    session_id = st.session_state.get("session_id", "test_session")
    await session_service.create_session(
        app_name="rickbot_agent", user_id="test_user", session_id=session_id
    )
    return Runner(
        agent=adk_agent, app_name="rickbot_agent", session_service=session_service
    )


def main():
    """
    Main function to run the Streamlit application.
    """
    try:
        # --- Page Configuration ---
        st.set_page_config(
            page_title="Rickbot",
            page_icon=str(
                ROOT_DIR / "rickbot_agent/media/rickbot-trans.png"
            ),  # Rickbot logo
            layout="wide",
            initial_sidebar_state="expanded",
        )

        config = get_config()

        # --- Authentication Check ---
        if config.auth_required and not st.user.is_logged_in:
            st.error("Please log in to access this application.")
            st.stop()

        # --- Rate Limiting ---
        rate_limiter = RateLimiter(max_requests=5, period_seconds=60)

        # --- Session State Initialization ---
        if "current_personality_name" not in st.session_state:
            st.session_state.current_personality_name = "Rick"

        # Re-initialize ADK runner if personality changes or not yet initialized
        if (
            "adk_runner" not in st.session_state
            or st.session_state.get("last_personality_name")
            != st.session_state.current_personality_name
        ):
            st.session_state.adk_runner = asyncio.run(
                initialize_adk_runner(st.session_state.current_personality_name)
            )
            st.session_state.last_personality_name = (
                st.session_state.current_personality_name
            )

        # --- Render Chat Interface ---
        render_chat(
            config, rate_limiter, config.rate_limit, st.session_state.adk_runner
        )

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        logger.error(f"Application error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
