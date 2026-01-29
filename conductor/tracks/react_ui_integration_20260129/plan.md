# Implementation Plan - React UI Integration

## Phase 1: Authentication Refactoring
- [ ] Task: Create `auth_service.py` in `rickbot_agent` to handle OAuth flows (Google & GitHub) using `Authlib`.
    - [ ] Create `AuthService` class.
    - [ ] Implement `login` method for redirecting to providers.
    - [ ] Implement `callback` method for handling OAuth callbacks and token exchange.
- [ ] Task: Update `main.py` to expose auth endpoints.
    - [ ] Add `/api/auth/login/{provider}` endpoint.
    - [ ] Add `/api/auth/callback/{provider}` endpoint.
- [ ] Task: Write tests for `AuthService` and new endpoints.
- [ ] Task: Conductor - User Manual Verification 'Authentication Refactoring' (Protocol in workflow.md)

## Phase 2: Frontend Refactoring for Static Export
- [ ] Task: Update Next.js configuration for static export.
    - [ ] Modify `next.config.js` to set `output: 'export'`.
    - [ ] Update build scripts in `package.json`.
- [ ] Task: Replace `next-auth` in frontend with custom auth hook.
    - [ ] Remove `next-auth` dependency.
    - [ ] Create `useAuth` hook to manage session state (reading cookies/tokens from backend).
    - [ ] Update `AuthButton.tsx` and other components to use `useAuth`.
- [ ] Task: Verify frontend works with backend auth.
- [ ] Task: Conductor - User Manual Verification 'Frontend Refactoring for Static Export' (Protocol in workflow.md)

## Phase 3: Backend Static Serving & Configuration
- [ ] Task: Update `main.py` to serve static files.
    - [ ] Import `StaticFiles` from `fastapi.staticfiles`.
    - [ ] Mount the static directory to `/`.
    - [ ] Implement a catch-all route to serve `index.html` for client-side routing.
- [ ] Task: Implement `UI_MODE` toggle.
    - [ ] Create `run.py` or entrypoint script.
    - [ ] Logic: If `UI_MODE=react`, run FastAPI with static files.
    - [ ] Logic: If `UI_MODE=streamlit`, run Streamlit command.
- [ ] Task: Conductor - User Manual Verification 'Backend Static Serving & Configuration' (Protocol in workflow.md)

## Phase 4: Container Optimization
- [ ] Task: Update `Dockerfile` for multi-stage build.
    - [ ] Add `frontend-builder` stage (Node.js) to build Next.js app.
    - [ ] Update final stage to copy `out/` directory from `frontend-builder` to `src/static`.
    - [ ] Update `CMD` to use the new entrypoint script.
- [ ] Task: Verify container build and startup time.
- [ ] Task: Conductor - User Manual Verification 'Container Optimization' (Protocol in workflow.md)

## Phase 5: Documentation Updates
- [ ] Task: Update `README.md` with new build/run instructions.
- [ ] Task: Update `deployment/README.md` regarding the new container structure.
- [ ] Task: Update `docs/design.md` to reflect the architectural shift (No Node.js runtime).
- [ ] Task: Update `docs/nextui_walkthrough.md` to explain the static export and auth changes.
- [ ] Task: Conductor - User Manual Verification 'Documentation Updates' (Protocol in workflow.md)
