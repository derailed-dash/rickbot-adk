"""
This script provides a command-line interface to test the RickBot agent.

It initializes an in-memory session and runs the agent with a sample query,
printing the agent's final response to the console. This is useful for quick,
programmatic validation of the agent's logic.
"""

# pylint: disable=wrong-import-position
import asyncio
import os
import sys

# Add this folder to the Python path to allow imports from 'src'.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from src.rickbot_agent.agent import root_agent

APP_NAME = "test_rickbot"


async def main():
    """
    Tests the agent's ability to maintain context across a two-turn conversation.
    """
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )
    queries = ["Hello, my name is Dazbo", "What is my name?"]
    for query in queries:
        print(f"> {query}")
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
                    print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
