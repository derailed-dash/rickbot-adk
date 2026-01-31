"""Unit tests for generic file search store support in the agent."""

from typing import cast
from unittest.mock import patch

import pytest
from google.adk.agents import Agent
from google.adk.tools import AgentTool

from rickbot_agent.agent import create_agent
from rickbot_agent.personality import Personality
from rickbot_agent.tools_custom import FileSearchTool


@pytest.fixture
def mock_config():
    with patch("rickbot_agent.agent.config") as m:
        m.model = "gemini-2.0-flash"
        m.agent_name = "test_agent"
        yield m


@patch("rickbot_agent.agent.get_store")
def test_create_agent_attaches_file_search_tool_for_any_personality(mock_get_store, mock_config):
    """Test that any personality with file_search_store_id gets the tool and instruction."""
    mock_get_store.return_value = "projects/test/locations/global/stores/yoda-store"

    # Define a personality that is NOT Dazbo but has a search store
    personality = Personality(
        name="Yoda",
        menu_name="Yoda",
        title="Yoda",
        overview="Wise one.",
        welcome="Welcome.",
        prompt_question="Query?",
        temperature=0.7,
        file_search_store_name="projects/test/locations/global/stores/yoda-store",
    )
    # We also need to mock personality.system_instruction because it's set in __post_init__
    # which might call secret manager. But our previous change to personality.py
    # and the fact that we might be in test mode handles it.
    # To be safe, let's just set it.
    personality.system_instruction = "You are Yoda."

    agent = create_agent(personality)

    # 1. Check instruction contains the new Tool Usage Policy header and prioritization
    assert "## TOOL USAGE POLICY:" in agent.instruction
    assert "1. **RagAgent (Internal Knowledge)**: This is your PRIORITIZED source" in agent.instruction
    assert "CRITICAL: If a user asks a question related to any of the topics" in agent.instruction

    # 2. Check tools include AgentTool for RagAgent
    rag_agent_tool = next((t for t in agent.tools if isinstance(t, AgentTool) and t.agent.name == "RagAgent"), None)
    assert rag_agent_tool is not None

    # Check that the RagAgent has the FileSearchTool
    rag_agent = cast(Agent, rag_agent_tool.agent)
    file_search_tools = [t for t in rag_agent.tools if isinstance(t, FileSearchTool)]
    assert len(file_search_tools) == 1
    assert file_search_tools[0].file_search_store_names == ["projects/test/locations/global/stores/yoda-store"]


def test_create_agent_no_file_search_tool_when_id_missing(mock_config):
    """Test that a personality without file_search_store_id does NOT get the tool."""
    personality = Personality(
        name="Rick",
        menu_name="Rick",
        title="Rick",
        overview="Smart.",
        welcome="Hey.",
        prompt_question="What?",
        temperature=1.0,
        file_search_store_name=None,
    )
    personality.system_instruction = "You are Rick."

    agent = create_agent(personality)

    # 1. Check instruction does NOT contain the Tool Usage Policy
    assert "## TOOL USAGE POLICY:" not in agent.instruction
    assert "RagAgent (Internal Knowledge)" not in agent.instruction

    # 2. Check tools do NOT include FileSearchTool
    file_search_tools = [t for t in agent.tools if isinstance(t, FileSearchTool)]
    assert len(file_search_tools) == 0


@patch("rickbot_agent.agent.get_store")
def test_create_agent_no_rag_agent_when_store_not_found(mock_get_store, mock_config):
    """Test that if the store is not found, RagAgent is not added but creation continues."""
    mock_get_store.return_value = None  # Simulate store not found

    personality = Personality(
        name="Yoda",
        menu_name="Yoda",
        title="Yoda",
        overview="Wise one.",
        welcome="Welcome.",
        prompt_question="Query?",
        temperature=0.7,
        file_search_store_name="missing-store",
    )
    personality.system_instruction = "You are Yoda."

    agent = create_agent(personality)

    # 1. Check instruction does NOT contain RagAgent info
    assert "## TOOL USAGE POLICY:" not in agent.instruction
    assert "RagAgent (Internal Knowledge)" not in agent.instruction

    # 2. Check RagAgent is not in tools
    rag_agent_tool = next((t for t in agent.tools if isinstance(t, AgentTool) and t.agent.name == "RagAgent"), None)
    assert rag_agent_tool is None

    # 3. Check description matches fallback
    assert "with access to a SearchAgent to perform Google Search." in agent.description
