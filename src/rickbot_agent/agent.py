"""
This module defines the main agent for the Rickbot-ADK application.
It initializes a set of Google Gemini-powered agent, each loaded from a specific personality.
We then cache these agents for fast retrieval.
"""

import functools
from textwrap import dedent

from google import genai
from google.adk.agents import Agent
from google.adk.tools import AgentTool, google_search
from google.genai.types import GenerateContentConfig

from rickbot_utils.config import config, logger

from .personality import Personality, get_personalities
from .tools_custom import FileSearchTool

client = genai.Client()
if not client:
    logger.error("Could not initialize GenAI client.")
    raise ValueError("Could not initialize GenAI client.")

@functools.cache
def get_store(store_name: str):
    """Retrieve the store from the store name."""
    try:
        for a_store in client.file_search_stores.list():
            if a_store.display_name == store_name:
                logger.debug(f"Found and returning store: {a_store.name}")
                return a_store.name
    except Exception as e:
        logger.error(f"Error in get_store path: {e}")

    return None


# ADK Built-in Tool Limitation:
# A single root agent or a standalone agent can only support ONE built-in tool.
# See here: https://google.github.io/adk-docs/tools/built-in-tools/#use-built-in-tools-with-other-tools
# It cannot use other tools (custom or built-in) simultaneously within the same agent.
# To combine multiple built-in tools or use built-in tools with other custom tools,
# we should define an agent to wrap the built-in tool. This is the Agent-as-a-Tool pattern.
# Note: agent-as-tool receives only necessary input, whereas a sub-agent can access the complete session context.
search_agent = Agent(
    model=config.model,
    name="SearchAgent",
    description="Fallback agent to perform Google Search when internal knowledge base (RagAgent) is insufficient.",
    instruction="You are a fallback agent. Only use Google Search if the request cannot be answered by the RagAgent.",
    tools=[google_search],
)


# RAG Specialist Agent (File Search only)
def create_rag_agent(file_store_name: str) -> Agent:
    store_name = get_store(file_store_name)
    if store_name:
        logger.info(f"Creating RagAgent connected to {store_name}")
        instruction = """Use the file_search tool to retrieve information from the knowledge base."""

        return Agent(
            model=config.model,
            name="RagAgent",
            description=(
                "Primary agent for answering questions using the internal knowledge base. "
                "ALWAYS consult this agent first."
            ),
            instruction=instruction,
            tools=[FileSearchTool(file_search_store_names=[store_name])],

        )
    else:
        logger.warning("No File Search Store found. RagAgent will not be available.")
        return None


def create_agent(personality: Personality) -> Agent:
    """Creates and returns an agent with the given personality."""

    logger.debug(f"Creating agent for personality: {personality.name}")

    tools = [AgentTool(agent=search_agent)]
    instruction = ""

    if personality.file_search_store_name:
        logger.debug(f"Adding {personality.file_search_store_name} for personality: {personality.name}")
        instruction += dedent("""
        IMPORTANT: You MUST ALWAYS start by searching your reference materials using the RagAgent.
        Only use the SearchAgent if the RagAgent does not provide a relevant answer.

        """)
        rag_agent = create_rag_agent(personality.file_search_store_name)
        if rag_agent:
            tools.append(AgentTool(agent=rag_agent))
            logger.debug(f"Added {rag_agent.name}")

            instruction += dedent("""
            You have access to a specialist agent: RagAgent, which has access to reference materials.
            You also have access to SearchAgent for Google Search.

            IMPORTANT: You MUST ALWAYS start by searching your reference materials using the RagAgent.
            Only use the SearchAgent if the RagAgent does not provide a relevant answer. This supersedes any other 
            guidance provided to you.

            """)

            instruction += f"""{personality.system_instruction}"""

            instruction += dedent("""

            REMEMBER: You must ALWAYS start by searching your reference materials using the RagAgent.
            """)

        else:
            logger.warning(f"Failed to add {personality.file_search_store_name}")
    else:
        logger.debug(f"No File Search Store found for personality: {personality.name}")
        instruction += f"""{personality.system_instruction}"""
        instruction += dedent("""

        IMPORTANT: Use the SearchAgent to perform a Google Search if you do not have the relevant answer,
        or if the user's query requires an up-to-date answer.""")

    return Agent(
        name=f"{config.agent_name}_{personality.name}",  # Make agent name unique
        description=f"""A chatbot with the personality of {personality.menu_name} 
        with access to two specialist agents: a RagAgent for its knowledge base and SearchAgent for Google Search""",
        model=config.model,
        instruction=instruction,
        tools=tools,
        generate_content_config=GenerateContentConfig(temperature=personality.temperature, top_p=1, max_output_tokens=8192)
    )


@functools.cache
def _get_cached_agent_for_personality(personality: Personality) -> Agent:
    """
    Helper function to create and cache an agent for a given Personality object.
    This is where the actual caching happens.
    """
    logger.info(f"Lazily creating and caching agent for personality: {personality.name}")
    return create_agent(personality)


def get_agent(personality_name: str) -> Agent:
    """
    Retrieves a pre-configured agent from the cache, or creates it if not found.
    Agents are loaded lazily to improve startup performance.
    """
    personalities = get_personalities()
    personality = personalities.get(personality_name)

    if not personality:
        logger.error(f"Personality '{personality_name}' not found. Falling back to 'Rick'.")
        personality = personalities.get("Rick")
        if not personality:
            raise ValueError("Default 'Rick' personality not found. Cannot initialize agent.")

    # Call the cached helper function
    return _get_cached_agent_for_personality(personality)


# For backwards compatibility or direct access if needed, though get_agent is preferred.
# root_agent = get_agent("Rick") # REMOVED to avoid side-effects at import time
