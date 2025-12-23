# Rickbot-ADK Design Documentation

## Overall Purpose

**Rickbot-ADK** represents the evolution of the original "Rickbot" chatbot into a sophisticated, multi-agent system. Its primary purposes are:

1.  **Platform Demonstration**: To serve as a reference implementation for creating advanced agents using the **Google Agent Development Kit (ADK)**, **Gemini CLI**, and the **Agent-Starter-Pack**.
2.  **Multi-Personality Architecture**: To demonstrate how to build a flexible agent architecture capable of robustly switching between distinct personas (e.g., Rick Sanchez, Yoda, Dazbot) while maintaining conversational coherence.

## Solution Design

The solution is architected as a cloud-native application running on Google Cloud, leveraging Vertex AI / Gemini for intelligence. It is containerised and can be deployed onto Google Cloud Run for compute.

### High-Level Architecture

```mermaid
graph TD
    User([User])
    
    subgraph "Interfaces"
        Streamlit[Streamlit UI\n(Existing)]
        React[React/Next.js UI\n(Planned)]
    end
    
    subgraph "Google Cloud Platform"
        LB[Load Balancer / Ingress]
        
        subgraph "Cloud Run Services"
            API[FastAPI Backend\n(Rickbot Agent)]
        end
        
        subgraph "Data & State"
            AlloyDB[(AlloyDB\nSession History)]
            GCS[Cloud Storage\nArtifacts/Logs]
            SecretMgr[Secret Manager\nOAuth Creds / API Keys]
        end
        
        subgraph "AI Services"
            Vertex[Vertex AI Agent Engine]
            Gemini[Gemini 1.5 Pro/Flash]
        end
    end

    User --> Streamlit
    User --> React
    
    Streamlit --> API
    React --> API
    
    API -->|ADK Framework| Vertex
    API -->|Store/Retrieve| AlloyDB
    API -->|Fetch Secrets| SecretMgr
    
    Vertex -->|Inference| Gemini
```

### Products and Services Used

*   **Hosting Services**:
    *   **Google Cloud Run**: Hosts both the generic API backend and the Streamlit frontend container. It provides a serverless, scalable environment. Cloud Run also offers a native domain name mapping feature to map custom domains to our Cloud Run services. Note that any custom domains used must be added to the OAuth authorised domains and authorised redirect URIs. 
*   **Agentic Services**:
    *   **Vertex AI Agent Engine**: The core runtime for the agent.
    *   **Google Gemini Models**: The underlying Large Language Models (LLMs) driving the personalities (e.g., `gemini-2.5-flash`).
    *   **Google Agent Development Kit (ADK)**: Provides the standardized framework for agent state management, pattern implementation, and multi-turn conversation handling.
*   **API Layer**:
    *   **FastAPI**: Powers the backend API, exposing RESTful endpoints.
*   **Frontend**:
    *   **Streamlit**: Powers the current frontend user interface for rapid prototyping.
    *   **Next.js / React (Planned)**: The framework for the future modern UI.
*   **Auth**:
    *   **Google Auth Platform**: Handles OAuth 2.0 authentication for users.
*   **Data, Infrastructure & Tools**:
    *   **Google Cloud Storage (GCS)**: Stores unstructured data, logs, and generated artifacts.
    *   **Secret Manager**: Securely stores sensitive configuration like OAuth client IDs and API keys.
    *   **Terraform**: Manages all infrastructure provisioning.
    *   **Google Cloud Build**: Orchestrates the CI/CD pipeline for testing and deployment.

## Design Decisions

### 1. Adopting the Agent Development Kit (ADK)

*   **Decision**: Migrate from custom Python logic to the Google ADK.
*   **Rationale**: The original Rickbot used ad-hoc state management which became brittle. ADK provides robust, standardized patterns for session handling, tool calling, and context management, making the system easier to extend and maintain.

### 2. Decoupling the API (FastAPI)

*   **Decision**: Expose the agent's functionality via a standalone FastAPI service (`src/main.py`), rather than embedding it tightly within the UI code.
*   **Rationale**: This follows the "Backend for Frontend" (BFF) pattern conceptually but allows multiple interfaces to coexist. It enables the development of the planned React/Next.js UI without modifying the core agent logic and allows third-party integrations (e.g., Slack bot, mobile app) in the future.

### 3. Streamlit for Initial UI

*   **Decision**: Use Streamlit for the first-generation user interface.
*   **Rationale**: Streamlit allows for extremely rapid prototyping using only Python. It was the fastest way to validate the ADK integration and multi-personality logic before investing in a more complex React frontend.

