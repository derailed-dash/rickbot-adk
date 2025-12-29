# Specification: Next.js UI Parity & Artifacts

## Overview
This track aims to bring the Next.js frontend to functional parity with the existing Streamlit implementation and enhance it with "production-ready" features. Key goals include adding missing functionality (Clear Chat, Tool Usage), implementing a public Privacy Policy page, and establishing a robust pattern for handling and displaying uploaded media using ADK Artifacts.

## Functional Requirements

### 1. Functional Parity
- **Clear Chat:**
    -   Add a "Clear Chat" button/action to the UI.
    -   Clicking this must reset the conversation session on both the frontend and backend (generating a new session ID).
- **Tool Usage Display:**
    -   The UI must visually indicate when the agent is using a tool (e.g., "Searching Google...", "Generating Image...").
    -   This should use the existing intermediate step data from the ADK/FastAPI response.

### 2. Public Pages
- **Privacy Policy:**
    -   Create a new page at `/privacy`.
    -   This page MUST be accessible without authentication (publicly available).
    -   The design must match the overall application theme.
    -   Content should be a placeholder or copied from the existing implementation if available.

### 3. ADK Artifacts & Media Handling
- **Research & Design:**
    -   Investigate best practices for integrating ADK Artifacts with a FastAPI backend.
    -   Propose a solution for uploading files (images, videos) and creating ADK artifacts.
- **Inline Display:**
    -   The chat interface must render uploaded media "inline" within the message history.
    -   **Images/Video:** Displayed directly (thumbnails or full view).
    -   **Other Files:** Displayed as "easily viewable" links or cards.

## Non-Functional Requirements
- **UX/UI:** All new features must align with the existing Material/Tailwind design system.
- **Performance:** Media loading should be optimized (lazy loading where appropriate).
- **Code Quality:** All new components must include unit tests.

## Out of Scope
- Full implementation of *every* possible file type rendering (focus on Images/Video first).
- Major redesign of the existing chat interface beyond the specified additions.
