"""
Integration tests to execute the agent with each personality.
"""

import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from rickbot_agent.agent import get_agent
from rickbot_agent.personality import get_personalities


@pytest.mark.asyncio
@pytest.mark.parametrize("personality_name", get_personalities().keys())
async def test_personality_loads_and_responds(personality_name: str) -> None:
    """
    Tests that each personality can be loaded, receive a prompt, and generate a response.

    This test is parameterized to run for each personality name defined in the
    `personalities` dictionary. It ensures that the agent for each character
    can be initialized and can produce a valid, non-empty response to a simple
    prompt.

    Args:
        personality_name (str): The name of the personality to test, injected by pytest.
    """
    # 1. Setup: Initialize the agent and session for the given personality.
    # The `get_agent` function is responsible for loading the correct
    # system prompt and configuration for the specified personality.
    agent = get_agent(personality_name)
    session_service = InMemorySessionService()
    session_id = "test_session"
    user_id = "test_user"
    await session_service.create_session(app_name="rickbot_test", user_id=user_id, session_id=session_id)
    runner = Runner(agent=agent, app_name="rickbot_test", session_service=session_service)
    prompt = "Hello"
    new_message = Content(role="user", parts=[Part(text=prompt)])

    # 2. Execution: Run the agent with the prompt and capture the final response.
    # We iterate through the asynchronous events from the agent's run
    # and build the final response string from the text parts of the final event.
    final_response = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    # 3. Assertion: Verify that the agent generated a non-empty response.
    # This confirms that the agent processed the input and produced an output.
    assert final_response, f"Agent for personality '{personality_name}' did not return a response."
    print(f"Personality '{personality_name}' responded successfully.")
