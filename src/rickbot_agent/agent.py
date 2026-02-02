"""
This module defines the main agent for the Rickbot-ADK application.
It initializes a set of Google Gemini-powered agent, each loaded from a specific personality.
We then cache these agents for fast retrieval.

IMPORTANT ARCHITECTURAL NOTE:
 This module performs critical monkey-patching of the `google.genai.Client` and `google.adk.tools.AgentTool`.
 Because the Google ADK library instantiates its own internal clients without accepting configuration arguments,
 we must apply these patches BEFORE any ADK modules are imported or used.

 Therefore, you will see `google.adk` imports placed further down in the file, *after* the patching logic.
 Attempting to move these imports to the top of the file will break the application (causing timeouts and hangs).
 Please do not "fix" the import order.
"""

import functools
import os
from textwrap import dedent
from typing import Any

from google import genai

from rickbot_utils.config import config, logger

# Monkey-patch genai.Client to force non-Vertex use if configured
# This is necessary because ADK Agents instantiate their own client and don't accept one as an argument
if not config.genai_use_vertexai:
    # Protect against multiple patching (e.g. reloads)
    if not getattr(genai.Client, "_is_patched", False):
        logger.info("Monkey-patching google.genai.Client to force vertexai=False")
        _OriginalClient = genai.Client

        class _PatchedClient(_OriginalClient):
            _is_patched = True
            def __init__(self, *args, **kwargs):
                kwargs['vertexai'] = False  # Force vertexai=False
                if 'api_key' not in kwargs or kwargs['api_key'] is None:
                     kwargs['api_key'] = os.getenv("GEMINI_API_KEY")

                # Set timeout for HTTP operations (in milliseconds)
                # 60000ms = 60 seconds, which provides sufficient time for:
                # - RAG store initialization and retrieval operations
                # - Network latency in containerized environments
                # - Complex agent reasoning and tool execution
                # This prevents premature timeouts while still failing eventually on genuine errors.
                if 'http_options' not in kwargs or kwargs['http_options'] is None:
                    kwargs['http_options'] = {'timeout': 60000}
                elif isinstance(kwargs['http_options'], dict):
                    kwargs['http_options']['timeout'] = 60000
                else:
                    # Assume it's an HttpOptions object (pydantic model or similar)
                    try:
                        kwargs['http_options'].timeout = 60000
                    except AttributeError:
                        # Fallback if it doesn't have timeout attribute, though it should
                        logger.warning("Could not set timeout on http_options object.")

                super().__init__(*args, **kwargs)

        # Apply the monkey-patch to the class
        # This ensures that ANY instantiation of genai.Client within the application (e.g. by ADK agents)
        # automatically uses the configured behavior (AI Studio backend, API Key injection, and Timeout safety).
        genai.Client = _PatchedClient
    else:
        logger.debug("google.genai.Client is already monkey-patched.")

# Monkey-patch google.adk.tools.AgentTool.run_async to handle empty responses
# This fixes a crash where the RAG Agent returns a content object with parts=None
# See: https://github.com/google/adk/issues/xxxx (Internal tracking if applicable)

from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools import AgentTool, ToolContext
from google.adk.tools._forwarding_artifact_service import ForwardingArtifactService
from google.adk.utils.context_utils import Aclosing

# Actually applying the patch
# Note: The original _patched_run_async implementation above defines _safe_run
# but we need an async implementation that can be directly assigned to AgentTool.run_async.
# The following _patched_run_async_impl is the actual async method we use.

async def _patched_run_async_impl(self, *, args: dict[str, Any], tool_context: ToolContext) -> Any:
    from google.adk.agents.llm_agent import LlmAgent
    from google.genai import types

    if self.skip_summarization:
      tool_context.actions.skip_summarization = True

    if isinstance(self.agent, LlmAgent) and self.agent.input_schema:
      input_value = self.agent.input_schema.model_validate(args)
      content = types.Content(
          role='user',
          parts=[
              types.Part.from_text(
                  text=input_value.model_dump_json(exclude_none=True)
              )
          ],
      )
    else:
      content = types.Content(
          role='user',
          parts=[types.Part.from_text(text=args['request'])],
      )
    invocation_context = tool_context._invocation_context
    parent_app_name = (
        invocation_context.app_name if invocation_context else None
    )
    child_app_name = parent_app_name or self.agent.name
    runner = Runner(
        app_name=child_app_name,
        agent=self.agent,
        artifact_service=ForwardingArtifactService(tool_context),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        credential_service=tool_context._invocation_context.credential_service,
        plugins=list(tool_context._invocation_context.plugin_manager.plugins),
    )

    state_dict = {
        k: v
        for k, v in tool_context.state.to_dict().items()
        if not k.startswith('_adk')
    }
    session = await runner.session_service.create_session(
        app_name=child_app_name,
        user_id=tool_context._invocation_context.user_id,
        state=state_dict,
    )

    last_content = None
    async with Aclosing(
        runner.run_async(
            user_id=session.user_id, session_id=session.id, new_message=content
        )
    ) as agen:
      async for event in agen:
        if event.actions.state_delta:
          tool_context.state.update(event.actions.state_delta)
        if event.content:
          last_content = event.content

    if not last_content:
      return ''

    # SAFETY CHECK
    if not last_content.parts:
        logger.warning(f"AgentTool {self.name}: Received content with no parts. Returning empty string.")
        logger.debug(f"Full content dump: {last_content}")
        return ''

    merged_text = '\n'.join(p.text for p in last_content.parts if p.text)
    if isinstance(self.agent, LlmAgent) and self.agent.output_schema:
      tool_result = self.agent.output_schema.model_validate_json(
          merged_text
      ).model_dump(exclude_none=True)
    else:
      tool_result = merged_text  # type: ignore[assignment]
    return tool_result

