# Implementation Plan - Next.js UI Parity & Artifacts

## Phase 1: Research and Architecture [checkpoint: 87b6f09]
- [x] Task: Research ADK Artifacts usage with FastAPI and Next.js.
- [x] Task: Analyze current Streamlit media handling and gaps.
- [x] Task: Propose and document the Artifact/Media upload and retrieval architecture in `docs/design.md`.
- [x] Task: Conductor - User Manual Verification 'Research and Architecture' (Protocol in workflow.md)

## Phase 2: Public Pages & Base UI [checkpoint: 17ebb49]
- [x] Task: Create the Privacy Policy page (`/pages/privacy.tsx`) and ensure it's publicly accessible.
- [x] Task: Link the Privacy Policy page from the Login screen and Chat Footer.
- [x] Task: Implement the "Clear Chat" button and backend session reset logic.
- [x] Task: Write Tests: Unit tests for Clear Chat functionality and Privacy page accessibility.
- [x] Task: Documentation: Update `@src/tests/README.md` to include new test files and categories (e.g., Privacy, Clear Chat).
- [x] Task: Conductor - User Manual Verification 'Public Pages & Base UI' (Protocol in workflow.md)

## Phase 3: Tool Usage & Feedback [checkpoint: 0a9ff74]
- [x] Task: Update the FastAPI response to include tool execution status. [52493a9]
- [x] Task: Update the Next.js Chat component to display "Thinking/Tool Usage" states (e.g., "Searching Google...").
- [x] Task: Write Tests: Component tests for tool usage status display.
- [x] Task: Documentation: Update `@src/tests/README.md` with new component tests for tool usage.
- [x] Task: Conductor - User Manual Verification 'Tool Usage & Feedback' (Protocol in workflow.md)

## Phase 4: ADK Artifacts & Media Handling [checkpoint: 898f58b]
- [x] Task: Implement backend endpoints for file upload and Artifact creation. [ccbceb3]
- [x] Task: Update the Chat interface to support multi-file uploads.
- [x] Task: Implement inline rendering for Images and Video in the chat messages.
- [x] Task: Implement generic file cards for other "viewable" media types.
- [x] Task: Write Tests: Integration tests for file upload -> Artifact creation -> UI rendering.
- [x] Task: Documentation: Update `@src/tests/README.md` with new integration tests for artifacts and media handling.
- [x] Task: Conductor - User Manual Verification 'ADK Artifacts & Media Handling' (Protocol in workflow.md)
