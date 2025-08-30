"""Streamlit chat interface for Rickbot-ADK.

This module provides the Streamlit-based chat interface for the Rickbot-ADK application.
It handles user input, displays chat messages, manages personality selection,
and interacts with the Agent Development Kit (ADK) runner to generate bot responses.
"""

import asyncio
from pathlib import Path
from typing import Any

import streamlit as st
from google.adk.runners import Runner
from google.genai.types import Blob, Content, Part

from rickbot_agent.personality import personalities
from streamlit_fe.st_utils import RateLimiter

# Define the root path of the project
ROOT_DIR = Path(__file__).parent.parent
USER_AVATAR = str(ROOT_DIR / "rickbot_agent/media/morty.png")


async def get_agent_response(runner: Runner, prompt: str, uploaded_file: Any, rate_limiter: RateLimiter):
    """
    Handles user input and generates the bot's response using the Rickbot ADK agent.
    """
    # --- Rate Limiting Check ---
    # Perform this check *before* modifying session state or displaying the user's prompt
    if not rate_limiter.hit("rickbot"):
        st.warning(
            "Whoa, slow down there! Give me a minute."
        )
        st.stop()  # Stop execution to prevent the message from being processed

    # Create the user message object, including any attachments
    user_message: dict[str, Any] = {"role": "user", "content": prompt}
    if uploaded_file:
        user_message["attachment"] = {
            "data": uploaded_file.getvalue(),
            "mime_type": uploaded_file.type or "",
        }
    st.session_state.messages.append(user_message)

    # Display user message and attachment in the chat
    with st.chat_message("user", avatar=USER_AVATAR):
        if uploaded_file:
            mime_type = uploaded_file.type or ""
            if "image" in mime_type:
                st.image(uploaded_file.getvalue())
            elif "video" in mime_type:
                st.video(uploaded_file.getvalue())
        st.markdown(prompt)

    # Prepare the message for the ADK
    message_parts = [Part(text=prompt)]
    if uploaded_file:
        message_parts.append(
            Part(
                inline_data=Blob(data=uploaded_file.getvalue(), mime_type=uploaded_file.type)
            )
        )

    new_message = Content(role="user", parts=message_parts)

    # Generate and display the agent's response
    with st.status("Thinking...", expanded=True) as bot_status:
        with st.chat_message("assistant", avatar=st.session_state.current_personality.avatar):
            response_placeholder = st.empty() # empty invisible container for retrieving streamed content
            full_response = ""

            # Call the agent runner
            async for event in runner.run_async(
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
                new_message=new_message
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts: # retrieve the response in parts
                        if part.text:
                            full_response += part.text
                    # Visual trick!
                    # Add the block element - a similated cursor - whilst the agent is still streaming the response
                    response_placeholder.markdown(full_response + "▌")

            bot_status.update(label="Done.", state="complete")
            response_placeholder.markdown(full_response)

    # Add the full bot response to the session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})


def render_chat(config, rate_limiter: RateLimiter, adk_runner: Runner):
    """
    Renders the main chat interface, including sidebar and chat history.
    """
    st.session_state.current_personality = st.session_state.current_personality

    # --- Session State Initialization ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "file_just_uploaded" not in st.session_state:
        st.session_state.file_just_uploaded = False

    def on_file_change():
        st.session_state.file_just_uploaded = True

    # --- Title and Introduction ---
    header_col1, header_col2 = st.columns([0.3, 0.7])
    header_col1.image(st.session_state.current_personality.avatar, width=140)
    header_col2.title(f"{st.session_state.current_personality.title}")
    st.caption(st.session_state.current_personality.welcome)

    # --- Sidebar for Configuration ---
    with st.sidebar:
        if config.auth_required and st.user.is_logged_in:
            st.caption(f"Welcome, {st.user.name}")
            st.button("Log out", on_click=st.logout)

        # --- Personality Selection ---
        personality_menu_names = [p.menu_name for p in personalities.values()]
        selected_menu_name = st.selectbox(
            "Choose your bot personality:",
            options=personality_menu_names,
            index=personality_menu_names.index(
                st.session_state.current_personality.menu_name
            ),
        )

        # Find the corresponding personality object based on the selected menu_name
        selected_personality = next(
            p for p in personalities.values() if p.menu_name == selected_menu_name
        )

        if selected_personality != st.session_state.current_personality:
            st.session_state.current_personality = selected_personality
            st.session_state.messages = []  # Reset messages on personality change
            st.rerun()

        st.info(st.session_state.current_personality.overview)

        uploaded_file = st.file_uploader(
            "Upload a file.",
            type=["png", "jpg", "jpeg", "pdf", "mp3", "mp4", "mov", "webm"],
            on_change=on_file_change,
        )

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.info(
            """
            ### Info
            * Created by Dazbo.
            * I do not store any user data, prompts or responses. Read our [Privacy Policy](/privacy_policy).
            * Check out the [GitHub repo](https://github.com/derailed-dash/rickbot-adk/).
            * View the [Rickbot blog posts](https://medium.com/google-cloud/creating-a-rick-morty-chatbot-with-google-cloud-and-the-gen-ai-sdk-e8108e83dbee).
            """
        )

    # Display previous messages from history
    for message in st.session_state.messages:
        avatar = (
            USER_AVATAR
            if message["role"] == "user"
            else st.session_state.current_personality.avatar
        )
        with st.chat_message(message["role"], avatar=avatar):
            if attachment := message.get("attachment"):
                if "image" in attachment.get("mime_type", ""):
                    st.image(attachment["data"])
                elif "video" in attachment.get("mime_type", ""):
                    st.video(attachment["data"])
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input(st.session_state.current_personality.prompt_question):
        file_to_process = None
        if st.session_state.get("file_just_uploaded"):
            file_to_process = uploaded_file
            st.session_state.file_just_uploaded = False # Consume the flag

        asyncio.run(get_agent_response(adk_runner, prompt, file_to_process, rate_limiter))