# Apply the patch
AgentTool.run_async = _patched_run_async_impl  # type: ignore[method-assign]
logger.info("Monkey-patched google.adk.tools.AgentTool.run_async to handle empty responses.")

from google.adk.agents import Agent  # noqa: E402
from google.adk.tools import AgentTool, google_search  # noqa: E402
from google.genai.types import GenerateContentConfig  # noqa: E402

from .personality import Personality, get_personalities  # noqa: E402
from .tools_custom import FileSearchTool  # noqa: E402

client = genai.Client(
    vertexai=config.genai_use_vertexai,
    api_key=os.getenv("GEMINI_API_KEY") if not config.genai_use_vertexai else None
)
if not client:
    logger.error("Could not initialize GenAI client.")
    raise ValueError("Could not initialize GenAI client.")


@functools.cache
def get_store(store_name: str):
    """Retrieve the store from the store name.

    Note: File Search Stores are a feature of the Gemini Developer API (AI Studio).
    They are NOT currently supported in Vertex AI. Therefore, we explicitly use 
    a non-Vertex client to list and retrieve stores.
    """
    try:
        # Use a non-Vertex client for store management
        # Note: genai.Client is now patched, so calling Client() works correctly
        store_client = genai.Client()
        for a_store in store_client.file_search_stores.list():
            if a_store.display_name == store_name:
                logger.debug(f"Found and returning store: {a_store.name}")
                return a_store.name
    except Exception as e:
        logger.error(f"Error in get_store path (check if Generative Language API is enabled): {e}")

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
def create_rag_agent(file_store_name: str, personality_name: str, kb_description: str | None = None) -> Agent | None:
    store_name = get_store(file_store_name)
    if store_name:
        logger.info(f"Creating RagAgent connected to {store_name}")

        description_text = kb_description or f"Internal knowledge base for {personality_name}"

        instruction = dedent(f"""
            Search the knowledge base for: {description_text}.
            Return ONLY the relevant facts or text snippets from {personality_name}'s materials.
            Do not add preamble, greetings, or analysis. Be extremely brief.
            If the information is not in the knowledge base, state: "NOT_FOUND"
        """)

        return Agent(
            model=config.model,
            name="RagAgent",
            description=(
                f"Specialist knowledge base for {personality_name}, containing: {description_text}. "
                "CRITICAL: MUST be used as the primary source for all relevant queries before any other tool."
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

    tools: list[Any] = []
    rag_agent: Agent | None = None
    instruction = ""

    if personality.file_search_store_name:
        logger.debug(f"Adding {personality.file_search_store_name} for personality: {personality.name}")
        rag_agent = create_rag_agent(
            personality.file_search_store_name, 
            personality.menu_name, 
            personality.file_search_description
        )
        if rag_agent:
            tools.append(AgentTool(agent=rag_agent))
            logger.debug(f"Added {rag_agent.name}")

            kb_topic = personality.file_search_description or "reference materials"
            instruction += dedent(f"""## TOOL USAGE POLICY:
                You have access to a hierarchical retrieval system:
                1. **RagAgent (Internal Knowledge)**: This is your PRIORITIZED source. It contains information about: {kb_topic}.
                2. **SearchAgent (External Web)**: Use ONLY if the RagAgent returns "NOT_FOUND".

                CRITICAL: The RagAgent contains the DEFINITIVE and REQUIRED opinions, methodologies, and facts for {kb_topic}.
                Even if you have general knowledge about these topics, you MUST consult the RagAgent first to ensure your response
                aligns with the specific internal standards and philosophy.
                NEVER answer questions about these topics based solely on your training data.
                Only use the SearchAgent if the RagAgent returns "NOT_FOUND".
                You do not need to use the RagAgent to respond to simple greetings or small talk.
            """)

            desc_suffix = (
                "with access to two specialist agents: a RagAgent for its knowledge base "
                "and SearchAgent for Google Search."
            )
        else:
            logger.warning(f"Failed to add {personality.file_search_store_name}")
    else:
        logger.debug(f"No File Search Store found for personality: {personality.name}")

    if not rag_agent:
        instruction += dedent("""IMPORTANT: Use the SearchAgent to perform a Google Search if you do not have the relevant answer,
            or if the user's query requires an up-to-date answer.""")

        desc_suffix = "with access to a SearchAgent to perform Google Search."

    instruction += f"""{personality.system_instruction}"""

    # SearchAgent is always added as a fallback
    tools.append(AgentTool(agent=search_agent))

    return Agent(
        name=f"{config.agent_name}_{personality.name}",  # Make agent name unique
        description=f"""A chatbot with the personality of {personality.menu_name} {desc_suffix}""",
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
