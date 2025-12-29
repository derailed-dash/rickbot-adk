# Implementation Plan - Unified Testing Documentation

## Phase 1: Documentation Scaffolding & Migration [checkpoint: 9364b0d]
- [x] Task: Create `docs/testing.md` and initialize the table of contents and structure.
- [x] Task: Migrate existing Python test guidance and configuration details from `src/tests/README.md`.
- [x] Task: Remove `src/tests/README.md` and ensure any references to it are updated.
- [x] Task: Conductor - User Manual Verification 'Documentation Scaffolding & Migration' (Protocol in workflow.md)

## Phase 2: Frontend Testing & Strategy [checkpoint: 1adfc79]
- [x] Task: Document the React/Next.js testing stack (Jest, React Testing Library) and execution steps.
- [x] Task: Document the general testing strategy, including Test Mode, `conftest.py`, and CI environment usage.
- [x] Task: Update the "Running Tests" section to clearly distinguish between Backend and Frontend commands.
- [x] Task: Conductor - User Manual Verification 'Frontend Testing & Strategy' (Protocol in workflow.md)

## Phase 3: Authentication & Manual Verification [checkpoint: aa16181]
- [x] Task: Create a step-by-step guide for retrieving a Bearer token from Browser Developer Tools.
- [x] Task: Document the usage of Mock Tokens (`mock:id:email:name`) for local development.
- [x] Task: Provide authenticated `curl` examples for all endpoints, specifically highlighting Artifact retrieval using `$AUTH_TOKEN`.
- [x] Task: Conductor - User Manual Verification 'Authentication & Manual Verification' (Protocol in workflow.md)

## Phase 4: Final Review & Integration
- [x] Task: Perform a final proofread of `docs/testing.md` for clarity and technical accuracy.
- [x] Task: Verify that all `curl` commands and shell snippets are correct and functional.
- [~] Task: Conductor - User Manual Verification 'Final Review & Integration' (Protocol in workflow.md)
