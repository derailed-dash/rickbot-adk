# Specification - Persona Metadata Integration

## Overview
Resolve the metadata parity gap between the React and Streamlit interfaces. Currently, the React frontend does not display persona-specific fields such as `title`, `overview`, `welcome`, and `prompt_question`, which are available in the backend configuration and used in the Streamlit version.

## Functional Requirements
1.  **Backend API Enhancement**:
    *   Update the `/personas` endpoint in `src/main.py` to include the additional fields (`title`, `overview`, `welcome`, `prompt_question`) in the response.
    *   Update the `Persona` Pydantic model in `src/main.py` to support these new fields.
2.  **React Frontend Updates**:
    *   **Data Model**: Update the `Personality` interface in `src/nextjs_fe/components/Chat.tsx` to include the new fields.
    *   **Persona Profile Area**: Implement a dedicated profile area (likely above the chat history or integrated into the header) that displays:
        *   The persona's `title`.
        *   The persona's `overview`.
        *   The persona's `welcome` message.
    *   **Dynamic Input Placeholder**: Update the chat input field's placeholder text to dynamically display the `prompt_question` of the currently selected persona.
    *   **Header Consistency**: Maintain "Rickbot" as the main header, displaying the persona `title` as a sub-header or within the new profile area.

## Non-Functional Requirements
*   **UI/UX**: Ensure the new profile area is visually consistent with the existing dark-themed Material UI design.
*   **Responsiveness**: The profile area should adapt well to different screen sizes.

## Acceptance Criteria
*   Selecting a persona in the React UI updates the profile area with the correct `title`, `overview`, and `welcome` text.
*   The input field placeholder correctly shows the `prompt_question` for the selected persona.
*   All data is fetched from the enhanced `/personas` endpoint.
*   "Rickbot" remains the primary header.

## Out of Scope
*   Adding new personas to the configuration.
*   Modifying the chat streaming or agent logic itself.
