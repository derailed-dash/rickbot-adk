# Implementation Plan - Auth Track

## Phase 1: Backend Preparation [checkpoint: 1ca8411]
- [x] Task: Research and select FastAPI auth library (e.g., Authlib, FastAPI Users). [cb9e356]
- [x] Task: Create a basic `AuthUser` model/schema. [3e2e3dd]
- [x] Task: Implement a dependency for verifying mock tokens (for initial testing). [dbb7bc9]
- [x] Task: Write Tests: Unit tests for token verification logic. [dbb7bc9]
- [x] Task: Conductor - User Manual Verification 'Backend Preparation' (Protocol in workflow.md)

## Phase 2: Next.js Google Auth
- [x] Task: Install and configure NextAuth.js in the Next.js project. [4cd3efe]
- [x] Task: Configure Google OAuth provider credentials (env vars). [0e18776]
- [x] Task: Create a Login/Logout button component. [36b3686]
- [x] Task: Create a mechanism to allow mock user in local dev (similar to existing Streamlit approach) [71ee949]
- [~] Task: Implement a protected route/page that requires login.
- [ ] Task: Write Tests: Component tests for the Login button.
- [ ] Task: Conductor - User Manual Verification 'Next.js Google Auth' (Protocol in workflow.md)

## Phase 3: Connect Frontend to Backend
- [ ] Task: Update Next.js API calls to include the auth token in the Authorization header.
- [ ] Task: Update FastAPI backend to verify the actual Google/GitHub JWTs (replacing mock logic).
- [ ] Task: Write Tests: Integration test ensuring frontend can call protected API endpoint.
- [ ] Task: Conductor - User Manual Verification 'Connect Frontend to Backend' (Protocol in workflow.md)

## Phase 4: GitHub Auth & Final Polish
- [ ] Task: Add GitHub OAuth provider to NextAuth.js configuration.
- [ ] Task: Update Login component to support multiple providers.
- [ ] Task: Refactor API error handling for auth failures (ensure clean UI feedback).
- [ ] Task: Conductor - User Manual Verification 'GitHub Auth & Final Polish' (Protocol in workflow.md)
