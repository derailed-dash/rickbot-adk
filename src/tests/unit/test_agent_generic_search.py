"""Unit tests for generic file search store support in the agent."""

from unittest.mock import patch

import pytest

from rickbot_agent.agent import create_agent
from rickbot_agent.personality import Personality
from rickbot_agent.tools_custom import FileSearchTool


@pytest.fixture
def mock_config():
    with patch("rickbot_agent.agent.config") as m:
        m.model = "gemini-2.0-flash"
        m.agent_name = "test_agent"
        yield m


def test_create_agent_attaches_file_search_tool_for_any_personality(mock_config):
    """Test that any personality with file_search_store_id gets the tool and instruction."""

    # Define a personality that is NOT Dazbo but has a search store
    personality = Personality(
        name="Yoda",
        menu_name="Yoda",
        title="Yoda",
        overview="Wise one.",
        welcome="Welcome.",
        prompt_question="Query?",
        temperature=0.7,
        file_search_store_id="projects/test/locations/global/stores/yoda-store",
    )
    # We also need to mock personality.system_instruction because it's set in __post_init__
    # which might call secret manager. But our previous change to personality.py
    # and the fact that we might be in test mode handles it.
    # To be safe, let's just set it.
    personality.system_instruction = "You are Yoda."

    agent = create_agent(personality)

    # 1. Check instruction contains generic search text
    # (Note: This will fail until we implement the generic instruction injection)
    assert "access to reference materials via the 'file_search' tool" in agent.instruction

    # 2. Check tools include FileSearchTool with correct ID
    file_search_tools = [t for t in agent.tools if isinstance(t, FileSearchTool)]
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
        file_search_store_id=None,
    )
    personality.system_instruction = "You are Rick."

    agent = create_agent(personality)

    # 1. Check instruction does NOT contain generic search text
    assert "access to reference materials via the 'file_search' tool" not in agent.instruction

    # 2. Check tools do NOT include FileSearchTool
    file_search_tools = [t for t in agent.tools if isinstance(t, FileSearchTool)]
    assert len(file_search_tools) == 0
