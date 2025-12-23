# Next.js UI Implementation Walkthrough

Here I summarise the goals, design decisions, and implementation relating to implementing the modern React/Next.js-based frontend to the Rickbot-ADK application.

## 1. Goals

The primary objective of this branch was to evolve the application from a rapid prototype (Streamlit) to a production-grade architecture using robust, scalable technologies.

*   **Modernise the UX**: Replace the functional but limited Streamlit interface with a responsive, customized UI using **Next.js** and **Material UI (MUI)**.
*   **Decouple Configuration**: Ensure the frontend is not hardcoded. Available personalities should be driven dynamically by the backend, allowing for easier updates without redeploying the UI.
*   **Enhance Performance**: Implement true streaming responses using Server-Sent Events (SSE) for a fluid conversational experience.
*   **Prepare for Scale**: Establish a client-side architecture (React) that interacts with the backend solely via REST API, paving the way for future mobile or third-party integrations.

## 2. Architecture Changes

### Frontend (`src/nextjs_fe`)
We introduced a structured Next.js application to serve as the new frontend.

*   **Framework**: Next.js 14+ (App/Pages router).
*   **Styling**: Material UI (MUI) for a polished, dark-mode "Rick and Morty" aesthetic.
*   **State Management**: React `useState` and `useEffect` hooks manage the chat history, streaming buffer, and personality list.

### Backend (`src/main.py`)
The existing FastAPI backend was enhanced to support the needs of the new frontend.

*   **New Endpoint**: `GET /personas`
    *   Returns the list of available agent personalities (name, description, avatar) defined in `src/rickbot_agent/data/personalities.yaml`.
    *   This eliminates the need for the frontend to maintain a duplicate hardcoded list of characters.
*   **Improved Streaming**: The `/chat_stream` endpoint was audited to ensure robust Server-Sent Events (SSE) compliance, enabling real-time token streaming to the browser.

## 3. Implementation Details

### Dynamic Persona Loading
One of the key achievements is the removal of hardcoded configuration from the UI.

1.  **Backend Source of Truth**: The `get_personalities()` helper in `src/rickbot_agent/personality.py` reads the YAML configuration.
2.  **API Exposure**: `src/main.py` wraps this data in a new `Persona` Pydantic model and serves it via `GET /personas`.
3.  **Frontend Consumption**:
    *   The `Chat.tsx` component uses a `useEffect` hook to fetch this list on mount.
    *   The "Personality" dropdown is populated dynamically.
    *   If a new personality is added to the backend YAML, it automatically appears in the UI upon refresh.

### Real-Time Chat Streaming
The chat interface handles asynchronous communication with the agent:

1.  **User Input**: The user sends a message (and optionally a file).
2.  **POST Request**: The frontend sends a `POST` request to `/chat_stream`.
3.  **SSE Consumption**:
    *   The browser uses the `ReadableStream` API (via `response.body.getReader()`) to process chunks as they arrive.
    *   A custom loop decodes these chunks and appends them to the current message in real-time, creating the "typing" effect.

## 4. Testing & Verification

*   **Unit Tests**: Added `src/tests/unit/test_api_personas.py` to verify the `/personas` endpoint returns the correct structure and data types.

## 5. Future Considerations

*   **Authentication**: Implementing a secure OAuth flow for the React app (likely using NextAuth.js or Google Identity Services) to match the security of the Streamlit prototype.
*   **Deployment**: Updating the `cloudbuild.yaml` and Terraform scripts to deploy the Next.js container alongside the API and Streamlit containers.
