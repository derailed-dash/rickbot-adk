"""
Integration tests to execute the agent with each personality.
"""

import pytest
import tenacity
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import errors
from google.genai.types import Content, Part

from rickbot_agent.agent import get_agent

# Hardcode the list of known personalities to avoid executing get_personalities() during collection
# which would trigger credential loading before conftest.py sets the Test Mode env var.
KNOWN_PERSONALITIES = ["Rick", "Yoda", "Donald", "Yasmin", "Jack", "Dazbo"]


@pytest.mark.asyncio
@pytest.mark.parametrize("personality_name", KNOWN_PERSONALITIES)
# The @tenacity.retry decorator is used to automatically retry the test if it
# fails with a `google.genai.errors.ClientError`, which typically happens
# when the API rate limit is exceeded (429 RESOURCE_EXHAUSTED).
# - wait=tenacity.wait_exponential(multiplier=1, min=4, max=10): Implements
#   exponential backoff, starting with a 4-second wait and increasing
#   exponentially up to a maximum of 10 seconds between retries.
# - stop=tenacity.stop_after_attempt(5): Stops retrying after 5 attempts.
# - retry=tenacity.retry_if_exception_type(errors.ClientError): Specifies
#   that the retry should only happen for `ClientError` exceptions.
@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type(errors.ClientError),
)
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
