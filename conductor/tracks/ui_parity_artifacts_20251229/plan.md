# Implementation Plan - Next.js UI Parity & Artifacts

## Phase 1: Research and Architecture [checkpoint: 87b6f09]
- [x] Task: Research ADK Artifacts usage with FastAPI and Next.js.
- [x] Task: Analyze current Streamlit media handling and gaps.
- [x] Task: Propose and document the Artifact/Media upload and retrieval architecture in `docs/design.md`.
- [x] Task: Conductor - User Manual Verification 'Research and Architecture' (Protocol in workflow.md)

## Phase 2: Public Pages & Base UI
- [ ] Task: Create the Privacy Policy page (`/pages/privacy.tsx`) and ensure it's publicly accessible.
- [ ] Task: Link the Privacy Policy page from the Login screen and Chat Footer.
- [ ] Task: Implement the "Clear Chat" button and backend session reset logic.
- [ ] Task: Write Tests: Unit tests for Clear Chat functionality and Privacy page accessibility.
- [ ] Task: Documentation: Update `@src/tests/README.md` to include new test files and categories (e.g., Privacy, Clear Chat).
- [ ] Task: Conductor - User Manual Verification 'Public Pages & Base UI' (Protocol in workflow.md)

## Phase 3: Tool Usage & Feedback
- [ ] Task: Update the FastAPI response to include tool execution status.
- [ ] Task: Update the Next.js Chat component to display "Thinking/Tool Usage" states (e.g., "Searching Google...").
- [ ] Task: Write Tests: Component tests for tool usage status display.
- [ ] Task: Documentation: Update `@src/tests/README.md` with new component tests for tool usage.
- [ ] Task: Conductor - User Manual Verification 'Tool Usage & Feedback' (Protocol in workflow.md)

## Phase 4: ADK Artifacts & Media Handling
- [ ] Task: Implement backend endpoints for file upload and Artifact creation.
- [ ] Task: Update the Chat interface to support multi-file uploads.
- [ ] Task: Implement inline rendering for Images and Video in the chat messages.
- [ ] Task: Implement generic file cards for other "viewable" media types.
- [ ] Task: Write Tests: Integration tests for file upload -> Artifact creation -> UI rendering.
- [ ] Task: Documentation: Update `@src/tests/README.md` with new integration tests for artifacts and media handling.
- [ ] Task: Conductor - User Manual Verification 'ADK Artifacts & Media Handling' (Protocol in workflow.md)
