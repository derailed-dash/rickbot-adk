import json
import os

# Set this BEFORE importing any src modules to ensure config picks it up
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
MOCK_TOKEN = "mock:123:test@example.com:Tester"
HEADERS = {"Authorization": f"Bearer {MOCK_TOKEN}"}

@pytest.mark.asyncio
async def test_dazbo_rag_agent_transfer():
    """
    Integration test to verify that the Dazbo persona triggers a transfer to the RagAgent
    when asked about topics relevant to its knowledge base (e.g., Google Cloud).
    """
    prompt = "What is your experience with Google Cloud and Agentic AI?"
    personality = "Dazbo"

    # We use chat_stream because it yields tool_call events
    # TestClient.post with stream=True works like requests
    with client.stream(
        "POST",
        "/chat_stream",
        data={"prompt": prompt, "personality": personality},
        headers=HEADERS,
    ) as response:
        assert response.status_code == 200

        found_rag_usage = False
        events = []

        for line in response.iter_lines():
            if line:
                if line.startswith("data: "):
                    data_str = line[len("data: "):].strip()
                    try:
                        event_data = json.loads(data_str)
                        events.append(event_data)
                        # Check for either agent_transfer or tool_call to RagAgent
                        if event_data.get("agent_transfer") == "RagAgent":
                            found_rag_usage = True
                        if (
                            "tool_call" in event_data
                            and event_data["tool_call"].get("name") == "RagAgent"
                        ):
                            found_rag_usage = True
                    except json.JSONDecodeError:
                        continue

        # Verify that the RagAgent was indeed triggered
        assert found_rag_usage, f"Did not find 'RagAgent' usage in events: {events}"
        print("\nSuccessfully detected usage of RagAgent for Dazbo persona.")
