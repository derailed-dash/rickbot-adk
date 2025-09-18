# Rickbot-ADK Refactoring and Deployment Strategy

This document summarizes the strategic plan for refactoring the Rickbot-ADK project to a scalable, decoupled architecture using Vertex AI Agent Engine.

## 1. Executive Summary

The goal is to evolve Rickbot-ADK into a modern, stateful agent architecture by separating the frontend and backend.

- **Backend (The Agent):** A single, dynamic agent will be deployed to **Vertex AI Agent Engine**. It will use `VertexAiSessionService` for conversation memory and `VertexAiSearchTool` to query a knowledge base created with `VertexAiMemoryBankService`.
- **Frontend (The UI):** The Streamlit application will be refactored into a pure client, deployed to **Cloud Run**, and will communicate with the backend via API calls.

## 2. Key Architectural Decisions

- **Session Management:** Switch from `InMemorySessionService` to the managed `VertexAiSessionService` provided by Agent Engine for persistent, multi-turn conversations.
- **Knowledge Management:** Use `VertexAiMemoryBankService` to create and manage knowledge bases from private documents (e.g., PDFs) for specific personalities. The agent will access this knowledge at runtime using the `VertexAiSearchTool`.
- **Agent Architecture:** Move from separate agent instances per personality to a **single, dynamic agent**. The agent's behavior (prompt, temperature, tools) will be controlled by a `personality` value stored in the `session.state`.

## 3. Detailed Action Plan

### Phase 1: Backend Refactoring & Knowledge Base Setup

1.  **Update Dependencies:** Add `google-cloud-aiplatform[adk,agent_engines]` to `pyproject.toml`.
2.  **Create Knowledge Base:**
    -   Write a setup script (`scripts/provision_memory.py`).
    -   Use `VertexAiMemoryBankService` to create a data store from reference documents.
    -   Capture the resulting `data_store_id`.
3.  **Refactor Agent for Dynamic Personalities:**
    -   Modify the agent to read `session.state.get("personality")` on each turn.
    -   Dynamically load the system prompt, temperature, and tools based on the active personality.
    -   Equip relevant personalities with the `VertexAiSearchTool`, configured with the `data_store_id`.
4.  **Create `set_personality` Tool:**
    -   Implement a tool that takes a `personality_name` and updates the `session.state["personality"]`.

### Phase 2: Deployment & Configuration

1.  **Create Agent Deployment Script:**
    -   Write a script (`deploy_agent.py`) to deploy the refactored agent to Agent Engine using `agent_engines.create()`.
    -   Capture the deployed agent's `resource_name` (its API endpoint).
2.  **Configure Authentication (IAM):**
    -   Grant the Cloud Run service account the "Vertex AI User" role to allow it to invoke the Agent Engine endpoint.

### Phase 3: Frontend Refactoring

1.  **Implement an Agent Engine Client:**
    -   Create a new client module in the Streamlit code.
    *   This client will connect to the remote agent using its `resource_name` (read from an environment variable).
    -   It will wrap API calls like `create_session` and `stream_query`.
2.  **Update UI Logic:**
    -   Remove the local `Runner` and `InMemorySessionService` instantiation from the UI code.
    -   Update the chat interface to use the new Agent Engine client.
    -   When a user selects a personality, the UI will call the agent's `set_personality` tool.

### Phase 4: Verification

1.  **Direct API Test:** Write a script to test the deployed agent endpoint directly, verifying session persistence and knowledge retrieval.
2.  **End-to-End Test:** Deploy the refactored Streamlit frontend to Cloud Run and conduct a full user journey to ensure all components work together seamlessly.
