# Specification: Containerization Refinement (React UI & API Backend)

## Overview
This track involves modularizing the Rickbot application's container strategy. We will create dedicated, optimized Dockerfiles for the React/Next.js frontend and the FastAPI backend. A new `docker-compose.yml` configuration will orchestrate these services alongside the existing Streamlit UI, facilitating a decoupled development environment that mirrors the planned production sidecar architecture.

## Functional Requirements
- **Backend Containerization:**
    - Create a new Dockerfile (e.g., `Dockerfile.api`) for the FastAPI backend.
    - Use a "Whitelist" approach: Copy only `src/main.py`, `src/rickbot_agent/`, and `src/rickbot_utils/`.
    - Ensure the image is optimized using a multi-stage build similar to the current production Dockerfile.
- **Frontend Containerization:**
    - Create `src/nextjs_fe/Dockerfile`.
    - Implement a multi-stage build (deps, builder, runner).
    - Ensure environment variables for the backend URL are correctly handled.
- **Orchestration:**
    - Update `docker-compose.yml` to include three services: `frontend` (React), `backend` (API), and `streamlit_fe`.
    - Configure service networking so `frontend` can communicate with `backend` using its service name.
- **Documentation:**
    - Update `README.md` with instructions for the new container setup.
    - Update `docs/design.md` to reflect the multi-container architecture.
    - Create `docs/containers.md`: A detailed, step-by-step walkthrough of the container architecture, build process, and local execution.

## Non-Functional Requirements
- **Optimization:** Use multi-stage builds to minimize image sizes.
- **Security:** Run all containers as non-root users.
- **Maintainability:** No significant code refactoring; authentication logic remains in its current location.
- **Consistency:** Follow existing naming conventions and style guides.

## Acceptance Criteria
- `docker compose build` succeeds for all three services.
- `docker compose up` successfully starts `frontend` (port 3000), `backend` (port 8080), and `streamlit_fe` (port 8501 or similar, ensuring no conflicts).
- The React UI can successfully fetch data from the API backend within the Docker network.
- `docs/containers.md` exists and provides a clear, blog-post-ready explanation of the containerization strategy.
- Existing tests pass within the containerized environment.

## Out of Scope
- Modifications to Terraform or Google Cloud Build configurations.
- Implementation of the sidecar pattern in Cloud Run (reserved for a future track).
- Changes to the authentication/authorization flow.
