# Container Architecture Walkthrough

This document details the containerization strategy for the Rickbot application, explaining how the different components are built, orchestrated, and run.

## Overview

The application is composed of three main services when running locally or in production:

1.  **Frontend (React/Next.js)**: The modern user interface.
2.  **Backend (FastAPI)**: The central agent API.
3.  **Streamlit UI (Legacy)**: The original prototype interface (optional).

We use **Docker** for containerization and **Docker Compose** for local orchestration.

## Dockerfiles

We utilize optimized Dockerfiles for each service to ensure minimal image sizes and secure execution.

### 1. Backend (`Dockerfile.api`)

This Dockerfile builds the Python FastAPI backend.

*   **Base Image**: `python:3.12-slim` for a small footprint.
*   **Multi-Stage Build**:
    *   **Builder Stage**: Installs dependencies using `uv` (an extremely fast Python package manager) into a virtual environment.
    *   **Final Stage**: Copies the virtual environment and only the necessary source code (`src/main.py`, `src/rickbot_agent/`, `src/rickbot_utils/`) from the builder.
*   **Whitelist Approach**: We explicitly copy only the required backend code, excluding the frontend source directories (`src/nextjs_fe`, `src/streamlit_fe`) to keep the image clean.
*   **Security**: Runs as a non-root user `app-user`.

### 2. Frontend (`src/nextjs_fe/Dockerfile`)

This Dockerfile builds the Next.js frontend application.

*   **Base Image**: `node:18-alpine`.
*   **Multi-Stage Build**:
    *   **Deps**: Installs dependencies (`npm ci`).
    *   **Builder**: Builds the Next.js application (`npm run build`). It accepts `NEXT_PUBLIC_API_URL` as a build argument to bake in the API endpoint.
    *   **Runner**: A lightweight production image that runs the app.
*   **Standalone Output**: We use Next.js's `output: 'standalone'` feature (configured in `next.config.js`) to automatically trace and include only the necessary files for production, significantly reducing image size.
*   **Security**: Runs as a non-root user `nextjs`.

## Local Development (Docker Compose)

The `docker-compose.yml` file orchestrates these services for a seamless local development experience that mirrors our production architecture.

### Services

*   **`backend`**:
    *   Builds from `Dockerfile.api`.
    *   Exposes port `8080`.
    *   Mounts the local `src` directory for live reloading during development (though full rebuilds are safer for structural changes).
    *   Mounts Google Cloud credentials (ADC) to allow access to Vertex AI and Secret Manager.
    *   Sets `BACKEND_ALLOW_MOCK_AUTH=true` to enable local testing without real OAuth.

*   **`frontend`**:
    *   Builds from `src/nextjs_fe/Dockerfile`.
    *   Exposes port `3000`.
    *   **Critical Configuration**: Passes `NEXT_PUBLIC_API_URL: http://localhost:8080` as a build argument. This ensures the client-side React app knows where to find the API (which is mapped to localhost:8080 by Docker Compose).
    *   Configured for Mock Auth by default (`NEXT_PUBLIC_ALLOW_MOCK_AUTH=true`).

*   **`streamlit_fe`**:
    *   Legacy interface, also available for testing.
    *   Exposes port `8501`.

### Running the Environment

To start the full stack:

```bash
docker compose up -d --build backend frontend
```

*   **Frontend**: Access at [http://localhost:3000](http://localhost:3000)
*   **Backend API Docs**: Access at [http://localhost:8080/docs](http://localhost:8080/docs)

### Troubleshooting

*   **"Not Authenticated"**: Ensure you are logged in (Mock Login works locally).
*   **API Connection Failed**: Check if the backend container is running (`docker ps`) and accessible at `http://localhost:8080`. If the frontend cannot reach it, ensure `NEXT_PUBLIC_API_URL` was correctly set during the build (try rebuilding with `--build`).
*   **Permissions Errors**: If the backend logs show permission errors accessing Google Cloud resources (like Secret Manager), ensure your local Application Default Credentials are set up and that the `GOOGLE_CLOUD_PROJECT` environment variable in `.env` matches the project your credentials have access to.
