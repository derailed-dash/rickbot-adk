"""Unit tests for the Rickbot agent.

This file contains unit tests to verify the functionality and behavior of the
Rickbot agent, including its ability to handle multi-turn conversations and
maintain context.
"""

import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from src.rickbot_agent.agent import root_agent

APP_NAME = "test_rickbot"


@pytest.mark.asyncio
async def test_rickbot_agent_response():
    """Tests that the rickbot agent returns a non-empty response."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )
    query = "What is the meaning of life?"
    response_text = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response():
            if event.content and event.content.parts and len(event.content.parts) > 0:
                response_text = event.content.parts[0].text
                print(f"Response: {response_text}")
            else:
                response_text = ""
            break

    assert isinstance(response_text, str)
    assert len(response_text) > 0


@pytest.mark.asyncio
async def test_rickbot_agent_two_turn_conversation():
    """
    Tests the agent's ability to maintain context across a two-turn conversation.

    It verifies that the agent can remember information from the first turn
    (the user's name) and use it in the second turn to answer a question.
    """
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )
    queries = ["Hello, my name is Dazbo", "What is my name?"]
    responses = []
    for query in queries:
        print(f"Query: {query}")
        response_text = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=genai_types.Content(
                role="user", parts=[genai_types.Part.from_text(text=query)]
            ),
        ):
            if event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and len(event.content.parts) > 0
                ):
                    response_text = event.content.parts[0].text
                    print(f"Response: {response_text}")
                else:
                    response_text = ""
                break
        responses.append(response_text)

    assert len(responses) == 2
    assert isinstance(responses[0], str)
    assert len(responses[0]) > 0
    assert isinstance(responses[1], str)
    assert "Dazbo" in responses[1]
