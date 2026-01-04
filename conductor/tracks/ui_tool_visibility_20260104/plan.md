# Plan: UI Tool Execution Visibility

This plan outlines the steps to implement real-time tool execution visibility in the Rickbot-ADK Next.js frontend.

## Phase 1: Backend Event Propagation (FastAPI & ADK) [checkpoint: 6a0fe65]
Goal: Ensure the backend correctly emits tool execution events that the frontend can consume.

- [x] Task: Review ADK event system for tool calls. 7c7b242
- [x] Task: Update FastAPI endpoint to stream tool execution events alongside response chunks. 455e3c5
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend Event Propagation (FastAPI & ADK)' (Protocol in workflow.md)

## Phase 2: Frontend State Management & Event Handling
Goal: Update the Next.js frontend to handle and store tool execution events.

- [ ] Task: Define TypeScript interfaces for tool execution events.
- [ ] Task: Update the chat streaming logic to parse and handle tool execution events.
- [ ] Task: Implement state management (e.g., React state) to track the "current active tool".
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend State Management & Event Handling' (Protocol in workflow.md)

## Phase 3: UI Implementation (Thinking Component)
Goal: Update the UI to display the tool information.

- [ ] Task: Create or update the `Thinking` component to display tool name, action, and icon.
- [ ] Task: Map ADK tool names to specific icons and descriptive verbs.
- [ ] Task: Ensure smooth transitions between different tools and the final response.
- [ ] Task: Style the tool status to match the "Portal Green" theme.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: UI Implementation (Thinking Component)' (Protocol in workflow.md)

## Phase 4: Final Verification & Cleanup
Goal: Ensure everything works as expected and meets quality standards.

- [ ] Task: Verify end-to-end flow with various tool-using agents (e.g., Rick with search).
- [ ] Task: Ensure mobile responsiveness of the updated "Thinking" state.
- [ ] Task: Run full linting, type checks, and tests.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Verification & Cleanup' (Protocol in workflow.md)
