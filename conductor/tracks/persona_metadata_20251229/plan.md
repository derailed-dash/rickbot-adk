# Implementation Plan - Persona Metadata Integration

## Phase 1: Backend API Enhancement [checkpoint: 2c1cbdc]
- [x] Task: Update the `Persona` Pydantic model in `src/main.py` to include `title`, `overview`, `welcome`, and `prompt_question` fields. 459d615
- [x] Task: Update the `get_personas` endpoint handler in `src/main.py` to populate these new fields from the loaded personality data. 459d615
- [x] Task: Write Tests: Update `src/tests/unit/test_api_personas.py` to verify the `/personas` endpoint returns the new fields. 459d615
- [x] Task: Conductor - User Manual Verification 'Backend API Enhancement' (Protocol in workflow.md) 2c1cbdc

## Phase 2: Frontend Data Model & Input Placeholder
- [x] Task: Update the `Personality` interface in `src/nextjs_fe/components/Chat.tsx` to match the new API response structure. 4765a71
- [x] Task: Update `handleSendMessage` and input logic to use `selectedPersonality` data directly for the placeholder. 4765a71
- [x] Task: Modify the input `TextField` placeholder to bind to `selectedPersonality.prompt_question`. 4765a71
- [x] Task: Conductor - User Manual Verification 'Frontend Data Model & Input Placeholder' (Protocol in workflow.md) 4765a71

## Phase 3: Frontend Profile UI
- [x] Task: Design and implement a `PersonaProfile` component (or integrated Box) within `Chat.tsx`. 4765a71
- [x] Task: Integrate the `title` and `overview` fields into the profile area. 4765a71
- [x] Task: Integrate the `welcome` message into the profile area. 4765a71
- [x] Task: Ensure the layout is responsive and visually consistent with the dark theme. 4765a71
- [x] Task: Conductor - User Manual Verification 'Frontend Profile UI' (Protocol in workflow.md) 4765a71
