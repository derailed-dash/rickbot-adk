# Implementation Plan - Persona Metadata Integration

## Phase 1: Backend API Enhancement
- [ ] Task: Update the `Persona` Pydantic model in `src/main.py` to include `title`, `overview`, `welcome`, and `prompt_question` fields.
- [ ] Task: Update the `get_personas` endpoint handler in `src/main.py` to populate these new fields from the loaded personality data.
- [ ] Task: Write Tests: Update `src/tests/unit/test_api_personas.py` to verify the `/personas` endpoint returns the new fields.
- [ ] Task: Conductor - User Manual Verification 'Backend API Enhancement' (Protocol in workflow.md)

## Phase 2: Frontend Data Model & Input Placeholder
- [ ] Task: Update the `Personality` interface in `src/nextjs_fe/components/Chat.tsx` to match the new API response structure.
- [ ] Task: Update `handleSendMessage` and input logic to use `selectedPersonality` data directly for the placeholder.
- [ ] Task: Modify the input `TextField` placeholder to bind to `selectedPersonality.prompt_question`.
- [ ] Task: Conductor - User Manual Verification 'Frontend Data Model & Input Placeholder' (Protocol in workflow.md)

## Phase 3: Frontend Profile UI
- [ ] Task: Design and implement a `PersonaProfile` component (or integrated Box) within `Chat.tsx`.
- [ ] Task: Integrate the `title` and `overview` fields into the profile area.
- [ ] Task: Integrate the `welcome` message into the profile area.
- [ ] Task: Ensure the layout is responsive and visually consistent with the dark theme.
- [ ] Task: Conductor - User Manual Verification 'Frontend Profile UI' (Protocol in workflow.md)
