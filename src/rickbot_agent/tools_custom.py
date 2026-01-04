"""
Custom Tools for Rickbot Agent.

This module defines custom tools compatible with the Google Agent Development Kit (ADK).
Specifically, it implements the `FileSearchTool`.

What it does:
    It acts as a middleware tool that intercepts the LLM request before it is sent
    to the model. It injects the specific `file_search` configuration (referencing a
    File Search Store ID) directly into the `tools` parameter of the Gemini API request.

Why we need it:
    The standard ADK library provides easy access to Python functions and Google Search,
    but we need a way to attach a persistent Gemini File Search Store (created in AI Studio)
    to our agent. This custom tool allows us to pass that specific store ID to the model,
    enabling RAG (Retrieval-Augmented Generation) capabilities using the native Gemini
    File Search feature.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from google.adk.tools import BaseTool, ToolContext
from google.genai import types

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
