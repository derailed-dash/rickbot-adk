"""
This module contains the chat interface for the Rickbot Streamlit application.
"""

import asyncio
from typing import Any
import streamlit as st
from google.genai.types import Content, Part
from rickbot_agent.personality import personalities

USER_AVATAR = "/home/darren/localdev/Python/rickbot-adk/rickbot_agent/media/morty.png"


async def get_adk_response(runner, prompt: str, uploaded_file: Any):
    """
    Handles user input and generates the bot's response using the ADK.
    """
    # This would be a good place to add rate limiting if needed

    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    # Prepare the message for the ADK
    message_parts = [Part(text=prompt)]
    if uploaded_file:
        # This part would need to be adapted if you want to handle file uploads
        # For now, we'll just pass the text
        pass

    new_message = Content(role="user", parts=message_parts)

    # Generate and display the ADK agent's response
    with st.chat_message("assistant", avatar=st.session_state.current_personality.avatar):
        response_placeholder = st.empty()
        full_response = ""
        async for event in runner.run_async(
            user_id="test_user", session_id="test_session", new_message=new_message
        ):
            if event.is_final_response() and event.content:
                full_response += event.content.parts[0].text
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)

    # Add the full bot response to the session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})


def render_chat(config, rate_limiter, rate_limit, adk_runner):
    """
    Renders the main chat interface, including sidebar and chat history.
    """
    st.session_state.current_personality = personalities[st.session_state.current_personality_name]

    # --- Title and Introduction ---
    header_col1, header_col2 = st.columns([0.3, 0.7])
    header_col1.image(st.session_state.current_personality.avatar, width=140)
    header_col2.title(f"{st.session_state.current_personality.title}")
    st.caption(st.session_state.current_personality.welcome)

    # --- Session State Initialization ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

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
            index=personality_menu_names.index(st.session_state.current_personality.menu_name),
        )

        # Find the corresponding personality object based on the selected menu_name
        selected_personality = next(
            p for p in personalities.values() if p.menu_name == selected_menu_name
        )

        if selected_personality.name != st.session_state.current_personality_name:
            st.session_state.current_personality_name = selected_personality.name
            st.session_state.messages = []  # Reset messages on personality change
            st.rerun()

        st.info(st.session_state.current_personality.overview)

        # --- File Uploader (placeholder for now) ---
        uploaded_file = st.file_uploader(
            "Upload a file.",
            type=["png", "jpg", "jpeg", "pdf", "mp3", "mp4", "mov", "webm"],
            disabled=True # Disabled until file upload is fully integrated with ADK
        )

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.info(
            """
            ### Info
            * Created by Dazbo.
            * I do not store any user data, prompts or responses. Read our [Privacy Policy](/privacy_policy).
            * Check out the [GitHub repo](https://github.com/derailed-dash/rickbot/).
            * View the [Rickbot blog post](https://medium.com/google-cloud/creating-a-rick-morty-chatbot-with-google-cloud-and-the-gen-ai-sdk-e8108e83dbee).
            """
        )

    # Display previous messages from history
    for message in st.session_state.messages:
        avatar = (
            USER_AVATAR if message["role"] == "user" else st.session_state.current_personality.avatar
        )
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input(st.session_state.current_personality.prompt_question):
        asyncio.run(get_adk_response(adk_runner, prompt, None))