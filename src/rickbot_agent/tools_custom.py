"""
Defines a custom tool for running Gemini File Search (RAG) queries inside 
the Google Agent Development Kit (ADK).

What it does:
    It acts as a middleware tool that intercepts the LLM request before it is sent
    to the model. It injects the specific `file_search` configuration (referencing a
    File Search Store ID) directly into the `tools` parameter of the Gemini API request.

Why we need it:
    The google.adk.tools library currently includes helpers for GoogleSearch,
    CodeExecution, and VertexAISearch, but it does not yet have a native FileSearch wrapper.
    We need a way to attach a persistent Gemini File Search Store (created in AI Studio)
    to our agent. 

    File Search is a server-side tool (executed by the model/Gemini API, not the client code).
    To use it, the specific tools configuration must be present in the 
    GenerateContentConfig of the request.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from google.adk.tools import BaseTool, ToolContext
from google.genai import types

# We only use LlmRequest for type hints, so we can hide it from runtime
if TYPE_CHECKING:
    from google.adk.models import LlmRequest

logger = logging.getLogger(__name__)


class FileSearchTool(BaseTool):
    """
    A custom ADK tool that enables the Gemini File Search (retrieval) capability.
    This attaches the native 'file_search' tool configuration to the model request.
    """

    def __init__(self, file_search_store_names: list[str]):
        """
        Initialize the FileSearchTool.

        Args:
            file_search_store_names: The resource name of the File Search Store.
                    e.g. ["fileSearchStores/mystore-abcdef0pqrst", ...]
        """
        super().__init__(name="file_search", description="Retrieval from file search store")
        self.file_search_store_names = file_search_store_names

    async def process_llm_request(
        self,
        *,
        tool_context: ToolContext,
        llm_request: LlmRequest,
    ) -> None:
        """
        Updates the model request configuration to include the File Search tool.
        """
        logger.debug(f"Attaching File Search Store: {self.file_search_store_names}")

        llm_request.config = llm_request.config or types.GenerateContentConfig()
        llm_request.config.tools = llm_request.config.tools or []

        # Append the native tool configuration for File Search
        llm_request.config.tools.append(
            types.Tool(file_search=types.FileSearch(file_search_store_names=self.file_search_store_names))
        )
        logger.debug("FileSearchTool configuration attached successfully.")

    def run(self, **args: Any) -> Any:
        """
        This should not be called for server-side tools, but if the model hallucinates a call
        or the ADK runner tries to execute it, we log it and return a placeholder.
        """
        logger.warning(f"FileSearchTool.run() was unexpectedly called with args: {args}")
        return "File Search is a server-side tool. Please check the citations in the response."

    async def run_async(self, **args: Any) -> Any:
        """Async version of run."""
        logger.warning(f"FileSearchTool.run_async() was unexpectedly called with args: {args}")
        return "File Search is a server-side tool. Please check the citations in the response."
