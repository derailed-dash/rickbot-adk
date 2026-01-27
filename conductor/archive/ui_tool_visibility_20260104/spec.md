# Specification: UI Tool Execution Visibility

## Overview
Currently, the Next.js frontend shows a generic "Thinking..." status when the agent is processing a request. This track aims to enhance user transparency by displaying specific information about which tools the agent is currently using, including the tool name, a descriptive action, and a relevant icon, all within the existing "Thinking" state area.

## Functional Requirements
- **Dynamic Status Updates:** The "Thinking" component must be updated to listen for and display specific tool execution events from the backend (ADK).
- **Tool Details:** For each tool invocation, the UI must show:
    - **Visual Icon:** A tool-specific icon (e.g., search icon for Google Search).
    - **Action Verb:** A clear descriptive action (e.g., "Searching...", "Reading...").
    - **Tool Name:** The name of the tool being executed.
- **Sequential Tool Handling:** When multiple tools are used in sequence, the status area should dynamically update to show only the currently active tool.
- **Visual Integration:** The tool status should feel native to the existing "Portal Green" Rick and Morty themed UI, likely replacing or sitting alongside the existing animated "Thinking" indicator.

## Non-Functional Requirements
- **Responsiveness:** Tool updates should be reflected in the UI with minimal latency.
- **Accessibility:** Ensure that screen readers can convey the changing status of the agent.

## Acceptance Criteria
- [ ] The generic "Thinking..." text is replaced or augmented by "Tool Name: Action Verb" (e.g., "Google Search: Searching...") when a tool is active.
- [ ] A relevant icon is displayed next to the tool status.
- [ ] If multiple tools are called, the UI updates smoothly to show only the latest tool.
- [ ] Once tools are finished and the final response starts streaming, the status indicator disappears.

## Out of Scope
- Displaying full input/output payloads of tool calls.
- Historical logging of tool calls in the chat history.
- Manual intervention or "approval" UI for tool calls (this remains automated).
