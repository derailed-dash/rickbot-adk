"""Integration tests for the Rickbot agent, making use of Google APIs.

This file contains unit tests to verify the functionality and behavior of the
Rickbot agent, including its ability to handle multi-turn conversations and
maintain context.
"""

import pytest
import tenacity
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import errors
from google.genai import types as genai_types

from rickbot_agent.agent import get_agent

APP_NAME = "test_rickbot"


# The @tenacity.retry decorator is used to automatically retry the test if it
# fails with a `google.genai.errors.ClientError`, which typically happens
# when the API rate limit is exceeded (429 RESOURCE_EXHAUSTED).
# - wait=tenacity.wait_exponential(multiplier=1, min=4, max=10): Implements
#   exponential backoff, starting with a 4-second wait and increasing
#   exponentially up to a maximum of 10 seconds between retries.
# - stop=tenacity.stop_after_attempt(5): Stops retrying after 5 attempts.
# - retry=tenacity.retry_if_exception_type(errors.ClientError): Specifies
#   that the retry should only happen for `ClientError` exceptions.
@pytest.mark.asyncio
@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type(errors.ClientError),
)
async def test_rickbot_agent_response():
    """Tests that the rickbot agent returns a non-empty response."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id="test_user", session_id="test_session"
    )
    agent = get_agent("Rick")
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    query = "What is the meaning of life?"
    response_text: str | None = ""
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


# The @tenacity.retry decorator is used to automatically retry the test if it
# fails with a `google.genai.errors.ClientError`, which typically happens
# when the API rate limit is exceeded (429 RESOURCE_EXHAUSTED).
# - wait=tenacity.wait_exponential(multiplier=1, min=4, max=10): Implements
#   exponential backoff, starting with a 4-second wait and increasing
#   exponentially up to a maximum of 10 seconds between retries.
# - stop=tenacity.stop_after_attempt(5): Stops retrying after 5 attempts.
# - retry=tenacity.retry_if_exception_type(errors.ClientError): Specifies
#   that the retry should only happen for `ClientError` exceptions.
@pytest.mark.asyncio
@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type(errors.ClientError),
)
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
    agent = get_agent("Rick")
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    queries = ["Hello, my name is Dazbo", "What is my name?"]
    responses = []
    for query in queries:
        print(f"Query: {query}")
        response_text: str | None = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=query)],
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