### 4. Runner Re-initialization for Context Isolation (Streamlit vs API)
*   **Decision**: Handle persona switching differently based on the interface's nature.
    *   **Streamlit (Stateful)**: Forces a full re-initialization of the ADK `Runner` instance when the selection changes. This guarantees zero "context leakage" for the stateful UI.
    *   **FastAPI (Stateless)**: Accepts a `personality` parameter on every request. The agent is strictly scoped to the individual request lifecycle.
*   **Rationale**: The Streamlit app simulates a continuous session with a specific character, requiring a hard reset to switch. The API is designed to be flexible and stateless, allowing a client to potentially mix-and-match or switch personalities instantly between calls without backend reconfiguration.

## User Interfaces (UIs)

The application supports multiple distinct interfaces, all interacting with the core agent logic.

### Streamlit UI (Existing)

The original user interface for rapid prototyping and demonstration. 
This UI is defined in `src/streamlit_fe/app.py` and can be launched with `make streamlit`.

Alternatively, we can launch it in a Docker container using `make docker-streamlit`.

*   **Technology**: Python, Streamlit.
*   **Features**:
    *   **Sidebar Navigation**: Allows users to select between different personalities.
    *   **Chat Interface**: A familiar chat-bubble layout for interacting with the agent.
    *   **Authentication**: Integrated OIDC authentication using Google Auth Platform.
    *   **State Management**: Handles session persistence locally within the Streamlit session state.

#### Handling Personality Changes in the Streamlit UI

The application is designed to ensure a clean and robust separation of context when switching between different chatbot personalities. The process is handled as follows:

1.  **UI Detection**: When a user selects a new personality from the sidebar dropdown in the Streamlit UI, the application immediately detects this change.
2.  **State Reset**: To prevent conversational context from leaking between personalities, the application clears the current chat history.
3.  **Application Rerun**: It then programmatically triggers a full rerun of the Streamlit application.
4.  **Runner Re-initialization**: During the rerun, the application logic detects that the personality has changed. This triggers the creation of a **brand new ADK `Runner` instance**.
5.  **New Agent Configuration**: The new `Runner` is configured with a fresh agent that embodies the newly selected personality. The old `Runner` instance is discarded and garbage-collected.

This approach ensures that each personality operates in a clean, isolated environment. It is a simple and robust pattern that aligns well with Streamlit's execution model, prioritizing a predictable state over the premature optimization of object re-creation.

### React/Next.js UI (Planned)

The future "North Star" interface for Rickbot.
*   **Technology**: TypeScript, React, Next.js, Material UI.
*   **Architecture**: Client-side application consuming the **FastAPI Backend**.
*   **Planned Features**:
    *   **Modern UX**: Enhanced aesthetics and responsiveness using Material UI (MUI).
    *   **Advanced Chat**: Richer message formatting and potential support for multimodal inputs (audio/video).
    *   **Optimized Performance**: leveraging Next.js server-side rendering (SSR) and static generation where appropriate.
    *   **Independent Auth**: Will implement its own OAuth flow (Google Identities) or use a sidecar pattern.

### API Backend

The central nervous system of the application. It is the primary entrypoint to the application is a FastAPI backend, defined in `src/main.py`. This provides a RESTful API that allows any client that can speak HTTP to interact with the Rickbot agent. This decoupled architecture allows for the development of custom user interfaces (such as a React-based web application) and enables other applications to integrate with Rickbot.

*   **Technology**: Python, FastAPI.
*   **Role**: Exposes the ADK agent as a set of RESTful endpoints.
*   **Capabilities**:
    *   Stateless/Stateful conversation handling (via ADK).
    *   Swagger/OpenAPI documentation auto-generation.
    *   Serves as the single source of truth for agent logic for all connected UIs.

### OAuth

Frontend user authentication is required for Rickbot.

#### OAuth with Streamlit

- With the Streamlit frontend this is achieved using Streamlit\'s integrated OIDC authentication. 
- We use Google Auth Platform as the OAuth2 Auth provider.
- OAuth credentials are obtained from the Google Auth Platform and stored in Google Secret Manager.
- When the application is first launched, these credentials are read and dynamically written to the `.streamlit/secrets.toml`, which is how the Streamlit OIDC works. We must supply the `oauth2callback` URI as well as the OAuth client ID and secret.
- Different credentials are used between Staging and Prod.
- When running locally we use an environment variable `MOCK_AUTH_USER` to bypass real authentication. This is automatically set by `make streamlit`.
