# Specification: React UI Integration and Container Optimization

## Overview
This track aims to integrate the new React (Next.js) frontend into the primary container build, replacing or providing an alternative to the existing Streamlit UI. The goal is to produce a lightweight, fast-starting container suitable for serverless environments (like Cloud Run) by serving a static export of the React UI directly from the FastAPI backend. This involves significant architectural changes, including moving OAuth handling to the backend and updating deployment documentation.

## Functional Requirements
1.  **Static UI Export:** Configure the Next.js frontend for static HTML export (`next export`).
2.  **Backend Integration:** Update the FastAPI application to serve the static frontend files (HTML, CSS, JS) from a designated directory (e.g., `src/static`).
3.  **UI Mode Toggle:** Implement an environment variable `UI_MODE` (values: `react`, `streamlit`) that determines which interface is served/started by the container.
4.  **Auth Migration:** Refactor the authentication flow to move OAuth handling from `next-auth` (Node.js dependent) to the FastAPI backend using `Authlib`, ensuring the React UI remains functional as a pure client-side application.
5.  **Multi-stage Docker Build:** Update the `Dockerfile` to:
    -   Stage 1: Build the Next.js frontend and generate the static export.
    -   Stage 2: Use a lightweight Python base image.
    -   Stage 3: Copy the static frontend assets and the Python backend into the final image.

## Non-Functional Requirements
-   **Cold Start Optimization:** The container must start as quickly as possible (target < 5 seconds for backend readiness).
-   **Minimal Image Size:** Use `python:3.12-slim` as the base image to minimize size.
-   **Security:** Ensure OAuth flows remain secure and tokens are handled correctly in the refactored architecture.
-   **Documentation:** All relevant documentation must be updated to reflect the new architecture, build process, and configuration options.

## Acceptance Criteria
-   Setting `UI_MODE=react` serves the Next.js frontend at the root URL.
-   Setting `UI_MODE=streamlit` starts the original Streamlit application.
-   The React UI successfully authenticates users via Google/GitHub without a Node.js runtime.
-   The container build process is fully automated within a single `Dockerfile`.
-   The final container image does not include Node.js or `node_modules`.
-   Documentation (`README.md`, `deployment/README.md`, `docs/design.md`, `docs/nextui_walkthrough.md`) is updated.

## Out of Scope
-   Adding new features to the React UI itself.
-   Migrating Streamlit-specific prototyping tools to React.
