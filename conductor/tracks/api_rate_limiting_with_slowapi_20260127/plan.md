# Plan: API Rate Limiting with slowapi

This plan outlines the steps to implement API rate limiting in the Rickbot-ADK backend using `slowapi`.

## Phase 1: Foundation & Configuration [checkpoint: 25225bb]
Goal: Add `slowapi` dependency and set up the basic rate limiting infrastructure.

- [x] Task: Add slowapi to pyproject.toml dependencies. 188d542
- [x] Task: Create a central limiter instance in `src/rickbot_utils/` or a new utils module. 785d220
- [x] Task: Implement a custom key function to identify users (User ID from JWT or IP). 2c0f07d
- [x] Task: Integrate the `Limiter` middleware into the FastAPI application in `src/main.py`. d571855
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Configuration' (Protocol in workflow.md)

## Phase 2: Global & Specific Limits [checkpoint: 264f122]
Goal: Apply the defined rate limit policies to the API endpoints.

- [x] Task: Apply the global default rate limit (60/minute) to the FastAPI app. c6ebc19
- [x] Task: Identify all LLM-related endpoints in the codebase. (Found: `/chat`, `/chat_stream`) b665ffc
- [x] Task: Apply specific stricter limits (5/minute) to LLM endpoints using decorators. f521c48
- [x] Task: Ensure the `429` error response is correctly handled and formatted. 1bbc070
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Global & Specific Limits' (Protocol in workflow.md)

## Phase 3: Verification & Documentation
Goal: Verify the implementation with tests and ensure it meets project standards.

- [x] Task: Write unit tests to verify the identifier extraction (IP vs User ID). 2c0f07d
- [x] Task: Write integration tests to simulate rate limit exhaustion and verify `429` responses. c6ebc19
- [x] Task: Verify that `Retry-After` headers are present in `429` responses. 1bbc070
- [x] Task: Update `README.md` and `docs/design.md` with rate limiting details. fecdded
- [ ] Task: Run full linting, type checks, and spelling checks.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification & Documentation' (Protocol in workflow.md)
