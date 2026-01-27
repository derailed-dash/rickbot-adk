# Plan: API Rate Limiting with slowapi

This plan outlines the steps to implement API rate limiting in the Rickbot-ADK backend using `slowapi`.

## Phase 1: Foundation & Configuration
Goal: Add `slowapi` dependency and set up the basic rate limiting infrastructure.

- [ ] Task: Add `slowapi` to `pyproject.toml` dependencies.
- [ ] Task: Create a central `limiter` instance in `src/rickbot_utils/` or a new utils module.
- [ ] Task: Implement a custom key function to identify users (User ID from JWT or IP).
- [ ] Task: Integrate the `Limiter` middleware into the FastAPI application in `src/main.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Configuration' (Protocol in workflow.md)

## Phase 2: Global & Specific Limits
Goal: Apply the defined rate limit policies to the API endpoints.

- [ ] Task: Apply the global default rate limit (60/minute) to the FastAPI app.
- [ ] Task: Identify all LLM-related endpoints in the codebase.
- [ ] Task: Apply specific stricter limits (5/minute) to LLM endpoints using decorators.
- [ ] Task: Ensure the `429` error response is correctly handled and formatted.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Global & Specific Limits' (Protocol in workflow.md)

## Phase 3: Verification & Documentation
Goal: Verify the implementation with tests and ensure it meets project standards.

- [ ] Task: Write unit tests to verify the identifier extraction (IP vs User ID).
- [ ] Task: Write integration tests to simulate rate limit exhaustion and verify `429` responses.
- [ ] Task: Verify that `Retry-After` headers are present in `429` responses.
- [ ] Task: Update `README.md` and `docs/design.md` with rate limiting details.
- [ ] Task: Run full linting, type checks, and spelling checks.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification & Documentation' (Protocol in workflow.md)
