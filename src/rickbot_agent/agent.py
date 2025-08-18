import os

import google.auth
from google.adk.agents import Agent
from google.adk.tools import google_search

from .personality import personalities

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Get the Rick personality
rick_personality = personalities.get("Rick")

if rick_personality is None:
    raise ValueError("Rick personality not found.")

root_agent = Agent(
    name="rickbot_agent",
    model="gemini-2.5-flash",
    instruction=rick_personality.system_instruction,
    tools=[google_search],
)
