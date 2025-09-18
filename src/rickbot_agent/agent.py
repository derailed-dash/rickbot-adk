"""
This module defines the main agent for the Rickbot-ADK application.
It initializes a single, dynamic, Google Gemini-powered agent that can adopt multiple personalities.
"""

from google.adk.agents import Agent
from google.adk.sessions import Session
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai.types import GenerateContentConfig, Tool

from .config import get_config, logger
from .personality import get_personalities

config = get_config()


class DynamicPersonalityAgent(Agent):
    """An agent that can dynamically switch personalities based on session state."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_personality(self, personality_name: str, session: Session):
        """
        The main execution method for the agent.
        It determines the personality from session state and runs the LLM.
        """
        # 1. Determine the active personality
        personalities = get_personalities()
        if ("personality_name" not in session.state # personality not set
                or session.state["personality_name"] != personality_name): # personality has changed

            logger.debug(f"Setting personality to: {personality_name}")
            retrieved_personality = personalities.get(personality_name)
            if retrieved_personality:
                session.state["personality_name"] = personality_name # Update the personality name in the session
            else:
                logger.error(f"Personality '{personality_name}' not found. Falling back to 'Rick'.")
                session.state["personality_name"] = "Rick"

            personality = personalities.get(session.state["personality_name"])
            assert personality is not None, "Personality should not be None at this point due to fallback logic."

            # 2. Apply personality dynamically
            self.instruction = personality.system_instruction
            self.generate_content_config = GenerateContentConfig(
                temperature=personality.temperature, 
                top_p=1, 
                max_output_tokens=8192
            )

        # # 3. Prepare for LLM call
        # # Prepend the system instruction to the conversation history
        # history = [Agent.to_genai_content(instruction, "system")] + session.events.to_parts()

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
    description="Agent to perform Google Search",
    instruction="You're a specialist in Google Search",
    tools=[google_search],
)

# Define the tools the agent will have access to.
# This includes the new tool for setting the personality.
agent_tools: list[Tool | FunctionTool | AgentTool] = [
    AgentTool(agent=search_agent)
]

# Instantiate the single, dynamic agent
root_agent = DynamicPersonalityAgent(
    name=config.agent_name,
    description="A multi-personality chatbot.",
    model=config.model,
    tools=agent_tools,
    output_key="last_turn_response",
)
