"""The root agent for the Rickbot ADK application."""

import os
import google.auth
from google.adk.agents import Agent
from .personality import personalities

# Set default environment variables for Vertex AI
try:
    _, project_id = google.auth.default()
    if project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except (google.auth.exceptions.DefaultCredentialsError, ImportError):
    print("Google Cloud credentials not found. Skipping project ID setup.")
    # Handle cases where credentials are not available, e.g., in a CI/CD environment
    # without user login. You might want to set a default project or handle this case
    # based on your application's needs.
    pass


os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Load the Rick personality
rick_personality = personalities.get("Rick")

if not rick_personality:
    raise ValueError(
        "Could not load the 'Rick' personality. "
        "Make sure it is defined in personalities.yaml"
    )

# Define the root agent using the loaded personality
root_agent = Agent(
    name="rickbot_agent",
    model="gemini-2.5-flash",
    instruction=rick_personality.system_instruction,
)